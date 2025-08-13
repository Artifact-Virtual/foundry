#!/usr/bin/env python3
import sys, os, json, requests

def main():
    if len(sys.argv) < 2:
        print("Usage: push_btc.py <raw_tx_hex> [RPC_URL] [RPC_USER] [RPC_PASS]\nEnv: BTC_RPC, BTC_USER, BTC_PASS")
        sys.exit(1)
    raw_hex = sys.argv[1].lower()
    rpc = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("BTC_RPC","http://127.0.0.1:8332")
    user = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("BTC_USER","user")
    pwd  = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("BTC_PASS","pass")
    payload = {"jsonrpc":"1.0","id":"fc","method":"sendrawtransaction","params":[raw_hex]}
    r = requests.post(rpc, auth=(user,pwd), data=json.dumps(payload))
    r.raise_for_status()
    print(r.json()["result"])

if __name__ == "__main__":
    main()
