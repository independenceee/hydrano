from typing import Any, List

from pycardano import UTxO

from hydrano.interfaces import IFetcher, ISubmitter
from hydrano.providers import HydraProvider
from hydrano.types import HydraTransaction, HydraUTxO


class HydraInstance:
    def __init__(
        self,
        hydra_provider: HydraProvider,
        fetcher: IFetcher,
        submitter: ISubmitter,
    ):
        """
        Desc: Represents an instance of the Hydra protocol, providing methods to interact with a Hydra head.
        Args:  
        - hydra_provider: The Hydra provider instance for interacting with the Hydra head. 
        - fetcher: The fetcher instance for fetching UTxOs and other data. 
        - submitter: The submitter instance for submitting transactions.
        """
        self.hydra_provider = hydra_provider
        self.fetcher = fetcher
        self.submitter = submitter

    async def __commit_to_hydra(self, payload: Any) -> str:
        """
        Description: Private method to build and commit a payload to the Hydra head.
        Arguments: 
        - payload (Any): The payload to commit, typically containing UTxO or blueprint transaction data.
        Returns: The CBOR hex string of the commit transaction.
        Raises: Any exceptions raised by the provider's build_commit method.
        """
        commit = await self.hydra_provider.build_commit(payload=payload, headers={
            "Content-Type": "application/json",
        })
        return commit.get("cborHex")

    async def __decommit_from_hydra(self, payload: Any) -> str:
        """
        Description: Private method to publish a decommit request to the Hydra head.
        Arguments: 
        - payload (Any): The payload for the decommit request, typically a transaction.
        Returns: The result of the decommit operation (e.g., CBOR hex string).
        Raises: Any exceptions raised by the provider's publish_decommit method.
        """
        decommit = await self.hydra_provider.publish_decommit(payload=payload, headers={
            "Content-Type": "application/json",
        })
        return decommit

    async def commit_funds(self, transaction_id: str, index: int) -> str:
        """
        Description: Commits funds to the Hydra head by selecting a UTxO to make available on layer 2.
        Arguments: 
        - transaction_id (str): The transaction hash of the UTxO to commit. 
        - index (int): The output index of the UTxO to commit.
        Returns: The CBOR hex string of the commit transaction, ready to be partially signed.
        Raises:  If the specified UTxO is not found.
        """
        utxos: List[UTxO] = await self.fetcher.fetch_utxos(transaction_id=transaction_id, index=index)
        if not utxos:
            raise Exception("UTxO not found")
        utxo = utxos[0]
        hydra_utxo = await HydraUTxO(
            address=str(utxo.output.address)
        )
        return await self.__commit_to_hydra({f"{transaction_id}#{index}": hydra_utxo})

    async def incremental_commit_funds(self, tx_hash: str, output_index: int) -> str:
        """
        Description: Incrementally commits funds to the Hydra head by selecting a UTxO to make available on layer 2.
        This method is a wrapper around commit_funds to support incremental commits.

        Arguments:
            - tx_hash (str): The transaction hash of the UTxO to commit.
            - output_index (int): The output index of the UTxO to commit.

        Returns: The CBOR hex string of the commit transaction, ready to be partially signed.

        Raises: If the specified UTxO is not found.
        """
        return await self.commit_funds(tx_hash, output_index)
    
    async def commit_blueprint(self, transaction_id: str, index: int, transaction: HydraTransaction) -> str:
        """
        Description: Commits a Cardano transaction blueprint to the Hydra head.
        This method allows committing a transaction in the Cardano text envelope format
        (a JSON object with 'type' and 'cborHex' fields) as a blueprint UTxO to the Hydra head.
        Useful for advanced use cases like reference scripts, inline datums, or other on-chain
        features requiring a transaction context.

        See: https://hydra.family/head-protocol/docs/how-to/commit-blueprint

        Arguments:
            - tx_hash (str): The transaction hash of the UTxO to be committed as a blueprint.
            - output_index (int): The output index of the UTxO to be committed.
            - transaction (hydraTransaction): The Cardano transaction in text envelope format, containing:
                - type: The type of the transaction (e.g., "Unwitnessed Tx ConwayEra").
                - description: (Optional) A human-readable description of the transaction.
                - cborHex: The CBOR-encoded unsigned transaction.

        Returns: The CBOR hex string of the commit transaction, ready to be partially signed.

        Raises: If the specified UTxO is not found.
        """

    async def incremental_blueprint_commit(self, transaction_id: str, index: int, transaction: HydraTransaction) -> str:
        """
        Description: Incrementally commits a Cardano transaction blueprint to the Hydra head.

        This method allows incrementally committing a transaction in the Cardano text envelope format
        (a JSON object with 'type' and 'cborHex' fields) as a blueprint UTxO to the Hydra head.
        Useful for advanced use cases like reference scripts, inline datums, or other on-chain
        features requiring a transaction context.

        See: https://hydra.family/head-protocol/docs/how-to/commit-blueprint

        Args:
            - transaction_id (str): The transaction hash of the UTxO to be committed as a blueprint.
            - index (int): The output index of the UTxO to be committed.
            - transaction (hydraTransaction): The Cardano transaction in text envelope format, containing:
                - type: The type of the transaction (e.g., "Unwitnessed Tx ConwayEra").
                - description: (Optional) A human-readable description of the transaction.
                - cborHex: The CBOR-encoded unsigned transaction.

        Returns: The CBOR hex string of the commit transaction, ready to be partially signed.

        Raises: If the specified UTxO is not found.
        """
        return await self.commit_blueprint(transaction_id=transaction_id, index=index, transaction= {
            "type": transaction.type,
            "cborHex": transaction.cbor_hex,
            "description": transaction.description,
            "txId": transaction.tx_id
        })

    async def decommit(self, transaction: HydraTransaction) -> str:
        """
        Description: Requests to decommit a UTxO from a Hydra head by providing a decommit transaction.
        Upon reaching consensus, this will eventually result in the corresponding transaction
        outputs becoming available on layer 1.

        Arguments:
            - transaction (hydraTransaction): The transaction to decommit.

        Returns: The result of the decommit operation (e.g., CBOR hex string).

        Raises: Any exceptions raised by the provider's publish_decommit method.
        """
        return self.__decommit_from_hydra(payload=transaction)

    async def incremental_decommit(self, transaction: HydraTransaction) -> str:
        """
        Description: Requests an incremental decommit of a UTxO from a Hydra head.
        This method is a wrapper around decommit to support incremental decommits.
        See: https://hydra.family/head-protocol/docs/how-to/incremental-decommit
        Arguments:
            - transaction (hydraTransaction): The transaction to decommit.
        Returns: The result of the decommit operation (e.g., CBOR hex string).
        Raises: Any exceptions raised by the provider's publish_decommit method.
        """
        return await self.decommit(transaction)