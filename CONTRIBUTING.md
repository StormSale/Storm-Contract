# Contributing to StormSale Smart Contracts

Welcome to the **StormSale Smart Contract** development guide. Our smart contracts are built on the **Stellar Network** using **Soroban** (Rust) to power verifiable, fraud-proof affiliate marketing escrows.

---

## Prerequisites

Ensure you have the following toolchains installed:

1. **Rust**: v1.75+
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```
2. **WASM Target**:
   ```bash
   rustup target add wasm32-unknown-unknown
   ```
3. **Stellar CLI** (v21+):
   ```bash
   cargo install --locked stellar-cli --features opt
   ```

---

## Architecture Guidelines

Our smart contracts adhere to strict modular design patterns:

- `admin.rs`: Access control, administrative initialization, emergency guards.
- `campaign.rs`: Budget escrow locking, campaign lifecycle management.
- `affiliate.rs`: Sale logging verification, commission audit, and payouts.
- `storage.rs`: Persistent/Instance storage abstractions and data schemas.
- `errors.rs`: Strict, descriptive error definitions.
- `lib.rs`: Stateless facade exposing Soroban contract functions.

### Security Principles:
- **No Unsafe Code**: `#![no_std]` compliance without unchecked memory operations.
- **Strict Budget Verification**: All commission transfers must be bounded by the campaign escrow balance.
- **Access Control**: Role verification (`admin`, `advertiser`, `affiliate`) must be explicitly enforced before any state modification.

---

## Building and Compiling

```bash
# Compile to WebAssembly
cargo build --target wasm32-unknown-unknown --release

# Optimize WASM size
stellar contract optimize --wasm target/wasm32-unknown-unknown/release/stormsale.wasm
```

---

## Pull Request Guidelines

1. Format code using `cargo fmt --check`.
2. Run `cargo clippy --all-targets` to ensure zero linter warnings.
3. Every new smart contract function must include clear doc comments explaining arguments, permissions, and event emissions.
