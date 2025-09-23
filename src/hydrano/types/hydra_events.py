from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from hydrano.types.hydra_post_chain import PostChainTx
from hydrano.types.hydra_transaction import HydraTransaction
from hydrano.types.hydra_type import HydraParty, HydraSnapshot
from hydrano.types.hydra_utxos import HydraUTxOs


@dataclass
class Greetings:
    tag: str
    me: Dict[str, str]
    headStatus: str
    hydraHeadId: str
    snapshotUtxo: HydraUTxOs
    timestamp: str
    hydraNodeVersion: str


@dataclass
class PeerConnected:
    tag: str
    peer: str
    seq: int
    timestamp: str


@dataclass
class PeerDisconnected:
    tag: str
    peer: str
    seq: int
    timestamp: str


@dataclass
class PeerHandshakeFailure:
    tag: str
    remoteHost: Dict[str, str]   # {"tag": "IPv4", "ipv4": "..."}
    ourVersion: int
    theirVersions: List[int]
    seq: int
    timestamp: str


@dataclass
class HeadIsInitializing:
    tag: str
    headId: str
    parties: List[HydraParty]
    seq: int
    timestamp: str


@dataclass
class Committed:
    tag: str
    parties: List[HydraParty]
    utxo: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class HeadIsOpen:
    tag: str
    headId: str
    utxo: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class HeadIsClosed:
    tag: str
    headId: str
    snapshotNumber: int
    contestationDeadline: str
    seq: int
    timestamp: str


@dataclass
class HeadIsContested:
    tag: str
    headId: str
    snapshotNumber: int
    contestationDeadline: str
    seq: int
    timestamp: str


@dataclass
class ReadyToFanout:
    tag: str
    headId: str
    seq: int
    timestamp: str


@dataclass
class HeadIsAborted:
    tag: str
    headId: str
    utxo: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class HeadIsFinalized:
    tag: str
    headId: str
    utxo: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class TxValid:
    tag: str
    headId: str
    seq: int
    timestamp: str
    transaction: HydraTransaction


@dataclass
class TxInvalid:
    tag: str
    headId: str
    utxo: HydraUTxOs
    transaction: HydraTransaction
    validationError: Dict[str, str]
    seq: int
    timestamp: str


@dataclass
class SnapshotConfirmed:
    tag: str
    headId: str
    snapshot: HydraSnapshot
    seq: int
    timestamp: str


@dataclass
class GetUTxOResponse:
    tag: str
    headId: str
    utxo: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class InvalidInput:
    tag: str
    reason: str
    input: str
    seq: int
    timestamp: str


@dataclass
class PostTxOnChainFailed:
    tag: str
    postChainTx: PostChainTx
    postTxError: object
    seq: int
    timestamp: str


# CommandFailed cần định nghĩa HydraCommand trước
@dataclass
class HydraCommandAbort:
    tag: str = "Abort"

@dataclass
class HydraCommandNewTx:
    tag: str = "NewTx"
    transaction: HydraTransaction = None

@dataclass
class HydraCommandGetUTxO:
    tag: str = "GetUTxO"

@dataclass
class HydraCommandDecommit:
    tag: str = "Decommit"
    decommitTx: HydraTransaction = None

@dataclass
class HydraCommandClose:
    tag: str = "Close"

@dataclass
class HydraCommandContest:
    tag: str = "Contest"

@dataclass
class HydraCommandFanout:
    tag: str = "Fanout"


HydraCommand = Union[
    HydraCommandAbort,
    HydraCommandNewTx,
    HydraCommandGetUTxO,
    HydraCommandDecommit,
    HydraCommandClose,
    HydraCommandContest,
    HydraCommandFanout,
]


@dataclass
class CommandFailed:
    tag: str
    clientInput: HydraCommand
    seq: int
    timestamp: str


@dataclass
class IgnoredHeadInitializing:
    tag: str
    headId: str
    contestationPeriod: int
    parties: List[HydraParty]
    participants: List[str]
    seq: int
    timestamp: str


@dataclass
class DecommitInvalid:
    tag: str
    headId: str
    decommitTx: HydraTransaction
    decommitInvalidReason: Dict[str, object]
    seq: int
    timestamp: str


@dataclass
class DecommitRequested:
    tag: str
    headId: str
    decommitTx: HydraTransaction
    utxoToDecommit: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class DecommitApproved:
    tag: str
    headId: str
    decommitTxId: str
    utxoToDecommit: HydraUTxOs
    seq: int
    timestamp: str


@dataclass
class DecommitFinalized:
    tag: str
    headId: str
    decommitTxId: str
    seq: int
    timestamp: str


HydraEvent = Union[
    Greetings,
    PeerConnected,
    PeerDisconnected,
    PeerHandshakeFailure,
    HeadIsInitializing,
    Committed,
    HeadIsOpen,
    HeadIsClosed,
    HeadIsContested,
    ReadyToFanout,
    HeadIsAborted,
    HeadIsFinalized,
    TxValid,
    TxInvalid,
    SnapshotConfirmed,
    GetUTxOResponse,
    InvalidInput,
    PostTxOnChainFailed,
    CommandFailed,
    IgnoredHeadInitializing,
    DecommitInvalid,
    DecommitRequested,
    DecommitApproved,
    DecommitFinalized,
]
