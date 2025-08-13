#!/usr/bin/env python3
"""
Foundry Courier
Carrier-agnostic encoder/decoder for signed blockchain transactions.

Features
- CRC32 per data frame
- Base64 text-safe payloads
- XOR parity frames (recover 1 missing data frame per group)
- Metadata in parity headers to identify group range
- Works with SMS, radio, mesh, or sneakernet
- CLI usage; importable as a library

Usage
  Encode:  python -m courier.foundry_courier encode examples/signed_tx.hex -o frames.txt
  Decode:  python -m courier.foundry_courier decode frames.txt -o recovered.hex
"""
import argparse
import base64
import itertools
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple

def chunk_bytes(b: bytes, size: int):
    for i in range(0, len(b), size):
        yield b[i:i+size]

def _xor_pad(a: bytes, b: bytes, size: int) -> bytes:
    a2 = a.ljust(size, b'\x00')
    b2 = b.ljust(size, b'\x00')
    return bytes(x ^ y for x, y in zip(a2, b2))

@dataclass
class DataFrame:
    seq: int
    size: int
    crc: int
    payload: bytes

@dataclass
class ParityFrame:
    gidx: int
    start_seq: int
    end_seq: int
    size: int
    crc: int
    parity: bytes

def encode_frames(tx_hex: str, frame_payload_bytes: int = 64, group_size: int = 8, add_parity: bool = True) -> List[str]:
    """
    tx_hex: signed raw transaction hex string (no 0x)
    frame_payload_bytes: payload size before base64 (keep <= 64 for SMS/radio comfort)
    group_size: number of frames per parity group
    add_parity: append 1 parity frame per group using XOR across group frames
    returns: list[str] frames:
       Data:  F:<seq>:<size>:<crc>:<base64payload>
       Parity: P:<gidx>:<start_seq>:<end_seq>:<size>:<crc>:<base64parity>
    """
    raw = bytes.fromhex(tx_hex)
    frames, group_parts, idx = [], [], 0
    gidx = 1

    for part in chunk_bytes(raw, frame_payload_bytes):
        crc = zlib.crc32(part) & 0xffffffff
        header = f"F:{idx:06d}:{len(part):03d}:{crc:08x}:"
        body = base64.b64encode(part).decode("ascii")
        frames.append(header + body)
        group_parts.append((idx, part))
        idx += 1

        if add_parity and (idx % group_size == 0):
            start_seq = group_parts[0][0]
            end_seq = group_parts[-1][0]
            size = max(len(p) for _, p in group_parts)
            parity = bytes(size)
            for _, p in group_parts:
                parity = _xor_pad(parity, p, size)
            crc_p = zlib.crc32(parity) & 0xffffffff
            header_p = f"P:{gidx:06d}:{start_seq:06d}:{end_seq:06d}:{size:03d}:{crc_p:08x}:"
            frames.append(header_p + base64.b64encode(parity).decode("ascii"))
            group_parts.clear()
            gidx += 1

    if add_parity and group_parts:
        start_seq = group_parts[0][0]
        end_seq = group_parts[-1][0]
        size = max(len(p) for _, p in group_parts)
        parity = bytes(size)
        for _, p in group_parts:
            parity = _xor_pad(parity, p, size)
        crc_p = zlib.crc32(parity) & 0xffffffff
        header_p = f"P:{gidx:06d}:{start_seq:06d}:{end_seq:06d}:{size:03d}:{crc_p:08x}:"
        frames.append(header_p + base64.b64encode(parity).decode("ascii"))

    return frames

