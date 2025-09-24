from blockfrost import ApiUrls
from pycardano import (
    Address,
    BlockFrostChainContext,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    StakeSigningKey,
    StakeVerificationKey,
    TransactionBuilder,
    Value,
)

from hydrano import HydraInstance, HydraProvider
from hydrano.providers import BlockfrostProvider

http_url ="http://194.195.87.66:4002"
project_id="previewdbVDuvrQuSQ96poPN7ZmAZIHEIIPt7y1"

hydra_provider = HydraProvider(
    http_url=http_url
)
blockfrost_provider = BlockfrostProvider(
    project_id=project_id, 
    base_url=ApiUrls.preview.value
)
hydra_instance = HydraInstance(
    hydra_provider=hydra_provider, 
    fetcher=blockfrost_provider,
    submitter=blockfrost_provider
)

network = Network.TESTNET
context = BlockFrostChainContext(
    project_id=project_id, 
    base_url=ApiUrls.preview.value
)

payment_signing_key = PaymentSigningKey.load("payment.skey")
payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)

stake_signing_key = StakeSigningKey.load("stake.skey")
stake_verification_key = StakeVerificationKey.from_signing_key(stake_signing_key)

payment_address = Address(
    payment_part=payment_verification_key.hash(),
    staking_part=stake_verification_key.hash(),
    network=network
)

print(f"Payment Address: {payment_address}")

utxos = context.utxos(payment_address)
if not utxos:
    raise ValueError(f"Không tìm thấy UTxO cho địa chỉ {payment_address}")

# In UTxO để kiểm tra
print("Danh sách UTxO:")
# for utxo in utxos:
    # print(utxo)

commit_funds_unsigned_tx =  hydra_instance.commit_funds(transaction_id="8b77626b8ac3eae750a483e61fe37eff34680b031cda71db9da7bc619b66974e", index=3)

print(commit_funds_unsigned_tx)


