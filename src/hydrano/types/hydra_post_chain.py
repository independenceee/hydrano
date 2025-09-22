from dataclasses import dataclass
from typing import Dict, List, Union

from hydrano.types.hydra_type import HydraHeadParameters, HydraSnapshot
from hydrano.types.hydra_utxos import HydraUTxO

@dataclass
class InitTx:
    tag: str = "InitTx"
    participants: List[str]
    head_parameters: HydraHeadParameters

@dataclass
class AbortTx:
    tag: str = "AbortTx"
    utxo: Dict[str, HydraUTxO]
    head_seed: str

@dataclass
class CollectComTx:
    tag: str = "CollectComTx"
    utxo: Dict[str, HydraUTxO]
    head_id: str
    head_parameters: HydraHeadParameters

@dataclass
class InitialSnapshot:
    tag: str = "InitialSnapshot"
    head_id: str
    initial_utxo: Dict[str, HydraUTxO]

@dataclass
class ConfirmedSnapshot:
    tag: str = "ConfirmedSnapshot"
    snapshot: HydraSnapshot
    signatures: Dict[str, List[str]]  # mutliSignature được biểu diễn dưới dạng List[str]

@dataclass
class DecrementTx:
    tag: str = "DecrementTx"
    head_id: str
    head_parameters: HydraHeadParameters
    decrementing_snapshot: Union[InitialSnapshot, ConfirmedSnapshot]

@dataclass
class CloseTx:
    tag: str = "CloseTx"
    head_id: str
    head_parameters: HydraHeadParameters
    closing_snapshot: Union[InitialSnapshot, ConfirmedSnapshot]
    open_version: int

@dataclass
class ContestTx:
    tag: str = "ContestTx"
    head_id: str
    head_parameters: HydraHeadParameters
    contesting_snapshot: Union[InitialSnapshot, ConfirmedSnapshot]
    open_version: int

@dataclass
class FanoutTx:
    tag: str = "FanoutTx"
    utxo: Dict[str, HydraUTxO]
    utxo_to_decommit: Dict[str, HydraUTxO]
    head_seed: str
    contestation_deadline: str

# Định nghĩa PostChainTx như một Union type
PostChainTx = Union[
    InitTx,
    AbortTx,
    CollectComTx,
    DecrementTx,
    CloseTx,
    ContestTx,
    FanoutTx
]