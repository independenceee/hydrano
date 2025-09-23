import asyncio

from hydrano.providers import HydraProvider


def main():
    http_url = "http://194.195.87.66:4001"
    provider = HydraProvider(http_url=http_url)
    print("🔌 Connecting to Hydra node...")
    print("✅ Connected")

    # Gọi thử Init (nếu head chưa mở)
    print("📢 Sending Init command...")
    provider.connect()
    provider.init()

    print("📦 Fetching snapshot UTxOs...")
    # print("UTxOs:", utxos)

if __name__ == "__main__":
    main()
