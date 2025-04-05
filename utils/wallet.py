from xrpl.wallet import Wallet

def create_wallet():
    # Creates a testnet wallet using XRPL SDK
    wallet = Wallet.create()
    return wallet