from typing import List, Optional

from blockfrost import ApiError, BlockFrostApi
from pycardano import (
    Address,
    AssetName,
    MultiAsset,
    PolicyId,
    TransactionInput,
    TransactionOutput,
    UTxO,
    Value,
)

from hydrano.interfaces import IFetcher, ISubmitter
from hydrano.types import BlockfrostOutput, BlockfrostTransaction


class BlockfrostProvider(IFetcher, ISubmitter):
    def __init__(
        self,
        project_id: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        self._blockfrost_api = BlockFrostApi(
            project_id=project_id,
            base_url=base_url,
            api_version=api_version
        )

    def fetch_utxos(self, transaction_id: str, index: Optional[int] = None) -> List[UTxO]:
        try:
            response: BlockfrostTransaction = self._blockfrost_api.transaction_utxos(hash=transaction_id)
            utxos: List[UTxO] = []
            for output in response.outputs:
                utxos.append(self.__to_utxo(output, transaction_id=transaction_id))
            if index is not None:
                utxos = [utxo for utxo in utxos if utxo.input.index == index]

            return utxos 
            
        except ApiError as e:
            raise Exception(f"Failed to fetch UTXOs: {e}") from e

    def submit_tx(self, tx: str):
        try:
            return self._blockfrost_api.transaction_submit_cbor(tx_cbor=tx)
        except ApiError as e:
            raise Exception(f"Failed to submit transaction: {e}") from e

    def __to_utxo(self, output: BlockfrostOutput, transaction_id: str) -> UTxO:
        tx_input: TransactionInput = TransactionInput(transaction_id=transaction_id, index=output.output_index)
        
        tx_output: TransactionOutput = TransactionOutput(
            address=Address.from_primitive(output.address),
            amount=output.amount,
            datum=output.inline_datum,
            datum_hash=output.data_hash,
            script=output.reference_script_hash
        )

        return UTxO(
            input=tx_input,
            output=tx_output
        )