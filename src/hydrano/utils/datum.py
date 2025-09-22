from typing import Any

import cbor2
from pycardano import PlutusData


def parse_datum_cbor(datum_cbor: str) -> Any:
    """
    Desc: Parse a CBOR-encoded Plutus datum (hex string) into a Python object.
    Args: datum_cbor: A hex string representing a CBOR-encoded Plutus datum.
    Returns: A Python object (typically a dict) representing the parsed datum. 
    Raises: ValueError: If the hex string or CBOR data is invalid. cbor2.CBORError: If CBOR decoding fails.
    """
    try:
        cbor_bytes = bytes.fromhex(datum_cbor)
        plutus_data = PlutusData.from_cbor(cbor_bytes)
        datum = plutus_data.to_json()
        return datum
    except ValueError as e:
        raise ValueError(f"Invalid hex string: {e}")
    except cbor2.CBORError as e:
        raise ValueError(f"Invalid CBOR data: {e}")