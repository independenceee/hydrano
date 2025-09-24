from typing import Dict, List, Tuple

from pycardano import Asset, AssetName, MultiAsset, ScriptHash, Value

HydraAssets = Dict[str, int]

def hydra_assets(assets: List[Tuple[str, AssetName, int]]) -> HydraAssets:
    """
    Convert a list of (policy_id, asset_name, quantity) tuples to a hydraAssets dictionary.
    
    Args:
        assets: List of tuples (policy_id, asset_name, quantity), where:
                - policy_id is a string (empty for Lovelace),
                - asset_name is a pycardano AssetName (empty for Lovelace),
                - quantity is an integer.
    
    Returns:
        A dictionary with 'lovelace' and other units (policy_id + asset_name) as keys,
        mapping to their total quantities.
    """
    result: HydraAssets = {"lovelace": 0}
    for unit, quantity in assets:
        if quantity < 0:
            raise ValueError(f"Negative quantity for asset {unit}: {quantity}")
        unit = "lovelace" if not unit else f"{unit}"
        
        result[unit] = result.get(unit, 0) + quantity
    
    return {key: value for key, value in result.items() if value != 0}

def to_assets(hydra_assets: HydraAssets) -> dict:
    """
    Convert a hydraAssets dictionary back to a list of (policy_id, asset_name, quantity) tuples.
    
    Args:
        hydra_assets: A dictionary mapping asset units to their quantities.
    
    Returns:
        A list of (policy_id, asset_name, quantity) tuples.
    """
    result = {"coin": 0, "multi_asset": {}}
    
    for unit, quantity in hydra_assets.items():
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

def hydra_assets_from_value(value: Value) -> HydraAssets:
    """
    Convert a pycardano Value object to a hydraAssets dictionary.
    
    Args:
        value: A pycardano Value object containing coin (Lovelace) and multi_asset.
    
    Returns:
        A hydraAssets dictionary with 'lovelace' and other units.
    """
    assets = []
    # Add Lovelace if present
    if value.coin > 0:
        assets.append(("", AssetName(b""), value.coin))
    # Add multi-assets
    for policy_id, asset in value.multi_asset.items():
        for asset_name, quantity in asset.data.items():  # Access Asset's internal dictionary
            assets.append((str(policy_id), asset_name, quantity))
    
    return hydra_assets(assets)

def hydra_assets_to_value(hydra_assets: HydraAssets) -> Value:
    """
    Convert a hydraAssets dictionary to a pycardano Value object.
    
    Args:
        hydra_assets: A dictionary mapping asset units to their quantities.
    
    Returns:
        A pycardano Value object with coin (Lovelace) and multi_asset.
    """
    multi_asset = MultiAsset()
    lovelace = 0
    
    for unit, quantity in hydra_assets.items():
        if unit == "lovelace":
            lovelace = quantity
        else:
            # Assume unit = policy_id (56 chars hex) + asset_name
            policy_id = unit[:56] if len(unit) >= 56 else ""
            asset_name = unit[56:] if len(unit) > 56 else ""
            try:
                policy_hash = ScriptHash(bytes.fromhex(policy_id)) if policy_id else ScriptHash(b"")
                if policy_hash not in multi_asset:
                    multi_asset[policy_hash] = Asset()
                multi_asset[policy_hash][AssetName(asset_name.encode("utf-8")) if asset_name else AssetName(b"")] = quantity
            except ValueError:
                raise ValueError(f"Invalid policy_id in unit: {unit}")
    
    return Value(coin=lovelace, multi_asset=multi_asset)