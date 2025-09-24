<div align="center">

<img src="https://hydra.family/head-protocol/img/hydra.png" width="120" alt="Hydra Logo" />

# **Hydrano**

**A Lightweight Python Toolkit for Cardano Hydra**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Cardano](https://img.shields.io/badge/Cardano-Hydra%20L2-green?logo=cardano)](https://cardano.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

</div>

## About Hydrano

Hydrano is an open-source Python toolkit designed to simplify interaction with **Cardano Hydra**, the Layer-2 scaling solution for the Cardano blockchain. Built for developers, Hydrano provides a lightweight, Pythonic interface to create, manage, and interact with Hydra Heads—state channels that enable fast, low-cost, and scalable off-chain transactions while maintaining Cardano's Layer-1 security guarantees. With minimal dependencies and a focus on simplicity, Hydrano is ideal for integrating Hydra functionality into Python-based projects, such as payment systems, gaming platforms, or DeFi applications.

### Key Benefits

- **Lightweight**: Minimal dependencies ensure a lean footprint for your projects.
- **Pythonic**: Intuitive APIs designed with Python best practices for ease of use.
- **Scalable**: Leverage Hydra’s high-throughput state channels for thousands of transactions per second (TPS) per head.
- **Secure**: Built to interact seamlessly with Hydra’s contestable commit mechanism, ensuring robust off-chain processing with Layer-1 settlement.
- **Developer-Friendly**: Clear documentation and modular design make it easy to extend for custom use cases.

### Use Cases

- **Micropayments**: Enable instant, low-fee transactions for tipping or subscriptions.
- **DeFi Applications**: Build scalable DeFi protocols with off-chain transaction processing.
- **Gaming**: Support real-time, high-frequency transactions for blockchain-based games.
- **Community Tools**: Create decentralized platforms with peer-to-peer payment channels.

---

## 🌐 Features

Hydrano offers a streamlined set of tools to interact with Cardano Hydra, focusing on simplicity and performance:

- **Hydra Head Management**: Create, join, and close Hydra Heads with minimal code.
- **Off-Chain Transactions**: Submit and validate transactions within Hydra state channels for near-instant processing (<1s latency).
- **Wallet Integration**: Connect to Cardano wallets via APIs like Blockfrost or Koios for transaction signing and submission.
- **State Channel Monitoring**: Real-time tracking of Head states and transaction logs.
- **Extensible Architecture**: Modular design allows developers to add custom validators or integrate with other Cardano tools.
- **Error Handling**: Robust handling of network issues, node sync errors, and invalid states.

---

## 🛠️ Technology Stack

| Component           | Technologies                             | Purpose                                                        |
| ------------------- | ---------------------------------------- | -------------------------------------------------------------- |
| **Core Toolkit**    | Python 3.8+, asyncio                     | Asynchronous client for Hydra node interactions.               |
| **Blockchain APIs** | Blockfrost/Koios (optional)              | Query Cardano blockchain data and submit Layer-1 transactions. |
| **Layer 2**         | Cardano Hydra (Rust-based nodes)         | Off-chain state channels for high-throughput transactions.     |
| **Dependencies**    | Minimal (e.g., `requests`, `websockets`) | Lightweight footprint for easy integration.                    |

---

## ⚡ Getting Started

Follow these steps to set up Hydrano and start building with Cardano Hydra. Prerequisites: Python 3.8+, a running Hydra node, and access to Cardano testnet ADA (available via the [Cardano faucet](https://docs.cardano.org/cardano-testnet/faucet)).

### 1. Clone the Repository

```bash
git clone https://github.com/independenceee/hydrano.git
cd hydrano
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

- Copy the example env file: `cp .env.example .env`
- Edit `.env`:
  - `HYDRA_NODE_URL`: URL of your Hydra node (e.g., `ws://localhost:4000`).
  - `BLOCKFROST_API_KEY`: (Optional) API key for Blockfrost or Koios queries.
  - `NETWORK`: Set to `preview` (testnet) or `mainnet`.
- Ensure a Hydra node is running. Refer to [Hydra Docs](https://hydra.family/head-protocol/) for setup instructions.

### 4. Run Examples

```bash
python examples/basic_head.py
```

This runs a sample script to create a Hydra Head, submit a transaction, and close the Head.

### 5. Test Locally

Use the provided test suite to verify functionality:

```bash
pytest tests/
```

**Troubleshooting**:

- **Hydra Node Issues**: Ensure the node is synced (`hydra-node --help`) and matches the network in `.env`.
- **API Errors**: Verify Blockfrost/Koios API keys and network alignment.
- **Test ADA**: Request testnet ADA from the Cardano faucet for preview network.

---

## 📦 Pip Installation

Hydrano can be installed as a Python package via Pip, making it easy to integrate into your projects without cloning the repository. The package is designed to be lightweight and compatible with standard Python workflows.

### Installing Hydrano via Pip

If Hydrano is published to PyPI, you can install it directly:

```bash
pip install hydrano
```

_Note_: As of September 2025, Hydrano may not yet be available on PyPI. Check [PyPI](https://pypi.org/project/hydrano/) for the latest status or follow the steps below to install from source.

### Installing from Source

To install Hydrano as a package from the repository:

1. Clone the repository (if not already done):

   ```bash
   git clone https://github.com/independenceee/hydrano.git
   cd hydrano
   ```

2. Install the package locally:

   ```bash
   pip install .
   ```

   This installs Hydrano into your Python environment, making it available as a module (`import hydrano`).

### Building the Package

To create a distributable package (e.g., for sharing or publishing to PyPI):

1. Ensure you have `build` installed:

   ```bash
   pip install build
   ```

2. Build the package:

   ```bash
   python -m build
   ```

   This generates `dist/` folder containing `.tar.gz` and `.whl` files.

3. Install the built package locally (optional):

   ```bash
   pip install dist/hydrano-*.whl
   ```

### Publishing to PyPI (For Maintainers)

If you are the project maintainer and wish to publish Hydrano to PyPI:

1. Ensure you have a PyPI account and `twine` installed:

   ```bash
   pip install twine
   ```

2. Upload the package to PyPI:

   ```bash
   twine upload dist/*
   ```

   You will need PyPI credentials configured in `~/.pypirc` or provided via the command line.

### Usage Example with Pip

After installing via Pip, you can use Hydrano in your Python projects:

```python
from hydrano import HydraClient

# Initialize a Hydra client
client = HydraClient(node_url="ws://localhost:4000")

# Create a Hydra Head
head_id = client.create_head(participants=["addr1...", "addr2..."])

# Submit a transaction
tx_id = client.submit_transaction(head_id, {"from": "addr1...", "to": "addr2...", "amount": 100})

# Close the Head
client.close_head(head_id)

print(f"Transaction {tx_id} submitted to head {head_id}")
```

---

## 📁 Project Structure

Hydrano follows a clean, modular structure for maintainability:

- **`src/hydrano/`** — Core toolkit code
  - `client.py`: Main HydraClient class for node interactions.
  - `head.py`: Utilities for creating and managing Hydra Heads.
  - `transaction.py`: Functions for building and submitting off-chain transactions.
  - `utils.py`: Helpers for address validation, signature handling, and logging.
- **`examples/`** — Sample scripts
  - `basic_head.py`: Demonstrates creating and closing a Hydra Head.
  - `tip_transaction.py`: Example of a micropayment transaction.
- **`tests/`** — Unit and integration tests
  - Uses `pytest` for testing client and transaction logic.
- **`docs/`** — Documentation
  - API reference and setup guides.
- **Root Files**:
  - `README.md`: Project overview (this file).
  - `requirements.txt`: Python dependencies.
  - `pyproject.toml`: Package configuration for Pip.
  - `LICENSE`: MIT License.
  - `.env.example`: Template for environment configuration.

---

## 🧑‍💻 Developer Notes

- **Hydra Workflow**: Users commit funds to a Hydra Head on Layer-1, perform off-chain transactions, and close the Head to settle on Layer-1. Hydrano abstracts this process into simple API calls.
- **Extending Hydrano**: Add custom transaction validators in `src/hydrano/validators/`. Integrate additional blockchain APIs via `src/hydrano/connectors/`.
- **Performance**: Hydra supports >1,000 TPS per Head. Benchmark with scripts in `examples/benchmarks/`.
- **Security**: Hydrano uses Cardano’s contestable commit mechanism to prevent double-spending. Always validate wallet signatures before submitting transactions.
- **Testing**: Run `pytest` for unit tests. Add new tests in `tests/` for custom features.
- **Packaging**: The `pyproject.toml` file is configured for modern Python packaging. Update version numbers before building new releases.

For advanced usage, consult the [Hydra RFCs](https://github.com/cardano-scaling/hydra) and [Cardano Developer Portal](https://developers.cardano.org/).

---

## 🤝 Contributing

Contributions are welcome to enhance Hydrano’s functionality, documentation, or performance. To contribute:

1. Fork the repository:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make changes and commit:
   ```bash
   git commit -m "Add: your feature with tests"
   ```
3. Push to your fork:
   ```bash
   git push origin feature/your-feature
   ```
4. Open a Pull Request on GitHub, referencing relevant issues.

Guidelines:

- Follow PEP 8 for Python code style.
- Include tests for new features in `tests/`.
- Discuss major changes in GitHub Issues first.
- Update `pyproject.toml` for new dependencies or version bumps.

Report bugs or suggest features via GitHub Issues. Join the Cardano community on [Discord](https://discord.com/invite/cardano) or [X](https://x.com) for collaboration.

---

## 📚 Documentation & Resources

- [API Reference](docs/api.md): Detailed documentation of Hydrano’s classes and methods.
- [Hydra Setup Guide](docs/hydra-setup.md): Instructions for configuring a Hydra node.
- Cardano Ecosystem:
  - [Cardano Developer Portal](https://developers.cardano.org/)
  - [Hydra Documentation](https://hydra.family/head-protocol/)
  - [Blockfrost API](https://blockfrost.io/)
  - [Koios API](https://koios.rest/)

---

## 📝 License

This project is licensed under the [MIT License](LICENSE). Copyright © 2025 [independenceee](https://github.com/independenceee). Free to use, modify, and distribute.
