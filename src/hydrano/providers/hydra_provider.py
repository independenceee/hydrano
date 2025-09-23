import asyncio
import json
import time
from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional

import requests
from pycardano import ProtocolParameters, UTxO
from pyee.asyncio import AsyncIOEventEmitter

from hydrano.connections.hydra_connection import HydraConnection
from hydrano.types.hydra_status import HydraStatus
from hydrano.types.hydra_transaction import HydraTransaction
from hydrano.types.hydra_utxos import HydraUTxO, to_utxo
from hydrano.utils.parse_error import parse_error


class HydraProvider:
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
        utxos: List[UTxO] = []
        for ref, data in response.items():
            hydra_utxo = HydraUTxO(
                address=data.get("address"),
                datum=data.get("datum"),
                datum_hash=data.get("datumhash"),
                inline_datum=data.get("inlineDatum"),
                inline_datum_raw=data.get("inlineDatumRaw"),
                inline_datum_hash=data.get("inlineDatumhash"),
                value=data.get("value"),
            )
            utxo = to_utxo(hydra_utxo, ref)
            utxos.append(utxo)

        return utxos

    def fetch_utxos(self, transaction_id: Optional[str] = None, index: Optional[int] = None) -> List[UTxO]:
        """
        Description: Fetch UTxOs from the Hydra node's snapshot, optionally filtered by hash and index.

        Args:
        - transaction_id (str, optional): The transaction hash to filter UTxOs. Defaults to None.
        - index (int, optional): The output index to filter UTxOs. Defaults to None.

        Returns: 
        - List[UTxO]: A list of unspent transaction outputs matching the criteria.
        """
        snapshot_utxos = self.subscribe_snapshot_utxo()
        outputs = [
            utxo for utxo in snapshot_utxos
            if transaction_id is None or utxo.input.transaction_id == transaction_id
        ]
        if index is not None:
            outputs = [utxo for utxo in outputs if utxo.input.index == index]
        return outputs

    def fetch_address_utxos(self, address: str) -> List[UTxO]:
        """
        Description: Fetch UTxOs for a specific address.
        Args:
        - address (str): The Cardano address to fetch UTxOs for.
        Returns:
        - List[UTxO]: A list of unspent transaction outputs for the given address.
        """
        utxos = self.fetch_utxos()
        return [utxo for utxo in utxos  if str(utxo.output.address) == address]
    
    def subscribe_protocol_parameters(self) ->  ProtocolParameters:
        """
        Description: Fetch protocol parameters from the Hydra node.
        Returns:
        - Protocol: The protocol parameters mapped to the Protocol type.
        """
        data = self.get("protocol-parameters")
        protocol_params = ProtocolParameters(
            min_fee_constant=data.get("txFeeFixed", 0),
            min_fee_coefficient=data.get("txFeePerByte", 0),
            max_block_size=data.get("maxBlockBodySize", 0),
            max_tx_size=data.get("maxTxSize", 0),
            max_block_header_size=data.get("maxBlockHeaderSize", 0),
            key_deposit=data.get("stakeAddressDeposit", 0),
            pool_deposit=data.get("stakePoolDeposit", 0),
            pool_influence=Fraction(str(data.get("poolPledgeInfluence", 0))),
            monetary_expansion=Fraction(str(data.get("monetaryExpansion", 0))),
            treasury_expansion=Fraction(str(data.get("treasuryCut", 0))),
            decentralization_param=Fraction(0), 
            extra_entropy="",
            protocol_major_version=data["protocolVersion"]["major"],
            protocol_minor_version=data["protocolVersion"]["minor"],
            min_utxo=data.get("minUTxOValue", 0),
            min_pool_cost=data.get("minPoolCost", 0),
            price_mem=Fraction(str(data["executionUnitPrices"].get("priceMemory", 0))),
            price_step=Fraction(str(data["executionUnitPrices"].get("priceSteps", 0))),
            max_tx_ex_mem=data["maxTxExecutionUnits"]["memory"],
            max_tx_ex_steps=data["maxTxExecutionUnits"]["steps"],
            max_block_ex_mem=data["maxBlockExecutionUnits"]["memory"],
            max_block_ex_steps=data["maxBlockExecutionUnits"]["steps"],
            max_val_size=data.get("maxValueSize", 0),
            collateral_percent=data.get("collateralPercentage", 0),
            max_collateral_inputs=data.get("maxCollateralInputs", 0),
            coins_per_utxo_word=0,  
            coins_per_utxo_byte=data.get("utxoCostPerByte", 0),
            cost_models=data.get("costModels", {})
        )
        return protocol_params

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
            "cborHex": cbor_hex,
            "txId": tx_id
        }
        payload = {"tag": "NewTx", "transaction": hydra_transaction}
        await self._connection.send(payload)

    async def wait_for_tx_response(self, tx: str) -> str:
        """
        Description: Internal helper to wait for TxValid or TxInvalid events.

        Args:
        - tx (str): The transaction CBOR hex to match.

        Returns: The transaction ID if valid.
        Raises: If the transaction is invalid.
        """
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        def callback(message: Dict[str, Any]) -> None:
            if message.get("tag") == "TxValid" and message.get("transaction", {}).get("cborHex") == tx:
                future.set_result(message["transaction"]["txId"])
            elif message.get("tag") == "TxInvalid" and message.get("transaction", {}).get("cborHex") == tx:
                future.set_exception(Exception(json.dumps(message["validationError"])))

        self._event_emitter.on("onmessage", callback)
        try:
            return await future
        finally:
            self._event_emitter.remove_listener("onmessage", callback)

    async def submit_tx(self, tx: str) -> str:
        """
        Description: Submit a transaction to the Hydra node.
        Unlike other providers, Hydra does not immediately return a transaction hash.
        This method waits for a TxValid or TxInvalid event to resolve or reject.

        Args:
        - tx (str): The transaction in CBOR hex format.

        Returns: The transaction ID if valid.
        Raises: If the transaction is invalid, raises an error with validation details.
        """
        try:
            await self.new_tx(tx, "Witnessed Tx ConwayEra")
            tx_id = await self.wait_for_tx_response(tx)
            return tx_id
        except Exception as error:
            raise parse_error(error)
        
    async def decommit(self, cbor_hex: str, type: str, description: str) -> None:
        """
        Description: Request to decommit a UTxO from a Head.
        Upon reaching consensus, the corresponding transaction outputs will become available on layer 1.

        Args:
        - cbor_hex (str): The base16-encoded CBOR data of the decommit transaction.
        - type (str): The transaction type, must be "Tx ConwayEra", "Unwitnessed Tx ConwayEra", or "Witnessed Tx ConwayEra".
        - description (str): Description of the decommit transaction.

        Returns: None
        """
        payload = {
            "tag": "Decommit",
            "decommitTx": {
                "type": type,
                "description": description,
                "cborHex": cbor_hex
            }
        }
        await self._connection.send(payload)

    def build_commit(self, payload: Any, headers: Dict[str, str] = {}) -> str:
        """
        Description: Draft a commit transaction for submission to the layer 1 network.

        Arguments:
        - payload (Any): The data to send in the POST request.
        - headers (Dict[str, str], optional): Additional HTTP headers. Defaults to {}.

        Returns: The transaction in CBOR hex format.
        """
        return self.post("commit", payload=payload, headers=headers)

    def publish_decommit(self, payload: Any, headers: Dict[str, str] ={}) -> str:
        """
        Description: Publishing the uncommitted transaction applied to Hydra's local ledger state.
        The specified transaction outputs will be available on layer 1 after successful processing.

        Arguments:
        - payload (Any): Data to send in the POST request.
        - headers (Dict[str, str], optional): Additional HTTP headers. Defaults to {}.

        Returns: Transaction in CBOR hex format.
        """
        return self.post("decommit", payload=payload, headers=headers)

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




