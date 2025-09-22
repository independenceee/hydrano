from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class HydraTransaction:
    type: Literal["Tx ConwayEra", "Unwitnessed Tx ConwayEra", "Witnessed Tx ConwayEra"]
    description: str
    cborHex: str
    txId: Optional[str] = None
