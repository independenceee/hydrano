import asyncio

from hydrano.hydra_provider import HydraProvider


async def main():
    http_url = "http://194.195.87.66:4001"
    provider = HydraProvider(http_url=http_url)
    print("🔌 Connecting to Hydra node...")
    print("✅ Connected")

    # Gọi thử Init (nếu head chưa mở)
    print("📢 Sending Init command...")
    await provider.connect()
    await provider.init()

    print("📦 Fetching snapshot UTxOs...")
    # print("UTxOs:", utxos)

if __name__ == "__main__":
    asyncio.run(main())
