import asyncio
import time
from typing import Any, Callable, Dict, List, Optional

import requests
from pycardano import ChainContext, UTxO
from pyee.asyncio import AsyncIOEventEmitter

from hydrano.hydra_connection import HydraConnection
from hydrano.types.hydra_status import HydraStatus
from hydrano.types.hydra_transaction import HydraTransaction
from hydrano.types.hydra_utxos import HydraUTxO, to_utxo
from hydrano.utils.parse_error import parse_error


class HydraProvider(ChainContext):
    """
    Description: 
    - A provider for interacting with Hydra Heads, a layer-2 scaling solution for Cardano.
    - This class handles communication with a Hydra node via HTTP (using requests) and WebSocket, providing methods to fetch data (e.g., UTxOs, protocol parameters) and submit transactions.
    - It also manages Hydra Head lifecycle commands and processes events from the node using pyee.

    Usage:
    - provider = HydraProvider(http_url="http://123.45.67.890:4001")
        asyncio.run(provider.connect())
    """
    def __init__(
        self,
        http_url: str,
        history: bool = False,
        address: Optional[str] = None,
        ws_url: Optional[str] = None,
    ):
        """
        Description: Initialize the HydraProvider with connection details.

        Arguments:
        - http_url (str): The HTTP URL of the Hydra node (e.g., 'http://123.45.67.890:4001').
        - history (bool, optional): Whether to enable history tracking. Defaults to False.
        - address (str, optional): The address associated with the provider. Defaults to None.
        - ws_url (str, optional): The WebSocket URL for the Hydra node. Defaults to None.
        """
        self._status = HydraStatus.DISCONNECTED
        self._http_url = http_url
        self._event_emitter = AsyncIOEventEmitter()
        self._connection = HydraConnection(
            http_url=http_url,
            address=address,
            event_emitter=self._event_emitter,
            history=history,
            ws_url=ws_url
        )
        self._session = requests.Session()
        self._status_callbacks = []

    async def init(self):
        """
        Initializes a new Hydra Head. This is a no-op if a Head is already open.
        """
        self._connection.send({"tag": "Init"})
    
    async def abort(self):
        """
        Aborts a Hydra Head before it is opened. Can only be done before all participants have committed.
        """
        self._connection.send({"tag": "Abort"})
    
    async def close(self):
        """
        Closes the Hydra Head, starting the contestation phase.
        """
        self._connection.send({"tag": "Close"})
    
    async def contest(self):
        """
        Contests the latest snapshot after head closure.
        """
        self._connection.send({"tag": "Contest"})

    async def fanout(self):
        """
        Finalizes the Hydra Head after the contestation period.
        """
        self._connection.send({"tag": "Fanout"})

    async def connect(self):
        """
        Description: Connect to the Hydra node via WebSocket.
        Establishes a WebSocket connection if not already connected.
        This is a no-op if a connection already exists.
        Returns: None
        """
        if self._status != HydraStatus.DISCONNECTED:
            return
        self._connection.connect()
        self._status = HydraStatus.CONNECTED

    def subscribe_snapshot_utxo(self) -> List[UTxO]:
        """
        Description: Fetch a set of unspent transaction outputs from the snapshot.
        Returns: List[UTxO]: A list of UTxOs from the snapshot.
        """
        response = self.get("snapshot/utxo")
        print(response)
        utxos: List[UTxO] = []
        for ref, data in response.items():
            print(ref)
            print(data)
            hydra_utxo = HydraUTxO(
                address=data.get("address"),
                datum=data.get("datum"),
                datumhash=data.get("datumhash"),
                inline_datum=data.get("inlineDatum"),
                inline_datum_raw=data.get("inlineDatumRaw"),
                inline_datumhash=data.get("inlineDatumhash"),
                value=data.get("value"),
            )
            utxo = to_utxo(hydra_utxo, ref)
            utxos.append(utxo)

        return utxos

    def fetch_utxos(self, tx_hash: Optional[str] = None, output_index: Optional[str] = None) -> List[UTxO]:
        """
        Description: Fetch UTxOs from the Hydra node's snapshot, optionally filtered by hash and index.

        Args:
        - hash (str, optional): The transaction hash to filter UTxOs. Defaults to None.
        - index (int, optional): The output index to filter UTxOs. Defaults to None.

        Returns: 
        - List[UTxO]: A list of unspent transaction outputs matching the criteria.
        """

    def fetch_address_utxos(self, address: str) -> List[UTxO]:
        """
        Description: Fetch UTxOs for a specific address.
        Args:
        - address (str): The Cardano address to fetch UTxOs for.
        Returns:
        - List[UTxO]: A list of unspent transaction outputs for the given address.
        """
        return self.utxos(address=address)
    


    async def new_tx(self, cbor_hex: str, type: str, description: str = "", tx_id: Optional[str] = None) -> None:
        """
        Description: Submits a transaction through the Hydra Head. The transaction is only broadcast if well-formed and valid.

        Arguments:
        - cbor_hex (str): The base16-encoding of the CBOR-encoded transaction.
        - type (str): The transaction type, one of: "Tx ConwayEra", "Unwitnessed Tx ConwayEra", "Witnessed Tx ConwayEra".
        - description (str, optional): A human-readable description of the transaction. Defaults to "".
        - tx_id (str, optional): The transaction ID. Defaults to None.

        Returns: None
        """
        hydra_transaction: HydraTransaction = {
            "type": type,
            "description": description,
            "cbor_hex": cbor_hex,
            "tx_id": tx_id,
        }
        payload = {"tag": "NewTx", "transaction": hydra_transaction}
        self._connection.send(payload)

    def on_message(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Registers a callback for handling incoming messages.
        :param callback: The function to call when a message is received.
        """
        
    def on_status_change(self, callback: Callable[[HydraStatus], None]) -> None:
        """
        Description: Registers a callback to handle changes in the Hydra node's connection status.
        Arguments: 
        - callback (Callable): The callback function to be called when the status changes.
        Returns: None
        """

    def get(self, url: str) -> Any:
        """
        Description: Perform a generic HTTP GET request to the Hydra node.
        Arguments: 
        - url (str): The URL path to fetch data from (relative to base_url).
        Returns: The data returned from the server.
        Raises: If the request fails or the server returns an error.
        """
        try:
            response  = self._session.get(f"{self._http_url}/{url}")
            if response.status_code in (200, 202):
                return response.json()
            raise parse_error(response.json())
        except Exception as error:
            raise parse_error(error)
    
    async def post(self, url: str, payload: Any, headers: Dict[str, str] = {}) -> Any:
        """
        Description: Perform a generic HTTP POST request to the Hydra node.

        Arguments:
        - url (str): The URL path to post data to (relative to base_url).
        - payload (Any): The data to send in the request body.
        - headers (Dict[str, str], optional): Additional HTTP headers. Defaults to {}.

        Returns: The response data from the URL.
        Raises: If the HTTP request fails or returns an error status.
        """
        try:
            response = self._session.post(f"{self._http_url}/{url}", json=payload, headers=headers)
            if response.status_code in (200, 202):
                return response.json()
            raise parse_error(response.json())
        except Exception as error:
            raise parse_error(error)




