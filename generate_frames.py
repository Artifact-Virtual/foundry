
from courier.foundry_courier import encode_frames
from pathlib import Path
tx_hex = Path("examples/signed_tx.hex").read_text().strip()
frames = encode_frames(tx_hex, frame_payload_bytes=64, group_size=8, add_parity=True)
Path("examples/frames.txt").write_text("\n".join(frames))
print("generated examples/frames.txt with", len(frames), "frames")
