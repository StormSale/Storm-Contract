# StormSale Smart Contract

This repository contains the core smart contract logic for the **StormSale** trustless affiliate marketing platform. 

StormSale is a verifiable data integrity ledger built on the **Stellar Network** using **Soroban** (Rust), designed to eliminate ad fraud and payment disputes between merchants and promoters.

## Architecture

The contract is built using a modular structure:

*   **`admin.rs`:** Handles role-based access control (Admin, Advertiser, Affiliate).
*   **`campaign.rs`:** Manages the creation of affiliate campaigns and the upfront **Campaign Budget Escrow**.
*   **`affiliate.rs`:** Manages the logging of verifiable sales and the automated claiming of commissions.
*   **`storage.rs`:** Defines the ledger data structures (`Campaign`, `Sale`) and the storage keys used by the contract.
*   **`errors.rs`:** Defines all custom error codes (e.g., `InsufficientBudget`, `Unauthorized`).
*   **`lib.rs`:** The main entry point and API gateway exposing the callable contract functions.

## The Campaign Budget Escrow Model

Unlike traditional platforms with net-30 payout delays and risk of default, StormSale uses a strict escrow model:
1. Advertisers must deposit the **full campaign budget** into the contract when creating a campaign.
2. When a sale is logged, Affiliates can claim their commission.
3. The contract mathematically verifies the sale and instantly deducts the commission from the locked budget, transferring it to the Affiliate.

## Prerequisites

To compile this contract, you need the Rust toolchain and the `wasm32-unknown-unknown` target installed.

```bash
rustup target add wasm32-unknown-unknown
```

## Compilation

The testing environment dependencies (`testutils`) have been explicitly removed to bypass a known dependency conflict in the `soroban-env-host` crate on crates.io. 

To build the final contract for deployment or for testing in the Stellar IDE, compile it directly to WebAssembly:

```bash
cargo build --target wasm32-unknown-unknown --release
```

The optimized `.wasm` file will be generated at:
`target/wasm32-unknown-unknown/release/stormsale.wasm`

## Testing (Stellar Laboratory)

You can manually test the `.wasm` binary on the [Stellar Laboratory](https://laboratory.stellar.org/):

1. Switch to the **Testnet**.
2. Upload the `stormsale.wasm` file.
3. Use a mock token (or XLM) for the escrow budget.
4. Call `init` to set the admin and token address.
5. Use `grant_role` to authorize an Advertiser and an Affiliate.
6. Have the Advertiser call `create_campaign` and log a sale.
7. Have the Affiliate call `claim_commission` to see the automated payout in real-time.
