<div align="center">
  <h1>⚡ StormSale Soroban Smart Contract</h1>
  <p><strong>Trustless On-Chain Affiliate Marketing & Campaign Budget Escrow on Stellar</strong></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Soroban](https://img.shields.io/badge/Soroban-v22+-purple?logo=stellar)](https://soroban.stellar.org/)
[![Rust](https://img.shields.io/badge/Rust-1.75+-orange?logo=rust)](https://www.rust-lang.org/)
[![Stellar Network](https://img.shields.io/badge/Network-Stellar%20Testnet-black?logo=stellar)](https://stellar.org/)
[![CI](https://github.com/StormSale/Storm-Contract/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
</div>

<br />

## 📖 Overview

The **StormSale Smart Contract** provides a decentralized, fraud-resistant escrow mechanism for affiliate marketing campaigns on the **Stellar Network**. Built on **Soroban** using Rust (`#![no_std]`), it mathematically guarantees:

1. **Merchant Escrow Protection:** Advertisers lock an upfront budget into the contract when launching campaigns.
2. **Instant Commission Settlement:** Affiliates claim their rewards automatically upon verified conversion, with funds transferred directly from the campaign escrow.
3. **Dispute Elimination:** No net-30 payout delays, chargeback tampering, or tracking discrepancies.

---

## 🏗️ Architecture & Modules

The contract follows an enterprise modular separation of concerns:

```text
contracts/stormsale/src/
├── lib.rs          # API Facade & Public Soroban Interface
├── admin.rs        # Administrative initialization and RBAC security guards
├── campaign.rs     # Campaign creation and escrow budget management
├── affiliate.rs    # Verifiable sale logging and instant payout distribution
├── storage.rs      # Storage keys, Campaign and Sale struct definitions
└── errors.rs       # Canonical error enums
```

### Module Responsibilities

| File | Purpose | Security Enforcement |
| :--- | :--- | :--- |
| `admin.rs` | Protocol governance | `require_auth` on admin address; role management |
| `campaign.rs` | Upfront escrow locking | Deposits tokens into contract address upon campaign creation |
| `affiliate.rs` | Verified conversions | Verifies remaining budget >= commission before settlement |
| `storage.rs` | Ledger state abstraction | Persistent & Instance storage isolation |
| `errors.rs` | Safe error handling | Explicit enum codes preventing silent reverts |

---

## ⚙️ Contract Interface & Function Reference

| Function | Caller Role | Parameters | Description |
| :--- | :--- | :--- | :--- |
| `init` | Admin | `admin: Address, token: Address` | Initializes contract with admin and SAC token address. |
| `grant_role` | Admin | `target: Address, role: RoleType` | Grants Advertiser, Affiliate, or Auditor role to an address. |
| `create_campaign` | Advertiser | `advertiser: Address, commission_rate: u32, clearing_period: u32, budget: i128` | Creates campaign and locks upfront budget tokens into escrow. |
| `top_up_budget` | Advertiser | `advertiser: Address, campaign_id: u32, amount: i128` | Deposits additional budget tokens into an active campaign escrow. |
| `refund_escrow` | Advertiser | `advertiser: Address, campaign_id: u32` | Reclaims unspent escrow budget, refunds tokens, and closes campaign. |
| `log_sale` | Advertiser | `advertiser: Address, campaign_id: u32, affiliate: Address, amount: i128` | Records conversion, deducts commission from escrow, sets clearing timer. |
| `audit_sale` | Auditor | `auditor: Address, campaign_id: u32, affiliate: Address` | Cryptographically approves a logged conversion for commission payout. |
| `claim_payout` | Affiliate | `affiliate: Address, campaign_id: u32` | Releases cleared, audited commission tokens from escrow to affiliate. |
| `get_campaign` | Any | `campaign_id: u32` | Returns campaign metadata, remaining budget, and active status. |
| `get_sale` | Any | `campaign_id: u32, affiliate: Address` | Returns recorded sale details, commission, audit status, and claim state. |

---

## 🧪 Testing & Verification

The test suite runs with native Soroban SDK test utilities and mocks Stellar Asset Contracts (SAC):

```bash
# Run all unit tests
cargo test --manifest-path contracts/stormsale/Cargo.toml
```

---

## 🚀 Building & Compilation

### Prerequisites
- [Rust & Cargo](https://www.rust-lang.org/tools/install) (v1.75+)
- WebAssembly target: `wasm32-unknown-unknown`
- [Stellar CLI](https://developers.stellar.org/docs/tools/developer-tools): `cargo install --locked stellar-cli --features opt`

```bash
# Add WASM target
rustup target add wasm32-unknown-unknown

# Build release binary
cargo build --target wasm32-unknown-unknown --release
```

The compiled WebAssembly binary will be output to:
`target/wasm32-unknown-unknown/release/stormsale.wasm`

---

## 🧪 Deployment to Stellar Testnet

```bash
# 1. Configure Stellar Testnet Identity
stellar keys generate --network testnet alice

# 2. Deploy the optimized contract WASM
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/stormsale.wasm \
  --source alice \
  --network testnet
```

---

## 👥 Maintainers

| Avatar | Name / Role | GitHub | Contact |
| :---: | :---: | :---: | :---: |
| <img src="https://github.com/AbuJulaybeeb.png" width="80" style="border-radius:50%" /> | **Jibril Raji Qasim (AJDEV)**<br/>*Lead Smart Contract & Backend Developer* | [@AbuJulaybeeb](https://github.com/AbuJulaybeeb) | [Telegram](https://t.me/AJDEV_Official) |

---

## 🤝 Contributing & Security

- Review our [CONTRIBUTING.md](CONTRIBUTING.md) for style and PR standards.
- Review our [SECURITY.md](SECURITY.md) for responsible disclosure guidelines.

---

## 📄 License

This contract is open-source software licensed under the [MIT License](LICENSE).
