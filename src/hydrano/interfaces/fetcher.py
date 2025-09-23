from abc import ABC, abstractmethod
from typing import List, Optional

from pycardano import UTxO


class IFetcher(ABC):
    """
    IFetcher is an abstract base class that defines the interface for fetching UTxOs.
    
    This allows different implementations (e.g., using Blockfrost, Koios, 
    a local node, or mock providers) while ensuring they share the same method signature.
    """
    @abstractmethod
    async def fetch_utxos(self, transaction_id: str, index: Optional[int] = None) -> List[UTxO]:
        """
        Description: Fetch UTxOs associated with a given transaction.

        Args:
        - transaction_id (str): The unique hash of the transaction from which UTxOs should be retrieved. This must be a valid Cardano transaction hash string.
        - index (Optional[int], default=None):
            - If None: fetch all UTxOs from the transaction.
            - If an integer: fetch only the UTxO at the specified output index.
                  This is useful when you know exactly which output you need.

        Returns:
        List[UTxO]:
        - A list of UTxO objects (from pycardano), representing unspent outputs of the given transaction. If `index` is provided and valid, the list will contain only one UTxO; if the index is invalid, it may return an empty list.

        Raises:
        Exception (implementation-specific):
        Implementations may raise exceptions if:
        - The transaction does not exist.
        - No UTxOs can be found.
        - The API or node connection fails.
        """
        pass