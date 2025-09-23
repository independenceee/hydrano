from abc import abstractmethod


class ISubmitter:
    """
    ISubmitter defines a generic interface for submitting transactions
    to the Cardano blockchain (or to a layer-2 such as Hydra).
    This abstraction allows different implementations to be swapped in easily,
    for example: Using Blockfrost API Using a local Cardano-node Using a Hydra node Using a mock implementation for testing
    """

    @abstractmethod
    async def submit_tx(self, tx: str) -> str:
        """
        Description: Submit a signed transaction to the network.

        Arguments:
        - tx (str): The serialized transaction in hexadecimal (CBOR hex) format. This should be a fully signed transaction ready for submission.

        Returns:
        - The transaction ID (hash) of the submitted transaction.
        - If submission fails, the implementation may raise an exception.
        """
        pass
