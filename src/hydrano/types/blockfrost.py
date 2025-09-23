from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BlockfrostAmount:
    unit: str
    quantity: str  

@dataclass
class BlockfrostOutput:
    address: str
    amount: List[BlockfrostAmount]
    output_index: int
    data_hash: Optional[str] = None
    inline_datum: Optional[str] = None
    collateral: bool = False
    reference_script_hash: Optional[str] = None
    consumed_by_tx: Optional[str] = None

@dataclass
class BlockfrostInput:
    address: str
    amount: List[BlockfrostAmount]
    tx_hash: str
    output_index: int
    data_hash: Optional[str] = None
    inline_datum: Optional[str] = None
    reference_script_hash: Optional[str] = None
    collateral: bool = False
    reference: bool = False

@dataclass
class BlockfrostTransaction:
    hash: str
    inputs: List[BlockfrostInput]
    outputs: List[BlockfrostOutput]
