#!/usr/bin/env python3
import sys, os
from web3 import Web3

def main():
    if len(sys.argv) < 2:
        print("Usage: push_eth.py <raw_tx_hex> [RPC_URL]\nEnv: ETH_RPC")
        sys.exit(1)
    raw_hex = sys.argv[1].lower().replace("0x","")
    rpc = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("ETH_RPC","https://sepolia.infura.io/v3/YOUR_KEY")
    w3 = Web3(Web3.HTTPProvider(rpc))
    raw = bytes.fromhex(raw_hex)
    tx_hash = w3.eth.send_raw_transaction(raw)
    print(tx_hash.hex())

if __name__ == "__main__":
    main()
