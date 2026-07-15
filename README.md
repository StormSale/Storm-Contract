# StormSale Contracts

This repository contains the smart contracts for **StormSale**, built using the [Soroban SDK](https://soroban.stellar.org/) on the Stellar network.

## Project Structure

This is a Rust workspace containing the following contracts:

- `contracts/stormsale`: The main StormSale smart contract.

## Prerequisites

- [Rust](https://www.rust-lang.org/tools/install) (latest stable version)
- Target `wasm32-unknown-unknown` installed:
  ```bash
  rustup target add wasm32-unknown-unknown
  ```
- [Soroban CLI](https://soroban.stellar.org/docs/getting-started/setup#install-the-soroban-cli) installed.

## Building

To build the contracts into WebAssembly (`.wasm`), run from the root of the repository:

```bash
cargo build --target wasm32-unknown-unknown --release
```

The compiled `.wasm` files will be located in `target/wasm32-unknown-unknown/release/`.

## Testing

To run the unit tests for the contracts:

```bash
cargo test
```

## Deployment

Refer to the Soroban CLI documentation for instructions on how to [deploy](https://soroban.stellar.org/docs/getting-started/deploy-to-testnet) and interact with the contract on the Stellar network (Testnet or Mainnet).
