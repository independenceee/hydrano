from enum import Enum
from typing import Any, Dict, Optional


class HydraStatus(Enum):

    IDLE = "IDLE"
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    INITIALIZING = "INITIALIZING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    FANOUT_POSSIBLE = "FANOUT_POSSIBLE"
    FINAL = "FINAL"


def hydra_status(value: dict[str, Optional[str]]) -> Optional[HydraStatus]:
    if value.get("headStatus") == "Open":
        return HydraStatus.OPEN

    tag = value.get("tag")
    match tag:
        case "HeadIsInitializing":
            return HydraStatus.INITIALIZING
        case "HeadIsOpen":
            return HydraStatus.OPEN
        case "HeadIsClosed":
            return HydraStatus.CLOSED
        case "ReadyToFanout":
            return HydraStatus.FANOUT_POSSIBLE
        case "HeadIsFinalized":
            return HydraStatus.FINAL
        case _:
            return None
