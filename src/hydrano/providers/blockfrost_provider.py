from argparse import Namespace
from typing import List, Optional

from blockfrost import ApiError, BlockFrostApi
from pycardano import (
    Address,
    AssetName,
    BlockFrostChainContext,
    MultiAsset,
    PolicyId,
    ScriptHash,
    TransactionId,
    TransactionInput,
    TransactionOutput,
    UTxO,
    Value,
)

from hydrano.interfaces import IFetcher, ISubmitter
from hydrano.types import BlockfrostAmount, BlockfrostOutput, BlockfrostTransaction


class BlockfrostProvider(IFetcher, ISubmitter, BlockFrostChainContext):
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
                utxos.append(self.__to_utxo(output=output, transaction_id=transaction_id))
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
        tx_input: TransactionInput = TransactionInput(
            transaction_id=TransactionId.from_primitive(value=transaction_id), 
            index=output.output_index
        )
        
        tx_output: TransactionOutput = TransactionOutput(
            address=Address.from_primitive(output.address),
            amount=self.__to_assets(assets=output.amount),
            datum=output.inline_datum,
            datum_hash=output.data_hash,
            script=output.reference_script_hash
        )

        return UTxO(
            input=tx_input,
            output=tx_output
        )
    
    def __to_assets(self, assets: List[Namespace]) -> dict:
        result = {"coin": 0, "multi_asset": {}}
        for asset in assets:  
            unit = asset.unit 
            quantity = int(asset.quantity)  
            if quantity == 0:
                continue
            if quantity < 0:
                raise ValueError(f"Negative quantity for unit {unit}: {quantity}")
            if unit == "lovelace":
                result["coin"] = quantity
            else:
                if len(unit) < 56:
                    raise ValueError(f"Invalid unit length: {unit}")
                policy_id = unit[:56]
                asset_name = unit[56:]
                try:
                    policy_hash = ScriptHash(bytes.fromhex(policy_id))
                    asset_name_obj = AssetName(asset_name.encode("utf-8")) if asset_name else AssetName(b"")
                    if policy_hash not in result["multi_asset"]:
                        result["multi_asset"][policy_hash] = {}
                    result["multi_asset"][policy_hash][asset_name_obj] = quantity
                except ValueError:
                    raise ValueError(f"Invalid policy_id in unit: {unit}")
        return result
