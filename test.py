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

PROJECT_ID = "previewdbVDuvrQuSQ96poPN7ZmAZIHEIIPt7y1" 
network = Network.TESTNET
context = BlockFrostChainContext(PROJECT_ID, base_url=ApiUrls.preview.value)

# Payment key
# payment_signing_key = PaymentSigningKey.generate()
# payment_signing_key.save("payment.skey")
payment_signing_key = PaymentSigningKey.load("payment.skey")
payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)

# Stake key
# stake_signing_key = StakeSigningKey.generate()
# stake_signing_key.save("stake.skey")
stake_signing_key = StakeSigningKey.load("stake.skey")
stake_verification_key = StakeVerificationKey.from_signing_key(stake_signing_key)

# Payment address
payment_address = Address(
    payment_part=payment_verification_key.hash(),
    staking_part=stake_verification_key.hash(),
    network=network
)


# In địa chỉ để kiểm tra
print(f"Payment Address: {payment_address}")

utxos = context.utxos(payment_address)
if not utxos:
    raise ValueError(f"Không tìm thấy UTxO cho địa chỉ {payment_address}")

# In UTxO để kiểm tra
print("Danh sách UTxO:")
for utxo in utxos:
    print(utxo)

# # Bước 4: Xây dựng giao dịch
# builder = TransactionBuilder(context)

# # Thêm input từ payment address
# builder.add_input_address(payment_address)

# # Thêm output: Chuyển 1 ADA (1_000_000 lovelace) đến địa chỉ đích
# receiver_address = Address("addr_test1vr...")  # Thay bằng địa chỉ testnet đích thực
# amount_to_send = 1_000_000  # 1 ADA
# builder.add_output(receiver_address, Value(ada_amount=amount_to_send))

# # Ký giao dịch, tự động tính phí và gửi change về payment_address
# signed_tx = builder.build_and_sign(
#     signing_keys=[payment_signing_key],
#     change_address=payment_address
# )

# # Bước 5: Gửi giao dịch
# context.submit_tx(signed_tx)

# print(f"Giao dịch đã gửi: {signed_tx.id}")