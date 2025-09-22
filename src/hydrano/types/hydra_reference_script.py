from dataclasses import dataclass
from typing import Optional, Union

import cbor2
from pycardano import CBORSerializable, NativeScript, PlutusScript


@dataclass 
class HydraScriptInfomation:
    script_instance: Optional[Union[PlutusScript, NativeScript]]
    script_type: str
    script_language: Optional[str]

@dataclass
class HydraReferenceScript:
    script_language: str
    script: dict


async def get_reference_script_info(script_ref: Optional[str]) -> HydraScriptInfomation:
    """
    Determines the type and language of a script reference.
    
    Args:
        script_ref: The script reference (e.g., CBOR hex string) from a UTxO, or None.
    
    Returns:
        A HydraScriptInfo object containing the script instance, type, and language.
    """
    script_instance: Optional[Union[PlutusScript, NativeScript]] = None
    script_type: str = "Unknown"
    script_language: Optional[str] = None

    if script_ref:
        try:
            # Decode CBOR hex string to bytes
            cbor_bytes = bytes.fromhex(script_ref)
            # Deserialize CBOR (mimics _ScriptRef.from_primitive)
            cbor_data = cbor2.loads(cbor_bytes)
            
            # Expect a CBORTag(24, script_data) for script references
            if isinstance(cbor_data, cbor2.CBORTag) and cbor_data.tag == 24:
                script_data = cbor2.loads(cbor_data.value)
                # _Script format: [type, script_data]
                if isinstance(script_data, list) and len(script_data) == 2:
                    script_type_id, script_content = script_data
                    if script_type_id == 0:
                        # NativeScript
                        script_instance = NativeScript.from_primitive(script_content)
                        script_type = "SimpleScript"
                        script_language = "NativeScriptLanguage SimpleScript"
                    elif script_type_id in (1, 2, 3):
                        # PlutusScript (V1, V2, V3)
                        script_instance = PlutusScript.from_version(script_type_id, script_content)
                        script_type = f"PlutusScriptV{script_type_id}"
                        script_language = f"PlutusScriptLanguage PlutusScriptV{script_type_id}"
        except (ValueError, cbor2.CBORError) as error:
            print(f"Error decoding script_ref: {error}")

    return HydraScriptInfomation(
        script_instance=script_instance,
        script_type=script_type,
        script_language=script_language
    )


async def hydra_reference_script(script_reference: Optional[str]) -> Optional[HydraReferenceScript]:
    """
    Desc: Convert a script reference to a hydraReferenceScript object.
    Args: script_ref: The script reference (e.g., CBOR hex string) from a UTxO, or None.
    Returns: A HydraReferenceScript object or None if script_ref is invalid or missing.
    """
    info = await get_reference_script_info(script_reference)
    
    if not script_reference or not info.script_instance or not info.script_language:
        return None
    
    return HydraReferenceScript(
        script_language=info.script_language,
        script={
            "cborHex": script_reference,
            "description": "",
            "type": info.script_type
        }
    )