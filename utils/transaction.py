from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx

client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def get_recent_transactions(address: str):
    try:
        tx_request = AccountTx(
            account=address,
            ledger_index_min=-1,
            ledger_index_max=-1,
            binary=False,
            limit=10
        )
        response = client.request(tx_request)
        print("FULL XRPL RESPONSE:", response.result)  # Debug
        transactions = response.result.get("transactions", [])
        results = []

        for tx_entry in transactions:
            tx_data = tx_entry.get("tx_json", {})  # ✅ Correct field

            tx_type = tx_data.get("TransactionType")
            destination = tx_data.get("Destination")
            amount = tx_data.get("DeliverMax") or tx_data.get("Amount")

            if tx_type != "Payment" or not amount:
                continue

            # Convert to XRP if numeric
            try:
                amount_value = int(amount) / 1_000_000
            except:
                amount_value = 0

            suspicious = []
            if amount_value > 500:
                suspicious.append("⚠️ Large Transfer")
            if amount_value < 0.01:
                suspicious.append("⚠️ Microtransaction (Possible Dusting Attack)")
            if destination and not destination.startswith("r"):
                suspicious.append("⚠️ Suspicious Destination Format")
            if not suspicious:
                suspicious.append("✅ No suspicious activity found")

            results.append({
                "type": tx_type,
                "amount": amount_value,
                "destination": destination or "N/A",
                "suspicious": suspicious
            })

        return results

    except Exception as e:
        return [{
            "type": "Error",
            "amount": "N/A",
            "destination": "N/A",
            "suspicious": [f"Error: {str(e)}"]
        }]
