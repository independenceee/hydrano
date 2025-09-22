from dataclasses import dataclass
from typing import List

from hydrano.types.hydra_utxos import HydraUTxOs


@dataclass
class HydraCommitTransaction:
    cborHex: str
    description: str
    txId: str
    type: str

@dataclass
class HydraParty:
    vkey: str

@dataclass
class HydraHeadParameters:
    contestationPeriod: int
    parties: List[HydraParty]

@dataclass
class HydraSnapshot:
    headId: str
    snapshotNumber: str
    utxo: HydraUTxOs
    confirmedTransactions: List[str]
    utxoToDecommit: HydraUTxOs
    version: int