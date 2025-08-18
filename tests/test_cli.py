"""
Tests for the courier_cli.py command-line interface.
"""
import os
import subprocess
import tempfile
from pathlib import Path
import sys
from typing import List, Optional, Any

def run_cli(
    args: List[str],
    input_data: Optional[str] = None,
) -> subprocess.CompletedProcess[Any]:
    # Point to the actual CLI location in this repo
    cli_path = Path(__file__).resolve().parent.parent / "courier_cli.py"
    cmd: List[str] = [sys.executable, str(cli_path)] + args
    env = dict(os.environ)
    env.setdefault("SVNEVM_HMAC", "test_hmac_key")
    result: subprocess.CompletedProcess[Any] = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    return result


def test_help():
    res = run_cli(["help"])
    assert res.returncode == 0
    assert "Available services" in res.stdout or "usage" in res.stdout.lower()


def test_encode_decode_cycle():
    tx_hex = "deadbeef" * 32
    with tempfile.TemporaryDirectory() as tmpdir:
        frames_path = Path(tmpdir) / "frames.txt"
        recovered_path = Path(tmpdir) / "recovered.hex"
        res1 = run_cli([
            "encode-tx", "--hex", tx_hex, "--output", str(frames_path)
        ])
        assert res1.returncode == 0
        res2 = run_cli([
            "decode-frames", "--input", str(frames_path),
            "--output", str(recovered_path)
        ])
        assert res2.returncode == 0
        recovered = recovered_path.read_text().strip()
        assert recovered == tx_hex


def test_encode_stdout():
    tx_hex = "cafebabe" * 16
    res = run_cli(["encode-tx", "--hex", tx_hex])
    assert res.returncode == 0
    assert "F:000000" in res.stdout


def test_decode_stdin():
    tx_hex = "aabbccdd" * 16
    from courier.foundry_courier import encode_frames
    frames = encode_frames(tx_hex, hmac_key=b"test_hmac_key")
    input_data = "\n".join(frames)
    res = run_cli(["decode-frames"], input_data=input_data)
    assert res.returncode == 0
    assert tx_hex in res.stdout
