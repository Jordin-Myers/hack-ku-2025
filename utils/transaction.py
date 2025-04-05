import requests

def get_recent_transactions(address: str) -> list:
    # Dummy demo data - replace with actual XRPL API call if needed
    if not address.startswith("r"):
        raise ValueError("Invalid XRPL address")
    # Simulate data
    return [
        f"Tx to rExample...123 - 20 XRP",
        f"Tx from rAnother...456 - 5 XRP",
    ]