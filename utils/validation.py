import re

XRPL_ADDRESS_REGEX = re.compile(r'^r[1-9A-HJ-NP-Za-km-z]{25,35}$')

def is_valid_xrpl_address(address):
    """
    Validates an XRPL classic address format:
    - Must start with 'r'
    - 26–36 characters total (r + 25–35 chars)
    - Uses XRPL Base58 alphabet (no 0, O, I, l)
    """
    if not isinstance(address, str):
        return False
    return bool(XRPL_ADDRESS_REGEX.fullmatch(address))