def parse_frame(line: str):
    # Returns Union[DataFrame, ParityFrame, None]
    if not line.strip():
        return None
    try:
        kind, rest = line.split(":", 1)
    except ValueError:
        return None

    if kind == "F":
        try:
            seq_s, size_s, crc_hex, b64 = rest.split(":", 3)
            seq, size, crc = int(seq_s), int(size_s), int(crc_hex, 16)
            part = base64.b64decode(b64.encode("ascii"))
            if (zlib.crc32(part) & 0xffffffff) != crc or len(part) != size:
                return None
            return DataFrame(seq=seq, size=size, crc=crc, payload=part)
        except Exception:
            return None
    elif kind == "P":
        try:
            gidx_s, start_s, end_s, size_s, crc_hex, b64 = rest.split(":", 5)
            gidx = int(gidx_s); start_seq = int(start_s); end_seq = int(end_s)
            size = int(size_s); crc = int(crc_hex, 16)
            parity = base64.b64decode(b64.encode("ascii"))
            if (zlib.crc32(parity) & 0xffffffff) != crc or len(parity) != size:
                return None
            return ParityFrame(gidx=gidx, start_seq=start_seq, end_seq=end_seq, size=size, crc=crc, parity=parity)
        except Exception:
            return None
    else:
        return None

def recover_with_parity(parts: Dict[int, bytes], parity: ParityFrame) -> None:
    """If exactly one frame missing in the parity range, reconstruct it via XOR and insert."""
    start, end = parity.start_seq, parity.end_seq
    missing = [s for s in range(start, end+1) if s not in parts]
    if len(missing) != 1:
        return
    miss = missing[0]
    acc = bytes(parity.size)  # start zero
    for s in range(start, end+1):
        if s == miss:
            continue
        part = parts.get(s, b"")
        acc = _xor_pad(acc, part, parity.size)
    recovered = _xor_pad(parity.parity, acc, parity.size)
    # We cannot verify the original CRC (unknown), but length is bounded
    parts[miss] = recovered[:parity.size]

def decode_frames(lines: List[str]) -> bytes:
    data_parts: Dict[int, bytes] = {}
    parities: List[ParityFrame] = []

    for line in lines:
        fr = parse_frame(line)
        if fr is None:
            continue
        if isinstance(fr, DataFrame):
            data_parts[fr.seq] = fr.payload
        else:
            parities.append(fr)

    # Attempt parity-based single-loss recovery
    for p in parities:
        recover_with_parity(data_parts, p)

    if not data_parts:
        return b""
    # Build contiguous from min to max available
    seqs = sorted(data_parts.keys())
    result = []
    for s in range(seqs[0], seqs[-1] + 1):
        if s in data_parts:
            result.append(data_parts[s])
        else:
            break  # stop at first gap
    return b"".join(result)

def cli():
    ap = argparse.ArgumentParser(description="Foundry Courier – frame/deframe signed transactions for offline carriers (SMS/radio/mesh/USB).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("encode", help="Encode signed transaction hex into frames.")
    enc.add_argument("input", help="Path to file containing hex (no 0x).")
    enc.add_argument("-o", "--output", help="Write frames to file (default stdout).")
    enc.add_argument("--size", type=int, default=64, help="Payload bytes per frame before base64 (default 64).")
    enc.add_argument("--group", type=int, default=8, help="Frames per parity group (default 8).")
    enc.add_argument("--no-parity", action="store_true", help="Disable parity frames.")

    dec = sub.add_parser("decode", help="Decode frames back into raw signed transaction bytes.")
    dec.add_argument("input", help="Path to file with frames (one per line).")
    dec.add_argument("-o", "--output", help="Write raw tx hex to file (default stdout).")

    args = ap.parse_args()

    if args.cmd == "encode":
        tx_hex = Path(args.input).read_text().strip().lower().replace("0x","")
        frames = encode_frames(tx_hex, frame_payload_bytes=args.size, group_size=args.group, add_parity=(not args.no_parity))
        out = "\n".join(frames)
        if args.output:
            Path(args.output).write_text(out)
        else:
            print(out)

    elif args.cmd == "decode":
        lines = Path(args.input).read_text().splitlines()
        raw = decode_frames(lines)
        raw_hex = raw.hex()
        if args.output:
            Path(args.output).write_text(raw_hex)
        else:
            print(raw_hex)

if __name__ == "__main__":
    cli()
