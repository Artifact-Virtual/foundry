#!/usr/bin/env python3
"""
Minimal SMS/HTTP gateway example.
- Exposes /frames endpoint to POST frames (one per line in body)
- Decodes and broadcasts to chain (ETH by default)
"""
import os
from flask import Flask, request, jsonify
from web3 import Web3
from courier.foundry_courier import decode_frames

app = Flask(__name__)

ETH_RPC = os.environ.get("ETH_RPC","https://sepolia.infura.io/v3/YOUR_KEY")
w3 = Web3(Web3.HTTPProvider(ETH_RPC))

@app.post("/frames")
def frames():
    body = request.get_data(as_text=True)
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    raw = decode_frames(lines)
    if not raw:
        return jsonify({"status":"error","msg":"decode_failed_or_incomplete"}), 400
    tx_hash = w3.eth.send_raw_transaction(raw)
    return jsonify({"status":"ok","tx": tx_hash.hex()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8080")))
