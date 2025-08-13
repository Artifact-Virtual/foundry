"""
Unit and property tests for courier.foundry_courier
"""
import pytest
from courier.foundry_courier import encode_frames, decode_frames
import random

def random_hex(length):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))

def test_encode_decode_identity():
    tx_hex = random_hex(128)
    frames = encode_frames(tx_hex)
    recovered = decode_frames(frames)
    assert recovered.hex() == tx_hex

def test_encode_decode_no_parity():
    tx_hex = random_hex(256)
    frames = encode_frames(tx_hex, add_parity=False)
    recovered = decode_frames(frames)
    assert recovered.hex() == tx_hex

def test_encode_decode_with_loss_and_parity():
    tx_hex = random_hex(128)
    frames = encode_frames(tx_hex, group_size=4, add_parity=True)
    # Remove one data frame from a group
    group = [f for f in frames if f.startswith('F:')][:4]
    parity = [f for f in frames if f.startswith('P:')][0]
    frames_lost = group[:1] + group[2:] + [parity]
    # Add all other frames
    frames_lost += frames[5:]
    recovered = decode_frames(frames_lost)
    assert recovered.hex() == tx_hex[:len(recovered.hex())]

def test_empty_input():
    assert decode_frames([]) == b''
    assert decode_frames(['']) == b''

def test_invalid_frame():
    # Corrupt CRC
    tx_hex = random_hex(64)
    frames = encode_frames(tx_hex)
    bad = frames[:]
    bad[0] = bad[0].replace(':', ':deadbeef:', 1)
    assert decode_frames(bad) != bytes.fromhex(tx_hex)
