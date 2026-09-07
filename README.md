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
| `init` | Deployer | `admin: Address, token: Address` | Initializes contract with admin and settlement token. |
| `grant_role` | Admin | `account: Address, role: RoleType` | Authorizes an Advertiser or Affiliate address. |
| `create_campaign` | Advertiser | `advertiser: Address, budget: i128, rate_bps: u32` | Creates a new campaign and locks the initial budget into escrow. |
| `top_up_budget` | Advertiser | `campaign_id: u64, amount: i128` | Deposits additional funds into an existing campaign escrow. |
| `log_sale` | Merchant/API | `campaign_id: u64, affiliate: Address, sale_id: u64, amount: i128` | Records a verified conversion and calculates affiliate reward. |
| `claim_payout` | Affiliate | `sale_id: u64` | Transfers the earned commission from contract escrow to the affiliate. |

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
