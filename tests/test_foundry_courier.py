"""
Unit and property tests for courier.foundry_courier
"""
from courier.foundry_courier import encode_frames, decode_frames
import random
 

def random_hex(length: int) -> str:
    chars = '0123456789abcdef'
    return ''.join(random.choice(chars) for _ in range(length))


def test_encode_decode_identity():
    tx_hex = random_hex(128)
    frames = encode_frames(tx_hex, hmac_key=b"test_hmac_key")
    recovered = decode_frames(frames, hmac_key=b"test_hmac_key")
    assert recovered.hex() == tx_hex


def test_encode_decode_no_parity():
    tx_hex = random_hex(256)
    frames = encode_frames(
        tx_hex, add_parity=False, hmac_key=b"test_hmac_key"
    )
    recovered = decode_frames(frames, hmac_key=b"test_hmac_key")
    assert recovered.hex() == tx_hex


def test_encode_decode_with_loss_and_parity():
    tx_hex = random_hex(128)
    frames = encode_frames(
        tx_hex, group_size=4, add_parity=True, hmac_key=b"test_hmac_key"
    )
    # Remove one data frame from a group
    group = [f for f in frames if f.startswith('F:')][:4]
    parity = [f for f in frames if f.startswith('P:')][0]
    frames_lost = group[:1] + group[2:] + [parity]
    # Add all other frames
    frames_lost += frames[5:]
    recovered = decode_frames(frames_lost, hmac_key=b"test_hmac_key")
    assert recovered.hex() == tx_hex[:len(recovered.hex())]


def test_empty_input():
    assert decode_frames([], hmac_key=b"test_hmac_key") == b''
    assert decode_frames([''], hmac_key=b"test_hmac_key") == b''


def test_invalid_frame():
    # Corrupt CRC
    tx_hex = random_hex(64)
    frames = encode_frames(tx_hex, hmac_key=b"test_hmac_key")
    bad = frames[:]
    bad[0] = bad[0].replace(':', ':deadbeef:', 1)
    # With parity present, the corrupted frame should be ignored and
    # the original payload recovered via XOR parity.
    assert decode_frames(
        bad, hmac_key=b"test_hmac_key"
    ) == bytes.fromhex(tx_hex)
