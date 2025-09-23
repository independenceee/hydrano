from hydrano.hydra_provider import HydraProvider


def main():
    http_url = "http://194.195.87.66:4001"
    provider = HydraProvider(http_url=http_url)
    print("🔌 Connecting to Hydra node...")
    print("✅ Connected")

    print("📦 Fetching snapshot UTxOs...")
    utxos = provider.subscribe_protocol_parameters()
    print("UTxOs:", utxos)


if __name__ == "__main__":
    main()