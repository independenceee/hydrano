from typing import Any

from pycardano import BlockFrostChainContext

from hydrano.hydra_provider import HydraProvider
from hydrano.types.hydra_transaction import HydraTransaction


class HydraInstance:
    def __init__(
        self,
        hydra_provider: HydraProvider,
        fetcher: BlockFrostChainContext,
        submitter: BlockFrostChainContext
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

    async def _commit_to_hydra(self, payload: Any) -> str:
        """
        Description: Private method to build and commit a payload to the Hydra head.
        Arguments: 
        - payload (Any): The payload to commit, typically containing UTxO or blueprint transaction data.
        Returns: The CBOR hex string of the commit transaction.
        Raises: Any exceptions raised by the provider's build_commit method.
        """

    async def _decommit_from_hydra(self, payload: Any) -> str:
        """
        Description: Private method to publish a decommit request to the Hydra head.
        Arguments: 
        - payload (Any): The payload for the decommit request, typically a transaction.
        Returns: The result of the decommit operation (e.g., CBOR hex string).
        Raises: Any exceptions raised by the provider's publish_decommit method.
        """

    async def commit_funds(self, tx_hash: str, output_index: int) -> str:
         """
        Description: Commits funds to the Hydra head by selecting a UTxO to make available on layer 2.
        Arguments: 
        - tx_hash (str): The transaction hash of the UTxO to commit. 
        - output_index (int): The output index of the UTxO to commit.
        Returns: The CBOR hex string of the commit transaction, ready to be partially signed.
        Raises:  If the specified UTxO is not found.
        """
         
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
    
    async def commit_blueprint(self, tx_hash: str, output_index: int, transaction: HydraTransaction) -> str:
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

    async def incremental_blueprint_commit(self, tx_hash: str, output_index: int, transaction: HydraTransaction) -> str:
        """
        Description: Incrementally commits a Cardano transaction blueprint to the Hydra head.

        This method allows incrementally committing a transaction in the Cardano text envelope format
        (a JSON object with 'type' and 'cborHex' fields) as a blueprint UTxO to the Hydra head.
        Useful for advanced use cases like reference scripts, inline datums, or other on-chain
        features requiring a transaction context.

        See: https://hydra.family/head-protocol/docs/how-to/commit-blueprint

        Args:
            - tx_hash (str): The transaction hash of the UTxO to be committed as a blueprint.
            - output_index (int): The output index of the UTxO to be committed.
            - transaction (hydraTransaction): The Cardano transaction in text envelope format, containing:
                - type: The type of the transaction (e.g., "Unwitnessed Tx ConwayEra").
                - description: (Optional) A human-readable description of the transaction.
                - cborHex: The CBOR-encoded unsigned transaction.

        Returns: The CBOR hex string of the commit transaction, ready to be partially signed.

        Raises: If the specified UTxO is not found.
        """
        return await self.commit_blueprint(tx_hash, output_index, {
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