# Smart Contract Security Policy

## 🛡 Overview

The StormSale protocol operates on the **Stellar network using Soroban WebAssembly (WASM) smart contracts**. Because smart contracts manage cryptographic escrow, affiliate commission settlements, and user authorization immutable on-ledger, security is the foundation of our engineering lifecycle.

This policy outlines our smart contract scope, threat model, severity classification, testing requirements, and responsible disclosure procedures.

---

## 📦 Scope of Smart Contracts

This policy explicitly covers all Soroban smart contract logic located in `contracts/stormsale`:

| Module | Purpose & Entry Points |
| :--- | :--- |
| **`admin.rs`** | Protocol initialization, admin transfer (`set_admin`), role-based access control (`set_role`, `get_role`), and emergency pause controls (`emergency_pause`, `unpause`). |
| **`campaign.rs`** | Campaign escrow lifecycle (`create_campaign`), budget bounds enforcement, commission rate validation (1%–50%), and clearing period settings. |
| **`sale.rs`** | Conversion tracking (`log_sale`), cryptographic referral verification, commission accounting deduction, and settlement claims (`claim_payout`). |
| **`storage.rs`** | On-chain ledger state structures, instance storage, and persistent storage management. |

---

## 🔒 Smart Contract Threat Model & Invariants

StormSale enforces strict mathematical and architectural invariants to ensure total contract solvency and security:

### 1. Mandatory Caller Authentication (`require_auth`)
- Every state-mutating entry point mandates cryptographic authorization from the appropriate stakeholder:
  - Admin functions require `admin.require_auth()`.
  - Campaign creation requires `advertiser.require_auth()`.
  - Sale conversion logging requires `advertiser.require_auth()`.
  - Payout claims require `affiliate.require_auth()`.
- Unauthorized or spoofed caller addresses immediately panic and revert the transaction.

### 2. Escrow Solvency & Zero-Deficit Invariant
- **Budget Capping**: Escrow allocations are locked upfront upon campaign creation.
- **Deficit Prevention**: Commission settlements cannot exceed remaining escrow budgets under any circumstances. If requested commission $> \text{remaining\_budget}$, execution halts.
- **Commission Rate Bounds**: Commission rates are strictly restricted to the valid range ($100 \le \text{rate} \le 5000$ basis points, corresponding to $1\%$ to $50\%$).

### 3. Arithmetic Overflow & Underflow Protection
- Contracts are compiled with `overflow-checks = true` enabled in `Cargo.toml`.
- All monetary amounts use 128-bit signed integers (`i128`) with checked mathematical operations to completely eliminate integer wrap-around vulnerabilities.

### 4. Reentrancy & Cross-Contract Security
- Soroban executes contracts within an isolated WASM sandbox.
- State updates follow the checks-effects-interactions pattern to prevent state desynchronization.

### 5. Emergency Circuit Breaker (Killswitch)
- The admin holds the capability to trigger `emergency_pause` in the event of an active exploit or anomaly.
- While paused, all new campaign creation, sale logging, and payout claims are instantly suspended.
- Once verified safe, `unpause` restores standard operation.

---

## 🚨 Reporting a Smart Contract Vulnerability

If you discover a vulnerability or potential exploit affecting the Soroban smart contracts, please notify us immediately through **coordinated responsible disclosure**.

### ⚠️ DO NOT EXPLOIT
Do not attempt to drain, grief, or exploit contracts deployed on Stellar Testnet or Mainnet. Test proof-of-concepts only within the Soroban local test environment (`soroban-sdk` test utilities with `Env::default()`).

### 📬 Emergency Contacts
- **Primary Security Email**: `security@stormsale.io`
- **Lead Maintainer**: `abujulaybeeb08@gmail.com`
- **Emergency Telegram**: `@AJDEV_Official`
- **GitHub Security Advisories**: Submit a private vulnerability advisory via the **Security** tab of `Storm-Contract`.

### 📋 Report Requirements
1. Clear description of the vulnerability.
2. Exact function(s) and lines of code affected in `contracts/stormsale/src/`.
3. Reproducible Rust test case using `#[test]` and `soroban_sdk::Env` demonstrating the exploit or state corruption.
4. Suggested patch or remediation logic.

---

## ⏱️ Response Timelines & SLA

| Phase | SLA | Action |
| :--- | :--- | :--- |
| **Emergency Triage** | **Within 12 hours** | Initial acknowledgment and review by contract maintainer. |
| **Severity Verification** | **Within 24 hours** | Replication using local Soroban test environment. |
| **Mitigation / Pause** | **Immediate** | Execution of `emergency_pause` on-chain if funds are at active risk. |
| **Hotfix & Deployment** | **Within 72 hours** | Patch development, formal test verification, and coordinated redeployment. |

---

## ⚖️ Web3 Severity Classification

| Severity | Impact on Stellar Ledger |
| :--- | :--- |
| **Critical** | Direct theft or unauthorized drain of escrowed user funds; permanent contract bricking or freezing of unaffected user assets without recourse. |
| **High** | Temporary freeze of escrowed funds beyond the clearing period; unauthorized privilege escalation to admin role; evasion of commission rate limits. |
| **Medium** | Griefing attacks that consume excess ledger storage rent without financial gain; unhandled panics that revert valid user transactions under edge cases. |
| **Low / Informational** | Misleading contract event emissions; non-exploitable gas inefficiencies; minor documentation or typing inconsistencies. |
