"""
End-to-end test suite for Foundry Courier
Covers encode, decode, and CLI integration.
"""
import subprocess
import tempfile
from pathlib import Path
import os

def run_cli(args, input_data=None):
    cmd = ["python", "courier_cli.py"] + args
    result = subprocess.run(cmd, input=input_data, capture_output=True, text=True)
    return result

def test_encode_decode_cycle():
    # Use a sample signed tx hex (dummy data)
    tx_hex = "deadbeef" * 32  # 128 bytes
    with tempfile.TemporaryDirectory() as tmpdir:
        frames_path = Path(tmpdir) / "frames.txt"
        recovered_path = Path(tmpdir) / "recovered.hex"
        # Encode
        res1 = run_cli(["encode-tx", "--hex", tx_hex, "--output", str(frames_path)])
        assert res1.returncode == 0, f"Encode failed: {res1.stderr}"
        # Decode
        res2 = run_cli(["decode-frames", "--input", str(frames_path), "--output", str(recovered_path)])
        assert res2.returncode == 0, f"Decode failed: {res2.stderr}"
        # Check output
        recovered = recovered_path.read_text().strip()
        assert recovered == tx_hex, f"Recovered tx does not match original. Got: {recovered}"
    print("[PASS] Encode/decode cycle")

def test_cli_help():
    res = run_cli(["help"])
    assert res.returncode == 0
    assert "Available services" in res.stdout or "usage" in res.stdout.lower()
    print("[PASS] CLI help")

def run_all():
    test_encode_decode_cycle()
    test_cli_help()
    print("All end-to-end tests passed.")

if __name__ == "__main__":
    run_all()
