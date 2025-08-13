


"""
Courier CLI – State-of-the-art, battle-hardened command-line interface for Foundry Courier
Move signed blockchain transactions over any carrier, anywhere, anytime.
"""

import argparse
import sys
from pathlib import Path
from courier.foundry_courier import encode_frames, decode_frames
from tools import push_btc, push_eth

def list_services():

    """Print all available CLI services and routes."""
    print("Available services:")
    print("- encode-tx: Encode signed transaction into frames")
    print("- decode-frames: Decode frames into raw transaction")
    print("- push-btc: Broadcast Bitcoin transaction")
    print("- push-eth: Broadcast Ethereum transaction")
    print("- help: Show command documentation")

def encode_tx(args):

    """Encode a signed transaction hex string into frames and output to file or stdout."""
    try:
        tx_hex = args.hex.strip().lower().replace("0x", "")
        frames = encode_frames(
            tx_hex,
            frame_payload_bytes=args.frame_size,
            group_size=args.group_size,
            add_parity=not args.no_parity
        )
        if args.output:
            Path(args.output).write_text("\n".join(frames))
            print(f"[OK] Wrote {len(frames)} frames to {args.output}")
        else:
            print("\n".join(frames))
    except Exception as e:
        print(f"[ERROR] Failed to encode: {e}")

def decode_frames_cmd(args):

    """Decode frames from file or stdin and output raw transaction hex."""
    try:
        if args.input:
            lines = Path(args.input).read_text().splitlines()
        else:
            lines = [line.strip() for line in sys.stdin if line.strip()]
        raw = decode_frames(lines)
        raw_hex = raw.hex()
        if args.output:
            Path(args.output).write_text(raw_hex)
            print(f"[OK] Decoded raw tx written to {args.output}")
        else:
            print(raw_hex)
    except Exception as e:
        print(f"[ERROR] Failed to decode: {e}")

def push_btc_cmd(args):

    """Broadcast a raw Bitcoin transaction to the network."""
    try:
        result = push_btc.push_btc(
            args.hex,
            rpc_url=args.rpc_url,
            user=args.user,
            pwd=args.password
        )
        print(f"[OK] Bitcoin tx broadcasted. Result: {result}")
    except Exception as e:
        print(f"[ERROR] Failed to broadcast BTC tx: {e}")

def push_eth_cmd(args):

    """Broadcast a raw Ethereum transaction to the network."""
    try:
        raw_bytes = bytes.fromhex(args.hex.strip().lower().replace("0x", ""))
        result = push_eth.push_eth(raw_bytes, rpc_url=args.rpc_url)
        print(f"[OK] Ethereum tx broadcasted. Result: {result}")
    except Exception as e:
        print(f"[ERROR] Failed to broadcast ETH tx: {e}")

def main():
    parser = argparse.ArgumentParser(
        prog="courier-cli",
        description="Courier CLI: Move value without the net. Battle-hardened, portable, and universal."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-services", help="List all available services and routes.")

    enc = subparsers.add_parser("encode-tx", help="Encode a signed transaction into frames.")
    enc.add_argument("--hex", required=True, help="Signed transaction hex string.")
    enc.add_argument("--frame-size", type=int, default=64, help="Frame payload size in bytes.")
    enc.add_argument("--group-size", type=int, default=8, help="Frames per parity group.")
    enc.add_argument("--no-parity", action="store_true", help="Disable parity frame.")
    enc.add_argument("--output", help="Write frames to file (default: stdout)")

    dec = subparsers.add_parser("decode-frames", help="Decode frames into raw transaction bytes.")
    dec.add_argument("--input", help="Input file with frames (default: stdin).")
    dec.add_argument("--output", help="Write raw tx hex to file (default: stdout)")

    btc = subparsers.add_parser("push-btc", help="Broadcast a raw Bitcoin transaction.")
    btc.add_argument("--hex", required=True, help="Signed transaction hex string.")
    btc.add_argument("--rpc-url", default="http://127.0.0.1:8332", help="Bitcoin RPC URL.")
    btc.add_argument("--user", default="rpcuser", help="RPC username.")
    btc.add_argument("--password", default="rpcpass", help="RPC password.")

    eth = subparsers.add_parser("push-eth", help="Broadcast a raw Ethereum transaction.")
    eth.add_argument("--hex", required=True, help="Signed transaction hex string.")
    eth.add_argument("--rpc-url", default="https://sepolia.infura.io/v3/YOUR_PROJECT_ID", help="Ethereum RPC URL.")

    subparsers.add_parser("help", help="Show help and usage for all commands.")

    args = parser.parse_args()

    if args.command == "list-services":
        list_services()
    elif args.command == "encode-tx":
        encode_tx(args)
    elif args.command == "decode-frames":
        decode_frames_cmd(args)
    elif args.command == "push-btc":
        push_btc_cmd(args)
    elif args.command == "push-eth":
        push_eth_cmd(args)
    elif args.command == "help" or args.command is None:
        parser.print_help()
    else:
        print("Unknown command. Use 'help' for usage.")
        sys.exit(1)

if __name__ == "__main__":
    main()


