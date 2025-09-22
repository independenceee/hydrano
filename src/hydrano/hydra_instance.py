from pycardano import BlockFrostChainContext

from hydrano.hydra_provider import HydraProvider


class HydraInstance:
    def __init__(
        self,
        provider: HydraProvider,
        fetcher: BlockFrostChainContext,
        submitter: BlockFrostChainContext
    ):
        """
        Desc: Represents an instance of the Hydra protocol, providing methods to interact with a Hydra head.
        Args: provider: The Hydra provider instance for interacting with the Hydra head. fetcher: The fetcher instance for fetching UTxOs and other data. submitter: The submitter instance for submitting transactions.
        """
        self.provider = provider
        self.fetcher = fetcher
        self.submitter = submitter
        