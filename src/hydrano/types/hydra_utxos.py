from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pycardano import PlutusData, TransactionInput, TransactionOutput, UTxO, datum_hash

from hydrano.types.hydra_assets import HydraAssets, hydra_assets, to_assets
from hydrano.types.hydra_reference_script import (
    HydraReferenceScript,
    hydra_reference_script,
)
from hydrano.utils.datum import parse_datum_cbor


@dataclass
class HydraUTxO:
    address: str
    value: HydraAssets
    datum: Optional[str] = None,
    datum_hash: Optional[str] = None,
    inline_datum: Optional[Any] = None,
    inline_datum_raw: Optional[str] = None,
    inline_datum_hash: Optional[str]= None,
    reference_script: Optional[HydraReferenceScript] = None

HydraUTxOs = Dict[str, HydraUTxO]


async def hydra_utxo(utxo: UTxO) -> HydraUTxO:
    """
    Desc: Convert a pycardano UTxO to a hydraUTxO object.
    Args: utxo: A pycardano UTxO object.
    Returns: A HydraUTxO object with address, datum, and value.
    """
    inline_datum = None
    inline_datum_raw = None
    if utxo.output.datum and isinstance(utxo.output.datum, PlutusData):
        inline_datum_raw = utxo.output.datum.to_cbor_hex()
        inline_datum = parse_datum_cbor(inline_datum_raw)
    
    return HydraUTxO(
        address=utxo.output.address,
        datum=None,  
        datum_hash=None,  
        inline_datum=inline_datum,
        inline_datum_raw=inline_datum_raw,
        inline_datum_hash=str(utxo.output.datum_hash) if utxo.output.datum_hash else None,
        reference_script=await hydra_reference_script(str(utxo.output.script) if utxo.output.script else None),
        value=hydra_assets(utxo.output.value)
    )

async def hydra_utxos(utxos: List[UTxO]) -> HydraUTxOs:
    """
    Convert a list of pycardano UTxOs to a hydraUTxOs dictionary.
    Args: utxos: A list of pycardano UTxO objects.
    Returns: A dictionary mapping txRef (txHash#outputIndex) to hydraUTxO objects.
    """
    entries = []
    for utxo in utxos:
        tx_ref = f"{utxo.input.transaction_id}#{utxo.input.index}"
        hydra_utxo_obj = await hydra_utxo(utxo)
        entries.append((tx_ref, hydra_utxo_obj))
    
    return dict(entries)

def to_utxo(hydra_utxo: HydraUTxO, tx_id: str) -> UTxO:
    """
    Convert a hydraUTxO object back to a pycardano UTxO.
    Args: hydra_utxo: A HydraUTxO object. tx_id: A string in the format txHash#outputIndex.
    Returns: A pycardano UTxO object.
    Raises: ValueError: If tx_id format is invalid.
    """
    try:
        tx_hash, output_index = tx_id.split("#")
        output_index = int(output_index)
    except (ValueError, TypeError):
        raise ValueError("Invalid TxId Format")
    
    script_reference = hydra_utxo.reference_script.script["cborHex"] if hydra_utxo.reference_script else None

    return UTxO(
        input=TransactionInput(
            transaction_id=tx_hash,
            index=output_index
        ),
        output=TransactionOutput(
            address=hydra_utxo.address,
            amount=to_assets(hydra_utxo.value),
            datum_hash=hydra_utxo.inline_datum if hydra_utxo.inline_datum_hash else None,
            datum=hydra_utxo.inline_datum_raw,
            script=script_reference
        )
    )