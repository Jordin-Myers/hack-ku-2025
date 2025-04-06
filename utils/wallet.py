from types import SimpleNamespace
import requests
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import autofill_and_sign, reliable_submission
from xrpl.utils import xrp_to_drops
from xrpl.account import get_balance
from xrpl.models.requests import AccountInfo

client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def get_live_balance(address):
    try:
        if not address:
            return "Unavailable"
        
        req = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True
        )
        response = client.request(req)
        balance_drops = int(response.result["account_data"]["Balance"])
        balance_xrp = balance_drops / 1_000_000
        return f"{balance_xrp:.6f} XRP"
    except Exception as e:
        print(f"[get_live_balance] Error for {address}: {e}")
        return "Unavailable"

def create_wallet():
    try:
        response = requests.post("https://faucet.altnet.rippletest.net/accounts", timeout=10)
        data = response.json()

        if "account" not in data or "seed" not in data:
            return SimpleNamespace(error="Faucet response missing address or secret.")

        return SimpleNamespace(
            address=data["account"]["classicAddress"],
            seed=data["seed"],
            balance=f"{data['amount']} XRP (testnet)"
        )
    except Exception as e:
        return SimpleNamespace(error=f"Faucet error: {str(e)}")

def send_test_transactions(seed):
    try:
        wallet = Wallet.from_seed(seed)

        # Dust transaction to valid but suspicious-looking address
        dust_tx = Payment(
            account=wallet.classic_address,
            amount=xrp_to_drops(0.00001),
            destination="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
        )

        # Large transaction to known XRPL test account
        big_tx = Payment(
            account=wallet.classic_address,
            amount=xrp_to_drops(1000),
            destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"
        )

        for tx in [dust_tx, big_tx]:
            print("⚙️ Sending transaction:", tx.to_dict())  # ✅ Not .to_xrpl()
            signed = autofill_and_sign(tx, client, wallet)
            response = reliable_submission(signed, client)
            print("✅ Submitted transaction result:", response.result)

        return True

    except Exception as e:
        print("Transaction error:", e)
        return False