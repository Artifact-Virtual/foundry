
# Foundry Courier Toolkit

> Darknet Continuum

![Cross-Platform](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20Mac%20%7C%20Android%20%7C%20TUI-informational)
![No Internet Required](https://img.shields.io/badge/Offline-Ready-success)
![Battle Hardened](https://img.shields.io/badge/Battle--Hardened-Yes-critical)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## Purpose

**Move signed blockchain transactions over radio, mesh, SMS, sneakernet, or any data carrier.**

This toolkit is designed for extreme resilience: when the internet fails, you can still move value. All tools are text-based, portable, and run on minimal hardware (USB, microSD, old phones, smartwatches with terminal access, etc.).

---

## Features

- Encode/decode signed transactions with CRC32 and optional parity (error correction)
- Broadcast raw transactions to Bitcoin and Ethereum networks
- Minimal HTTP/SMS gateway for rebroadcasting
- Text-based CLI and TUI (menu interface) for universal access
- Portable: runs from USB, microSD, or any device with Python and a terminal
- Offline documentation (`commands.lib`)

---

## Project Structure

- `courier/foundry_courier.py` – Core encode/decode logic
- `courier_cli.py` – Main CLI tool (battle-hardened, menu-driven)
- `tools/push_eth.py` – Broadcast raw Ethereum tx
- `tools/push_btc.py` – Broadcast raw Bitcoin tx
- `gateways/sms_gateway.py` – Minimal HTTP/SMS gateway
- `examples/` – Test vectors and demo files
- `commands.lib` – All CLI commands and usage, always up to date
- `requirements.txt` – Minimal dependencies

---

## Install & Run

```bash
# 1. Set up Python (3.11+ recommended)
python -m venv .venv && .venv\Scripts\activate   # Windows
# or
python3 -m venv .venv && source .venv/bin/activate # Linux/Mac
pip install -r requirements.txt

# 2. Run the CLI (menu or direct command)
python courier_cli.py help
python courier_cli.py list-services
```

---


## Usage Examples

### Encode a signed transaction

```bash
$ export SVNEVM_HMAC=change_me_strong_key   # or pass --allow-insecure-default-key for lab only
python courier_cli.py encode-tx --hex <SIGNED_TX_HEX> --output frames.txt
```

### Decode frames

```bash
python courier_cli.py decode-frames --input frames.txt --output recovered.hex
```

### Broadcast to Ethereum

```bash
python courier_cli.py push-eth --hex <SIGNED_TX_HEX> --rpc-url <ETH_RPC_URL>
```

### Broadcast to Bitcoin

```bash
python courier_cli.py push-btc --hex <SIGNED_TX_HEX> --rpc-url <BTC_RPC_URL> --user <USER> --password <PWD>
```

---

## End-to-End Testing

This project includes a full end-to-end test suite to ensure all core functionality works as expected.

### Run all tests

```bash
python test_end_to_end.py
```

Test results and a summary report will be written to `report.md` in the project root after running the tests.

---

## Battle-Hardened Philosophy

- **Text-based first:** Works on any OS, terminal, or device (including Termux, smartwatches, old phones)
- **Portable Python:** Bundle on USB/microSD, run anywhere with Python or as a standalone executable
- **Minimal dependencies:** No heavy libraries, easy to audit and maintain
- **Offline docs:** All commands in `commands.lib` for field reference
- **Universal UI:** TUI/CLI for maximum compatibility; QR/barcode support possible for smart devices
- **No private keys ever:** Always sign offline, only move signed payloads
- **Legal & safe:** Respect radio laws, never transmit keys, repeat for reliability

---

## License

MIT
