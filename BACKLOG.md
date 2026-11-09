# ⚡ StormSale Smart Contract: Production Backlog & Issue Roadmap

> **Live GitHub Issue Tracker:** [StormSale/Storm-Contract Issues](https://github.com/StormSale/Storm-Contract/issues)

This document provides the canonical tracking backlog for all **107 production issues** on the StormSale Soroban smart contracts. Every issue is categorized with required Drips milestone tags, complexity tiers, and full technical specifications.

## 📊 Summary by Complexity

| Classification | Tag | Count | Status |
| :--- | :--- | :--- | :--- |
| **Total Open Issues** | `contract` | **107** | Open for Contribution |
| **Drips Eligible** | `Drips` | **106** | Bounty Milestone |
| **High Complexity** | `complexity: high` | **30** | Protocol Core & Cryptography |
| **Medium Complexity** | `complexity: medium` | **45** | State Machine & Integration |
| **Low Complexity** | `complexity: low` | **31** | Entrypoints, Queries & CLI |

---

## 📋 Backlog Catalog

### [#1: feat(contracts): Implement Soroban State TTL Auto-Bump Strategy for Persistent Escrows](https://github.com/StormSale/Storm-Contract/issues/1)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/1
- **Labels:** `enhancement`, `contract`

### Problem Statement
In Soroban (Protocol 20+), state entries incur ledger rent and expire if their Time-To-Live (TTL) is not extended. Long-running affiliate campaigns or unclaimed affiliate commissions risk being archived.
### Proposed Solution
- Add explicit extend_ttl entry points to the contract.
- Automatically bump storage entry TTL whenever log_sale or claim_commission is called.

---

### [#9: feat(escrow): support arbitrary SAC stablecoins (USDC/EURC) in campaign budget escrows](https://github.com/StormSale/Storm-Contract/issues/9)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/9
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`, `stellar-ecosystem`

### User Story
As an advertiser, I want to fund campaign budget escrows in SAC-wrapped USDC and EURC tokens so that affiliate payouts settle in stable currencies.

### Technical Specification
- Store supported asset addresses in instance storage under `DataKey::SupportedAsset(Address)`.
- Update `create_campaign` to accept `token_address: Address` alongside budget.
- Validate that the specified token is either native XLM or a whitelisted SAC asset contract.
- Transfer tokens via `soroban_sdk::token::Client::new(&env, &token_address)`.

### Acceptance Criteria
- [ ] `DataKey::SupportedAsset(Address)` mapping implemented in `storage.rs`.
- [ ] Admin method `set_token_whitelisted(token: Address, enabled: bool)` added.
- [ ] `create_campaign` verifies token whitelist status.
- [ ] Unit tests verify deposits and payouts in non-native SAC assets.

---

### [#10: feat(escrow): enforce minimum escrow deposit threshold per asset class to prevent spam campaigns](https://github.com/StormSale/Storm-Contract/issues/10)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/10
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`, `stellar-ecosystem`

### User Story
As an ecosystem maintainer, I want campaigns to require a minimum deposit threshold per asset class (e.g. 50 XLM, 10 USDC) so that spam or zero-value campaigns do not pollute the contract state.

### Technical Specification
- Define `MIN_BUDGET_XLM` and asset-specific threshold mapping in `storage.rs`.
- Validate `budget >= min_budget` during `create_campaign`.
- Return `Error::BudgetBelowMinimum` if threshold is not satisfied.

### Acceptance Criteria
- [ ] Asset minimum thresholds configured in storage.
- [ ] `create_campaign` rejects budget below threshold with explicit error.
- [ ] Unit tests cover rejection and boundary conditions.

---

### [#11: feat(escrow): add safe math wrapper module for i128 decimal conversions across diverse SAC decimals](https://github.com/StormSale/Storm-Contract/issues/11)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/11
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`, `stellar-ecosystem`

### User Story
As a contract engineer, I want safe decimal normalization between 7-decimal XLM and arbitrary SAC tokens (e.g. 6-decimal USDC) so that rounding errors and truncation exploits are prevented.

### Technical Specification
- Create `math.rs` module with `checked_mul_div` and decimal scaling functions.
- Implement basis point commission math with checked arithmetic.
- Reject operations that overflow `i128::MAX` or lose precision.

### Acceptance Criteria
- [ ] Safe math module implemented with zero panics.
- [ ] Multi-decimal scaling unit tests pass.
- [ ] Overflow/underflow assertions verified.

---

### [#12: feat(escrow): implement asset balance reconciliation query for campaign budgets](https://github.com/StormSale/Storm-Contract/issues/12)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/12
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As an auditor, I want to query the total escrowed balance per asset across all active campaigns to reconcile contract token reserves with total campaign obligations.

### Technical Specification
- Track `TotalEscrowed(Address)` in instance storage.
- Update counter on `create_campaign`, `top_up_budget`, `refund_escrow`, and `claim_payout`.
- Expose `get_total_escrowed(token: Address) -> i128`.

### Acceptance Criteria
- [ ] `TotalEscrowed` tracked in storage.
- [ ] Invariant holds: total token balance >= total escrowed.
- [ ] Public query endpoint tested.

---

### [#13: feat(escrow): add fee-on-transfer asset detection and safety guards](https://github.com/StormSale/Storm-Contract/issues/13)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/13
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As a protocol architect, I want the contract to verify the actual received token amount during transfers so that fee-on-transfer or deflationary tokens do not cause escrow accounting insolvency.

### Technical Specification
- Query contract balance before and after `client.transfer` in `create_campaign` and `top_up_budget`.
- Credit only the net received amount to `campaign.budget`.
- Revert if received amount is less than expected without explicit tolerance.

### Acceptance Criteria
- [ ] Balance delta checked on budget deposits.
- [ ] Discrepancies cause `Error::TransferAmountMismatch`.
- [ ] Unit tests verify net balance crediting.

---

### [#14: feat(escrow): implement dynamic asset whitelist and deprecation management by Admin](https://github.com/StormSale/Storm-Contract/issues/14)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/14
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `stellar-ecosystem`

### User Story
As a platform admin, I want to whitelist new Stellar asset contracts (SAC) and deprecate decommissioned tokens so that the platform can expand asset support safely.

### Technical Specification
- Add `set_asset_status(admin: Address, token: Address, enabled: bool)` entrypoint.
- Store asset status under `DataKey::AssetStatus(Address)`.
- Ensure deprecated assets allow existing campaigns to refund/claim but block new campaign creation.

### Acceptance Criteria
- [ ] Admin can enable/disable asset contracts.
- [ ] Deprecated assets permit claim/refund but block `create_campaign`.
- [ ] Role authorization verified.

---

### [#15: feat(oracle): add SEP-0040 price oracle interface for real-time XLM/USD conversion rates](https://github.com/StormSale/Storm-Contract/issues/15)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/15
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`, `stellar-ecosystem`

### User Story
As an advertiser, I want to set campaign budgets in USD terms resolved on-chain via a SEP-0040 compliant price oracle so that fiat-pegged affiliate campaigns remain stable against XLM volatility.

### Technical Specification
- Define `PriceOracleClient` interface matching SEP-0040 / Reflector specifications.
- Store oracle contract address in admin instance storage.
- Add entrypoint to convert requested USD budget to stroops at time of deposit.

### Acceptance Criteria
- [ ] Oracle contract interface defined.
- [ ] Mock oracle test verifies conversion rate lookup.
- [ ] Stale price checks revert with `Error::OraclePriceStale`.

---

### [#16: feat(escrow): implement multi-currency campaign budget tracking in storage](https://github.com/StormSale/Storm-Contract/issues/16)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/16
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a developer, I want campaign storage structs to record the token address alongside the budget amount so that multi-currency campaigns operate concurrently.

### Technical Specification
- Update `Campaign` struct in `storage.rs` with `token: Address` field.
- Migrate persistent storage deserialization to support versioned campaign records.
- Ensure `claim_payout` routes transfers through the specific campaign's token client.

### Acceptance Criteria
- [ ] `Campaign.token` field persisted.
- [ ] `claim_payout` transfers tokens of the specific campaign asset.
- [ ] Multi-token concurrent tests pass.

---

### [#17: feat(escrow): add emergency asset recovery function for accidentally sent unsupported tokens](https://github.com/StormSale/Storm-Contract/issues/17)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/17
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a platform admin, I want an emergency sweep function to recover tokens erroneously sent to the contract address that are not part of any campaign escrow.

### Technical Specification
- Add `emergency_recover_tokens(admin: Address, token: Address, recipient: Address, amount: i128)`.
- Enforce `admin.require_auth()`.
- Calculate unallocated surplus = `token_client.balance(&contract) - total_escrowed(token)`.
- Restrict withdrawal to surplus only.

### Acceptance Criteria
- [ ] Only unallocated surplus can be swept.
- [ ] Escrowed campaign funds cannot be touched.
- [ ] Admin auth enforced.

---

### [#18: feat(escrow): support token allowance pre-authorization pattern alongside direct transfers](https://github.com/StormSale/Storm-Contract/issues/18)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/18
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `stellar-ecosystem`

### User Story
As an advertiser, I want to deposit escrow funds via `transfer_from` using pre-approved SAC token allowances so that smart wallets and automated contracts can fund campaigns seamlessly.

### Technical Specification
- Implement `create_campaign_with_allowance` and `top_up_with_allowance`.
- Utilize `client.transfer_from(&contract, &advertiser, &contract, &amount)`.
- Handle allowance expiration errors gracefully.

### Acceptance Criteria
- [ ] `transfer_from` flow implemented for SAC tokens.
- [ ] Insufficient allowance reverts with clear error.
- [ ] Allowance deposit tested with mock SAC.

---

### [#19: feat(escrow): implement automated escrow deficit alert event when budget falls below threshold](https://github.com/StormSale/Storm-Contract/issues/19)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/19
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As an advertiser, I want the smart contract to emit an `escrow_low` event when a campaign's remaining budget falls below 20% of its initial budget so that automated bots can trigger a top-up.

### Technical Specification
- Store `initial_budget` in `Campaign` struct.
- In `log_sale`, calculate remaining percentage.
- If `remaining <= initial_budget / 5`, emit `("camp", symbol_short!("low_esc"))` event.

### Acceptance Criteria
- [ ] `initial_budget` tracked in `Campaign`.
- [ ] Event emitted when budget crosses low watermark.
- [ ] Unit test asserts event emission.

---

### [#20: feat(escrow): add fractional payout precision rounding guardrails for micro-commissions](https://github.com/StormSale/Storm-Contract/issues/20)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/20
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an affiliate, I want commission division to never round to 0 stroops on low-value sales so that micro-conversions are fairly compensated without truncation.

### Technical Specification
- In commission calculation: `if commission == 0 && sale_amount > 0 { return Err(Error::CommissionTooSmall); }`.
- Document minimum commissionable sale amounts for given basis points.

### Acceptance Criteria
- [ ] Zero-commission truncation rejected.
- [ ] Explicit error `CommissionTooSmall` returned.
- [ ] Boundary tests pass.

---

### [#21: feat(escrow): support tiered budget deposit milestones with progressive unlocking](https://github.com/StormSale/Storm-Contract/issues/21)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/21
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As an advertiser, I want to deposit escrow in progressive tranches released upon affiliate sales milestones so that working capital is managed efficiently.

### Technical Specification
- Add `TrancheConfig { milestone_volume: i128, release_amount: i128 }` to storage.
- Auto-unlock subsequent tranches when cumulative sales reach milestone volume.
- Emit milestone unlock events.

### Acceptance Criteria
- [ ] Tranche data structures implemented.
- [ ] Progressive unlock tested across multi-stage sales.
- [ ] Unearned tranches remain refundable.

---

### [#22: feat(escrow): add multi-asset campaign budget breakdown query](https://github.com/StormSale/Storm-Contract/issues/22)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/22
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a frontend integrator, I want an endpoint returning campaign financial health (initial budget, spent, remaining, token address, asset symbol) in a single Soroban call.

### Technical Specification
- Implement `get_campaign_financials(campaign_id: u32) -> CampaignFinancials`.
- Return struct containing `budget`, `spent`, `pending_claims`, `token`.
- Extend TTL on query.

### Acceptance Criteria
- [ ] Struct `CampaignFinancials` defined.
- [ ] Public query returns accurate aggregates.
- [ ] Tested in test suite.

---

### [#23: feat(escrow): implement asset-specific maximum clearing period limit enforcement](https://github.com/StormSale/Storm-Contract/issues/23)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/23
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As an affiliate, I want clearing periods to be capped at a maximum (e.g. 30 days / 2,592,000s) so that advertisers cannot lock affiliate commissions indefinitely.

### Technical Specification
- Define `MAX_CLEARING_PERIOD = 2_592_000u32` (30 days).
- In `create_campaign`, enforce `clearing_period <= MAX_CLEARING_PERIOD`.
- Return `Error::ClearingPeriodExceedsMax` on violation.

### Acceptance Criteria
- [ ] Max clearing period constant enforced.
- [ ] Reverts when exceeding 30 days.
- [ ] Tests verify lower and upper bounds.

---

### [#24: feat(referral): store parent recruiter address relationship in persistent storage](https://github.com/StormSale/Storm-Contract/issues/24)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/24
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an affiliate, I want to register under a parent recruiter address so that our referral relationship is cryptographically recorded on the Stellar ledger.

### Technical Specification
- Add `DataKey::Recruiter(Address)` mapping affiliate to parent recruiter.
- Add entrypoint `register_recruiter(affiliate: Address, recruiter: Address)`.
- Prevent self-referral (`affiliate != recruiter`).

### Acceptance Criteria
- [ ] Recruiter mapping stored persistently.
- [ ] Self-referral rejected with `Error::InvalidRecruiter`.
- [ ] Recruiter lookup helper implemented.

---

### [#25: feat(referral): calculate automated two-tier commission split upon sale logging](https://github.com/StormSale/Storm-Contract/issues/25)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/25
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As a recruiter, I want the smart contract to automatically calculate and deduct my second-tier commission override from campaign escrow when my sub-affiliate makes a sale.

### Technical Specification
- Look up recruiter for `affiliate` in `log_sale`.
- If recruiter exists, calculate override = `(sale_amount * override_rate) / 10000`.
- Deduct `affiliate_commission + recruiter_override` from `campaign.budget`.
- Store separate `Sale` record for recruiter.

### Acceptance Criteria
- [ ] Two-tier split calculated and deducted in `log_sale`.
- [ ] Both records created in persistent storage.
- [ ] Budget reflects combined deduction.

---

### [#26: feat(referral): enforce maximum recruiter override percentage cap invariant (<= 5%)](https://github.com/StormSale/Storm-Contract/issues/26)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/26
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As an advertiser, I want recruiter override rates to never exceed 500 basis points (5%) so that campaign budgets are protected from predatory referral fee stacking.

### Technical Specification
- Define `MAX_OVERRIDE_BPS: u32 = 500`.
- In campaign/referral configuration, enforce `override_rate <= MAX_OVERRIDE_BPS`.
- Revert with `Error::OverrideRateExceedsCap` if exceeded.

### Acceptance Criteria
- [ ] Maximum cap enforced in code.
- [ ] Violations revert with explicit error.
- [ ] Unit tests verify cap validation.

---

### [#27: feat(referral): implement circular referral graph cycle detection guard](https://github.com/StormSale/Storm-Contract/issues/27)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/27
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As a security auditor, I want the contract to prevent circular referral loops (e.g. Alice recruited Bob, Bob recruits Alice) so that infinite recursive payouts are impossible.

### Technical Specification
- In `register_recruiter`, traverse recruiter ancestors up to 5 hops.
- If `target == recruiter`, return `Error::CircularReferralDetected`.
- Fail closed if cycle is found.

### Acceptance Criteria
- [ ] Cycle detection algorithm implemented.
- [ ] Loops of length 1, 2, and 3 successfully rejected.
- [ ] Verified with unit tests.

---

### [#28: feat(referral): add dedicated claim_recruiter_payout entrypoint for sub-affiliate overrides](https://github.com/StormSale/Storm-Contract/issues/28)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/28
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a recruiter, I want a dedicated entrypoint to claim my accumulated second-tier overrides independently of the primary selling affiliate.

### Technical Specification
- Add `claim_recruiter_payout(env: Env, recruiter: Address, campaign_id: u32, sub_affiliate: Address)`.
- Verify clearing period and auditor approval.
- Transfer override tokens to recruiter and mark claimed.

### Acceptance Criteria
- [ ] Independent recruiter claim entrypoint.
- [ ] Auth enforced on recruiter address.
- [ ] Token balance updated and claimed flag set.

---

### [#29: feat(referral): emit specialized two-tier commission split event on verified conversion](https://github.com/StormSale/Storm-Contract/issues/29)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/29
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As an indexer, I want specialized events emitted when a two-tier commission is logged so that off-chain explorers can visualize the referral network tree.

### Technical Specification
- Emit `("referral", symbol_short!("split"))` with topics `(campaign_id, affiliate, recruiter)` and data `(direct_comm, override_comm)`.
- Document event schema in README.

### Acceptance Criteria
- [ ] Event emitted on two-tier sale logging.
- [ ] Direct and override amounts included.
- [ ] Snapshot test asserts event structure.

---

### [#30: feat(referral): implement recruiter address revocation and reassignment by admin/advertiser](https://github.com/StormSale/Storm-Contract/issues/30)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/30
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an advertiser, I want the ability to reassign or revoke an abusive recruiter relationship with proper authorization.

### Technical Specification
- Add `reassign_recruiter(env: Env, caller: Address, affiliate: Address, new_recruiter: Address)`.
- Require Advertiser or Admin authorization.
- Update storage key `DataKey::Recruiter(affiliate)`.

### Acceptance Criteria
- [ ] Reassignment restricted to authorized roles.
- [ ] Reassigned recruiter applies to future sales.
- [ ] Existing pending claims remain untouched.

---

### [#31: feat(referral): add aggregate sub-affiliate volume tracking per recruiter address](https://github.com/StormSale/Storm-Contract/issues/31)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/31
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a recruiter, I want to query the total sales volume generated by my direct sub-affiliates to assess team performance.

### Technical Specification
- Track `RecruiterVolume(Address)` in persistent storage.
- Increment volume upon successful `log_sale`.
- Expose query `get_recruiter_volume(recruiter: Address) -> i128`.

### Acceptance Criteria
- [ ] Cumulative volume tracked accurately.
- [ ] Query returns correct sum across sub-affiliates.
- [ ] Unit tests pass.

---

### [#32: feat(referral): enforce strict 2-tier maximum tree depth invariant in storage](https://github.com/StormSale/Storm-Contract/issues/32)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/32
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As a protocol maintainer, I want the contract to enforce a strict maximum depth of 2 tiers so that multi-level pyramid structures are structurally prohibited.

### Technical Specification
- Store recruiter depth metadata on registration.
- If recruiter already has a parent, disallow third-level override deductions.
- Return `Error::MaxReferralDepthExceeded`.

### Acceptance Criteria
- [ ] Depth limited to direct recruiter only.
- [ ] Multi-tier MLM structures prevented.
- [ ] Verified with regression tests.

---

### [#33: feat(referral): implement separate escrow reserve guarantee for pending recruiter overrides](https://github.com/StormSale/Storm-Contract/issues/33)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/33
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a recruiter, I want campaign escrow accounting to reserve funds for my override so that merchant budget top-ups or refunds cannot leave my override unbacked.

### Technical Specification
- In `Campaign`, track `reserved_overrides: i128`.
- In `refund_escrow`, compute refundable amount as `budget - pending_claims - reserved_overrides`.
- Prevent refunding locked commissions.

### Acceptance Criteria
- [ ] Invariant holds: contract balance >= total pending + reserved overrides.
- [ ] Refund cannot withdraw reserved override funds.
- [ ] Accounting verified in unit tests.

---

### [#34: feat(referral): allow advertisers to set custom recruiter override rates per campaign](https://github.com/StormSale/Storm-Contract/issues/34)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/34
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an advertiser, I want to configure the recruiter override basis points at campaign creation instead of using a global protocol default.

### Technical Specification
- Add `override_rate: u32` parameter to `create_campaign`.
- Store `override_rate` in `Campaign` struct.
- Use campaign-specific rate in `log_sale` calculations.

### Acceptance Criteria
- [ ] Campaign struct stores custom override rate.
- [ ] Defaults to 0 if no override desired.
- [ ] Tested with varying campaign rates.

---

### [#35: feat(referral): add query method to inspect affiliate recruiter and override configuration](https://github.com/StormSale/Storm-Contract/issues/35)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/35
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a frontend developer, I want a query endpoint to fetch an affiliate's recruiter, override percentage, and registration timestamp in a single call.

### Technical Specification
- Implement `get_affiliate_recruiter_info(affiliate: Address) -> RecruiterInfo`.
- Return struct with `recruiter`, `override_rate`, `registered_at`.
- Handle unrecruited affiliates cleanly.

### Acceptance Criteria
- [ ] `RecruiterInfo` struct returned.
- [ ] Returns empty/None for organic affiliates.
- [ ] Query tested in unit suite.

---

### [#36: feat(referral): support grace period for recruiter claims after campaign closure](https://github.com/StormSale/Storm-Contract/issues/36)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/36
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a recruiter, I want a 14-day grace period after campaign closure to claim all earned overrides before remaining funds are fully liquidated.

### Technical Specification
- Store `closed_at: Option<u64>` on campaign closure/refund.
- Allow `claim_recruiter_payout` during grace period.
- Revert claim attempts only after grace period expires.

### Acceptance Criteria
- [ ] Grace period timestamp verified.
- [ ] Claims succeed during grace period.
- [ ] Claims rejected after expiration with `Error::GracePeriodExpired`.

---

### [#37: feat(referral): implement batch recruiter override claim method](https://github.com/StormSale/Storm-Contract/issues/37)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/37
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As a large recruiter, I want to claim overrides across multiple sub-affiliates and campaigns in a single transaction to reduce fee overhead.

### Technical Specification
- Add `batch_claim_recruiter_payouts(env: Env, recruiter: Address, claims: Vec<(u32, Address)>)`.
- Iterate through `(campaign_id, sub_affiliate)` tuples.
- Consolidate token transfers into a single aggregate payment.

### Acceptance Criteria
- [ ] Vector of claims processed in single call.
- [ ] Consolidated token transfer executed.
- [ ] Partial failure handling tested.

---

### [#38: feat(referral): add recruiter tier performance ranking and multiplier logic](https://github.com/StormSale/Storm-Contract/issues/38)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/38
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As an ecosystem manager, I want recruiters who drive over 50,000 XLM in verified volume to earn a 1.2x bonus multiplier on overrides funded from protocol incentives.

### Technical Specification
- Define performance tiers based on `RecruiterVolume`.
- Apply bonus multiplier if recruiter qualifies for VIP tier.
- Cap total override within protocol limits.

### Acceptance Criteria
- [ ] Tier qualification logic verified.
- [ ] Multiplier applied only to eligible recruiters.
- [ ] Verified in test suite.

---

### [#39: feat(batch): implement log_batch_sales_merkle for bulk off-chain conversion roots](https://github.com/StormSale/Storm-Contract/issues/39)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/39
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`, `stellar-ecosystem`

### User Story
As an advertiser processing thousands of daily sales, I want to anchor a 32-byte Merkle root of sales on Soroban rather than submitting thousands of individual ledger transactions.

### Technical Specification
- Add `log_batch_sales_merkle(advertiser: Address, campaign_id: u32, merkle_root: BytesN<32>, total_commissions: i128, sale_count: u32)`.
- Deduct `total_commissions` from campaign budget upfront into batch escrow.
- Store root under `DataKey::BatchRoot(campaign_id, batch_id)`.

### Acceptance Criteria
- [ ] Merkle root stored in persistent storage.
- [ ] Budget deducted and batch escrow reserved.
- [ ] Event emitted with batch ID and root.

---

### [#40: feat(batch): implement Merkle proof verification for individual commission claims](https://github.com/StormSale/Storm-Contract/issues/40)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/40
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`, `stellar-ecosystem`

### User Story
As an affiliate included in a batch sale, I want to submit a cryptographic Merkle proof to claim my commission directly against the on-chain root.

### Technical Specification
- Implement `claim_merkle_payout(affiliate: Address, campaign_id: u32, batch_id: u32, amount: i128, proof: Vec<BytesN<32>>)`.
- Verify leaf hash matches Merkle root using sha256.
- Enforce double-spend protection via leaf nullifier bitmap.

### Acceptance Criteria
- [ ] Cryptographic Merkle proof verifier passes.
- [ ] Double-claim prevention nullifier verified.
- [ ] Payout transferred to affiliate.

---

### [#41: feat(batch): implement batch_claim_payouts for claiming multiple sales in one transaction](https://github.com/StormSale/Storm-Contract/issues/41)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/41
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an affiliate with sales across multiple campaigns, I want to claim all cleared payouts in one atomic transaction to minimize wallet interactions.

### Technical Specification
- Add `batch_claim_payouts(affiliate: Address, campaign_ids: Vec<u32>)`.
- Loop through campaigns, verify auditor approval and clearing period.
- Transfer aggregated commission in a single token transfer.

### Acceptance Criteria
- [ ] Vector of campaign IDs processed.
- [ ] Single consolidated token transfer executed.
- [ ] All sales marked claimed atomically.

---

### [#42: feat(batch): optimize Soroban read/write footprint for multi-sale settlements](https://github.com/StormSale/Storm-Contract/issues/42)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/42
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a protocol developer, I want batch methods to use compact footprints so that transaction simulation fees remain well within Stellar ledger resource limits.

### Technical Specification
- Refactor storage keys to group related campaign metrics into composite entries.
- Profile Soroban CPU instructions and RAM usage for 10, 25, and 50 claims.
- Document ledger footprint footprints.

### Acceptance Criteria
- [ ] Footprint reduction verified via simulation.
- [ ] Gas/fee benchmarks documented in README.
- [ ] Resource limits respected.

---

### [#43: feat(batch): add batch campaign status toggle (pause/resume multiple campaigns)](https://github.com/StormSale/Storm-Contract/issues/43)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/43
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As an enterprise advertiser managing 20+ campaigns, I want to pause or resume multiple campaigns simultaneously in an emergency.

### Technical Specification
- Implement `batch_set_campaign_status(advertiser: Address, campaign_ids: Vec<u32>, active: bool)`.
- Verify caller owns all specified campaigns.
- Update active flags and emit batch status event.

### Acceptance Criteria
- [ ] Batch toggle entrypoint implemented.
- [ ] Ownership verified across all IDs.
- [ ] Event emitted with updated IDs.

---

### [#44: feat(batch): add batch_top_up_budget for multi-campaign advertisers](https://github.com/StormSale/Storm-Contract/issues/44)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/44
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an advertiser, I want to replenish budgets across multiple campaigns with varying amounts in one transaction.

### Technical Specification
- Add `batch_top_up_budget(advertiser: Address, topups: Vec<(u32, i128)>)`.
- Calculate total sum, execute single transfer from advertiser.
- Increment budgets of respective campaigns.

### Acceptance Criteria
- [ ] Single token transfer for total sum.
- [ ] Individual campaign budgets incremented correctly.
- [ ] Reverts atomically if any campaign ID invalid.

---

### [#45: feat(batch): implement batch auditor approvals using bitfield verification](https://github.com/StormSale/Storm-Contract/issues/45)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/45
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an auditor, I want to approve up to 64 logged conversions in a single operation using an encoded bitfield to streamline compliance reviews.

### Technical Specification
- Add `batch_audit_sales(auditor: Address, campaign_id: u32, affiliates: Vec<Address>)`.
- Enforce Auditor role.
- Batch-update `approved_by_auditor = true`.

### Acceptance Criteria
- [ ] Auditor role verified once per batch.
- [ ] Multiple sales approved atomically.
- [ ] Audit event emitted.

---

### [#46: feat(batch): support EIP-712 / SEP-style off-chain signed conversion vouchers](https://github.com/StormSale/Storm-Contract/issues/46)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/46
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`, `stellar-ecosystem`

### User Story
As a merchant with an e-commerce backend, I want to issue Ed25519-signed conversion vouchers so that affiliates can submit and log their own sales trustlessly.

### Technical Specification
- Add `log_sale_with_voucher(affiliate: Address, voucher: ConversionVoucher, signature: BytesN<64>)`.
- Verify signature against advertiser public key using `env.crypto().ed25519_verify`.
- Prevent replay using nonce bitmap.

### Acceptance Criteria
- [ ] Cryptographic Ed25519 signature verification passes.
- [ ] Nonce nullifier prevents replay attacks.
- [ ] Commission logged to affiliate.

---

### [#47: feat(batch): implement vectorized signature verification for multi-advertiser sales](https://github.com/StormSale/Storm-Contract/issues/47)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/47
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As a network aggregator, I want to batch-submit vouchers from distinct advertisers in a single call.

### Technical Specification
- Implement vectorized loop validating multiple `(advertiser, voucher, signature)` tuples.
- Short-circuit on invalid signature or skip failed vouchers with error report.
- Commit valid conversions.

### Acceptance Criteria
- [ ] Vectorized verification passes.
- [ ] Invalid signatures isolated.
- [ ] Tests verify multi-signer batches.

---

### [#48: feat(batch): add bulk campaign metadata query endpoint to minimize RPC round-trips](https://github.com/StormSale/Storm-Contract/issues/48)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/48
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a frontend developer, I want to query a list of campaign IDs and receive their metadata in an array in a single query.

### Technical Specification
- Implement `get_campaigns_bulk(campaign_ids: Vec<u32>) -> Vec<Campaign>`.
- Skip non-existent IDs gracefully.
- Extend TTL on accessed entries.

### Acceptance Criteria
- [ ] Bulk query returns array of Campaign structs.
- [ ] Handles mixed valid/invalid IDs safely.
- [ ] Unit tests verify bulk query.

---

### [#49: feat(batch): implement Merkle tree depth and leaf validation constraints](https://github.com/StormSale/Storm-Contract/issues/49)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/49
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a protocol engineer, I want Merkle trees bounded to maximum depth of 16 (65,536 sales) to prevent unbounded computation in proof verification.

### Technical Specification
- Enforce `proof.len() <= 16` in proof verification.
- Reject oversized proofs with `Error::MerkleProofTooDeep`.
- Assert canonical leaf hashing format `sha256(leaf)`.

### Acceptance Criteria
- [ ] Proof length capped at 16 elements.
- [ ] Oversized proofs rejected immediately.
- [ ] Canonical hashing validated.

---

### [#50: feat(batch): add batch sale revocation mechanism for disputed conversions prior to clearing](https://github.com/StormSale/Storm-Contract/issues/50)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/50
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an auditor, I want the ability to reject a batch of fraudulent sales before their clearing period concludes, returning the locked commissions to campaign escrow.

### Technical Specification
- Add `batch_reject_sales(auditor: Address, campaign_id: u32, affiliates: Vec<Address>)`.
- Require Auditor role authorization.
- Credit commission amounts back to `campaign.budget` and delete or mark sales rejected.

### Acceptance Criteria
- [ ] Auditor auth verified.
- [ ] Commissions refunded back to campaign budget.
- [ ] Sales marked rejected; cannot be claimed.

---

### [#51: feat(batch): implement pagination cursors for large campaign sale sets](https://github.com/StormSale/Storm-Contract/issues/51)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/51
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an indexer, I want paginated read access to a campaign's sales using a cursor to prevent memory limit exhaustion on large datasets.

### Technical Specification
- Implement `get_sales_paginated(campaign_id: u32, start_index: u32, limit: u32) -> Vec<Sale>`.
- Enforce maximum limit of 50 per page.
- Return slice of sales.

### Acceptance Criteria
- [ ] Paginated access returns requested slice.
- [ ] Max page limit enforced.
- [ ] Cursor boundaries tested.

---

### [#52: feat(batch): add batch claim failure isolation (partial settlement pattern)](https://github.com/StormSale/Storm-Contract/issues/52)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/52
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As an affiliate claiming 10 sales, I want valid sales to succeed even if 1 sale fails clearance so that the entire batch is not blocked.

### Technical Specification
- Implement try-catch / Result matching within batch iteration.
- Return struct `BatchClaimResult { successful: u32, failed: u32, total_claimed: i128 }`.
- Settle valid claims.

### Acceptance Criteria
- [ ] Partial successes settle cleanly.
- [ ] Failed claim details returned in result struct.
- [ ] Comprehensive test with mixed valid/invalid claims.

---

### [#53: feat(security): implement global emergency pause circuit breaker (pause/unpause)](https://github.com/StormSale/Storm-Contract/issues/53)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/53
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a security administrator, I want to pause critical protocol state during active exploit detection so that user escrow funds cannot be drained.

### Technical Specification
- Add `pause(admin: Address)` and `unpause(admin: Address)` entrypoints.
- Store boolean under `DataKey::Paused`.
- Gate `create_campaign`, `top_up_budget`, `log_sale`, and `claim_payout` with `require_not_paused`.

### Acceptance Criteria
- [ ] Admin auth enforced on pause/unpause.
- [ ] Protocol operations revert with `Error::ProtocolPaused` when paused.
- [ ] Unit tests cover pause and unpause cycles.

---

### [#54: feat(security): add advertiser campaign-level pause and unpause controls](https://github.com/StormSale/Storm-Contract/issues/54)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/54
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As an advertiser, I want to pause my campaign instantly if my merchant checkout server experiences fraud or downtime.

### Technical Specification
- Add `pause_campaign(advertiser: Address, campaign_id: u32)`.
- Add `resume_campaign(advertiser: Address, campaign_id: u32)`.
- Revert new sales with `Error::CampaignInactive` when paused.

### Acceptance Criteria
- [ ] Advertiser can pause/resume own campaign.
- [ ] Logging sales to paused campaign fails.
- [ ] Existing cleared claims remain payable.

---

### [#55: feat(security): implement affiliate fraud pause flag to freeze disputed commission claims](https://github.com/StormSale/Storm-Contract/issues/55)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/55
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an auditor, I want to flag a suspicious affiliate address so that their pending payouts are frozen while an investigation proceeds.

### Technical Specification
- Store `DataKey::AffiliateBlacklist(Address)`.
- Add `set_affiliate_frozen(auditor: Address, affiliate: Address, frozen: bool)`.
- Block `claim_payout` if affiliate is frozen.

### Acceptance Criteria
- [ ] Auditor role verified.
- [ ] Frozen affiliates cannot claim payouts.
- [ ] Unfreezing restores claim eligibility.

---

### [#56: feat(security): add timelock delay requirement for critical admin governance parameters](https://github.com/StormSale/Storm-Contract/issues/56)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/56
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As a community participant, I want protocol parameter changes (fees, whitelists) subject to a 48-hour timelock delay before taking effect.

### Technical Specification
- Implement two-phase commit: `queue_parameter_change` and `execute_parameter_change`.
- Store proposed change and `executable_after = env.ledger().timestamp() + 172_800`.
- Revert execution before timelock matures.

### Acceptance Criteria
- [ ] Timelock period enforced.
- [ ] Premature execution reverts with `Error::TimelockNotMatured`.
- [ ] Tested with simulated ledger timestamps.

---

### [#57: feat(security): implement reentrancy protection guard for external token transfer invocations](https://github.com/StormSale/Storm-Contract/issues/57)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/57
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a smart contract auditor, I want a reentrancy guard invariant so that malicious token contracts cannot re-enter the escrow during payout execution.

### Technical Specification
- Add reentrancy lock in instance storage `DataKey::Locked`.
- Enforce checks-effects-interactions pattern across all payout functions.
- Set lock before transfer and clear after transfer.

### Acceptance Criteria
- [ ] State changes committed before external token calls.
- [ ] Reentrant calls revert with `Error::ReentrancyDetected`.
- [ ] Formal review passed.

---

### [#58: feat(security): support contract upgradability via env.deployer().update_current_contract_wasm](https://github.com/StormSale/Storm-Contract/issues/58)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/58
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`, `stellar-ecosystem`

### User Story
As a protocol admin, I want to upgrade the contract WASM bytecode in-place using Soroban native deployer updates without migrating state.

### Technical Specification
- Add `upgrade(admin: Address, new_wasm_hash: BytesN<32>)`.
- Require Admin authorization.
- Invoke `env.deployer().update_current_contract_wasm(new_wasm_hash)`.

### Acceptance Criteria
- [ ] Upgrade entrypoint implemented.
- [ ] Restricted exclusively to Admin.
- [ ] Event emitted with new WASM hash.

---

### [#59: feat(security): add multi-sig threshold authorization requirement for contract upgrades](https://github.com/StormSale/Storm-Contract/issues/59)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/59
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As an institutional user, I want contract upgrades to require M-of-N multi-sig authorization rather than a single private key.

### Technical Specification
- Define multi-sig signer threshold in admin storage.
- Implement proposal and approval collection for upgrades.
- Execute upgrade only when required approvals are met.

### Acceptance Criteria
- [ ] Multi-sig threshold enforced.
- [ ] Upgrade rejected with insufficient signatures.
- [ ] Integration tests verify M-of-N threshold.

---

### [#60: feat(security): implement strict zero-address and contract-as-affiliate validation guards](https://github.com/StormSale/Storm-Contract/issues/60)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/60
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As a contract engineer, I want affiliate addresses checked against zero/null addresses and self-referential addresses to eliminate phantom payouts.

### Technical Specification
- In `log_sale`, verify `affiliate != env.current_contract_address()`.
- Verify `affiliate != advertiser`.
- Revert with `Error::InvalidAffiliate` if violated.

### Acceptance Criteria
- [ ] Contract address cannot be designated as affiliate.
- [ ] Advertiser cannot log sale to self.
- [ ] Guard tests pass.

---

### [#61: feat(security): enforce storage partition isolation between distinct campaign IDs](https://github.com/StormSale/Storm-Contract/issues/61)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/61
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an advertiser, I want absolute cryptographic guarantees that sales logged in Campaign A can never deduct budget from Campaign B.

### Technical Specification
- Audit key derivation for `DataKey::Campaign(id)` and `DataKey::Sale(id, affiliate)`.
- Add invariant assertion verifying campaign budget deductions only match associated sales.
- Property test invariant with random IDs.

### Acceptance Criteria
- [ ] Storage keys strictly isolated by ID.
- [ ] Cross-campaign contamination mathematically impossible.
- [ ] Verified via property tests.

---

### [#62: feat(security): add rate-limiting counter for rapid-fire sale logging from single advertiser](https://github.com/StormSale/Storm-Contract/issues/62)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/62
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a platform protector, I want a rate limiter on sales logged per ledger block per advertiser to mitigate DDoS or runaway bot loops.

### Technical Specification
- Track `SalesLoggedThisLedger(Address, u32)` in temporary storage.
- Enforce maximum 100 sales per block per advertiser.
- Revert excess sales with `Error::RateLimitExceeded`.

### Acceptance Criteria
- [ ] Temporary counter tracks sales per block.
- [ ] Resets on next ledger block automatically.
- [ ] Over-limit requests rejected.

---

### [#63: feat(security): implement maximum commission rate sanity cap (<= 50%)](https://github.com/StormSale/Storm-Contract/issues/63)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/63
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As an advertiser, I want a safety cap on commission rates (e.g. max 5000 bps / 50%) so that fat-finger mistakes during campaign creation do not bankrupt budget escrows.

### Technical Specification
- Define `MAX_COMMISSION_BPS: u32 = 5000` (50%).
- In `create_campaign`, enforce `commission_rate <= MAX_COMMISSION_BPS`.
- Revert with `Error::CommissionRateExceedsCap`.

### Acceptance Criteria
- [ ] 50% max commission rate enforced.
- [ ] Campaign creation with 5001 bps rejected.
- [ ] Boundary tests pass.

---

### [#64: feat(security): add minimum clearing period threshold (>= 1 hour) to prevent flash claims](https://github.com/StormSale/Storm-Contract/issues/64)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/64
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As an advertiser, I want clearing periods to require at least 3,600 seconds (1 hour) so that fraudulent sales cannot be flash-claimed in the same block.

### Technical Specification
- Define `MIN_CLEARING_PERIOD = 3_600u32`.
- In `create_campaign`, enforce `clearing_period >= MIN_CLEARING_PERIOD`.
- Return `Error::ClearingPeriodTooShort`.

### Acceptance Criteria
- [ ] 1-hour minimum clearing period enforced.
- [ ] 0-second clearing periods rejected.
- [ ] Unit tests pass.

---

### [#65: feat(security): implement two-step admin transfer pattern (nominate and accept)](https://github.com/StormSale/Storm-Contract/issues/65)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/65
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As the platform founder, I want admin transfers to follow a two-step nominate/accept pattern so that ownership is never lost to a mistyped address.

### Technical Specification
- Add `nominate_admin(current_admin: Address, nominated: Address)`.
- Add `accept_admin(nominated: Address)`.
- Transfer ownership only when nominated address signs acceptance.

### Acceptance Criteria
- [ ] Two-step admin transfer implemented.
- [ ] Only nominated address can accept.
- [ ] Reassignment event emitted.

---

### [#66: feat(security): add audit trail event logging for all administrative role updates](https://github.com/StormSale/Storm-Contract/issues/66)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/66
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As an auditor, I want every role grant and revocation logged with timestamp and target address so that access changes are permanently auditable.

### Technical Specification
- In `grant_role`, emit `("admin", symbol_short!("role"))` with `(target, role)`.
- Document role event indexing guide in README.

### Acceptance Criteria
- [ ] Event emitted on every role grant.
- [ ] Role transitions traceable in ledger history.
- [ ] Snapshot test verified.

---

### [#67: feat(security): implement blacklisted wallet screening interface in entrypoints](https://github.com/StormSale/Storm-Contract/issues/67)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/67
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As an enterprise compliance team, I want sanctions-screened addresses blocked at the contract level from creating campaigns or claiming rewards.

### Technical Specification
- Add `is_sanctioned(address: Address) -> bool` check in entrypoints.
- Admin or compliance oracle can update blacklist registry.
- Deny access with `Error::SanctionedAddress`.

### Acceptance Criteria
- [ ] Blacklist registry stored in storage.
- [ ] Screened addresses blocked from all write methods.
- [ ] Compliance test suite verified.

---

### [#68: feat(storage): automate persistent storage TTL extension on active campaign interactions](https://github.com/StormSale/Storm-Contract/issues/68)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/68
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `infra`

### User Story
As a campaign owner, I want every interaction with my campaign to automatically bump its storage TTL so that my campaign never expires while actively running.

### Technical Specification
- Add `extend_campaign_ttl` call inside `top_up_budget`, `log_sale`, and `audit_sale`.
- Bump to at least 100,000 ledgers.
- Verify storage rent is preserved.

### Acceptance Criteria
- [ ] TTL automatically extended on all active campaign calls.
- [ ] Expiration risk eliminated for active campaigns.
- [ ] Simulation tests pass.

---

### [#69: feat(storage): automate instance storage TTL extension on protocol state calls](https://github.com/StormSale/Storm-Contract/issues/69)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/69
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `infra`

### User Story
As the contract admin, I want instance storage (Admin, Token, CampaignCount) automatically extended on every transaction so that global contract configuration never expires.

### Technical Specification
- Add `env.storage().instance().extend_ttl(100_000, 200_000)` in facade functions.
- Ensure threshold and extension parameters align with Stellar recommendations.

### Acceptance Criteria
- [ ] Instance TTL bumped on protocol calls.
- [ ] Threshold parameters audited.
- [ ] Verified via cargo test.

---

### [#70: feat(storage): implement claimed sale data pruning to temporary storage](https://github.com/StormSale/Storm-Contract/issues/70)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/70
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `infra`

### User Story
As an ecosystem architect, I want claimed and settled sales to be pruned or archived to Temporary storage to minimize persistent ledger rent.

### Technical Specification
- Upon successful `claim_payout`, delete persistent `DataKey::Sale` entry.
- Record receipt hash in temporary storage with 30-day TTL.
- Save persistent rent for old settled transactions.

### Acceptance Criteria
- [ ] Claimed sales pruned from persistent storage.
- [ ] Receipt hash verifiable in temporary storage.
- [ ] Rent cost reduction verified.

---

### [#71: feat(storage): add closed campaign archival mechanism to eliminate persistent rent overhead](https://github.com/StormSale/Storm-Contract/issues/71)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/71
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As an advertiser who has refunded and closed a campaign, I want to archive its state so that ongoing rent is no longer incurred.

### Technical Specification
- Implement `archive_campaign(advertiser: Address, campaign_id: u32)`.
- Verify budget is 0 and no pending claims exist.
- Remove persistent campaign entry and emit archival event.

### Acceptance Criteria
- [ ] Campaign can be archived when budget is 0.
- [ ] Persistent entry removed cleanly.
- [ ] Archival event emitted.

---

### [#72: feat(storage): implement rent fee estimation helper query for prospective campaigns](https://github.com/StormSale/Storm-Contract/issues/72)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/72
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a frontend user, I want a query endpoint that calculates estimated rent cost for running a campaign for 30, 90, or 365 days.

### Technical Specification
- Implement `estimate_rent_cost(duration_ledgers: u32) -> i128`.
- Base calculation on current Stellar network rent rate per byte.
- Return stroop estimate.

### Acceptance Criteria
- [ ] Rent estimator implemented.
- [ ] Estimates scale with requested ledger duration.
- [ ] Unit tests pass.

---

### [#73: feat(storage): create dedicated extend_campaign_ttl entrypoint for automated keeper bots](https://github.com/StormSale/Storm-Contract/issues/73)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/73
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `infra`

### User Story
As a DevOps engineer, I want a permissionless entrypoint to bump TTL on any campaign so that automated keeper bots can maintain ledger state health.

### Technical Specification
- Add public `bump_campaign_ttl(campaign_id: u32)`.
- Extend persistent TTL by 200,000 ledgers.
- Anyone can call (permissionless keeper pattern).

### Acceptance Criteria
- [ ] Permissionless TTL bump entrypoint.
- [ ] Bumps TTL on valid campaign.
- [ ] Tested with mock ledger.

---

### [#74: feat(storage): audit and separate Temporary vs Persistent storage across all data keys](https://github.com/StormSale/Storm-Contract/issues/74)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/74
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a protocol architect, I want an audit of all `DataKey` entries to ensure ephemeral state uses Temporary storage and immutable state uses Persistent storage.

### Technical Specification
- Audit `storage.rs` data keys.
- Migrate nonces, rate-limit counters, and short-term locks to Temporary storage.
- Keep campaigns and balances in Persistent storage.

### Acceptance Criteria
- [ ] Temporary storage used for short-lived state.
- [ ] Persistent storage reserved for financial balances.
- [ ] Comprehensive audit report in PR.

---

### [#75: feat(storage): implement compact key hashing scheme to minimize ledger entry byte sizes](https://github.com/StormSale/Storm-Contract/issues/75)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/75
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a gas optimizer, I want storage keys represented as short symbols or packed 16-byte hashes rather than verbose enum variants.

### Technical Specification
- Refactor `DataKey` enum to minimize discriminant overhead.
- Benchmark key byte footprint reduction.
- Update storage accessor helpers.

### Acceptance Criteria
- [ ] Storage key size reduced.
- [ ] All existing read/write helpers updated.
- [ ] Benchmarks documented.

---

### [#76: feat(storage): add automated TTL health inspection query returning remaining ledger blocks](https://github.com/StormSale/Storm-Contract/issues/76)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/76
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a monitoring service, I want to query the exact remaining TTL (in ledgers) of a campaign so that alerting systems can warn of impending expiration.

### Technical Specification
- Implement `get_campaign_ttl_status(campaign_id: u32) -> TTLStatus`.
- Return struct with `live_until_ledger`, `ledgers_remaining`, `health_status`.
- Handle expired or missing campaigns cleanly.

### Acceptance Criteria
- [ ] `TTLStatus` returned accurately.
- [ ] Status categorized as Healthy, Warning, or Critical.
- [ ] Query tested in unit suite.

---

### [#77: feat(storage): implement batch TTL extension for multi-campaign merchant portfolios](https://github.com/StormSale/Storm-Contract/issues/77)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/77
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a keeper bot, I want to extend the TTL on up to 50 campaigns in a single transaction to reduce operational bot transaction fees.

### Technical Specification
- Add `batch_bump_campaign_ttl(campaign_ids: Vec<u32>)`.
- Loop through IDs and extend persistent TTL.
- Skip non-existent campaigns without failing batch.

### Acceptance Criteria
- [ ] Bulk TTL bump handles up to 50 IDs.
- [ ] Resilient to missing or closed campaigns.
- [ ] Unit test verifies batch extension.

---

### [#78: feat(storage): benchmark Soroban CPU instructions and memory consumption across operations](https://github.com/StormSale/Storm-Contract/issues/78)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/78
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a performance engineer, I want automated benchmarks measuring CPU instructions and RAM usage for every contract entrypoint to prevent gas spikes.

### Technical Specification
- Create benchmark harness using Soroban SDK metering testutils.
- Assert CPU instruction limits (< 200,000 instructions per call).
- Fail CI if CPU instructions regress by > 10%.

### Acceptance Criteria
- [ ] Metering benchmark tests implemented.
- [ ] Instruction and memory budgets asserted.
- [ ] Baseline metrics committed to docs.

---

### [#79: feat(storage): implement stale campaign sweep logic with rent rebate incentive for caller](https://github.com/StormSale/Storm-Contract/issues/79)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/79
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As a community participant, I want to earn a micro-reward for sweeping completely exhausted and inactive campaigns from persistent storage.

### Technical Specification
- Add `sweep_closed_campaign(caller: Address, campaign_id: u32)`.
- Verify campaign has been closed > 90 days with 0 balance.
- Delete storage entry and award micro-incentive to caller.

### Acceptance Criteria
- [ ] Safe sweep condition verified.
- [ ] Storage deleted and rent returned.
- [ ] Unit tests pass.

---

### [#80: feat(storage): optimize string storage by migrating campaign metadata tags to symbol hashes](https://github.com/StormSale/Storm-Contract/issues/80)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/80
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a contract engineer, I want campaign tags stored as 32-bit symbol hashes instead of raw UTF-8 strings to save byte rent.

### Technical Specification
- Replace string tags in `Campaign` with `Vec<Symbol>`.
- Limit tags to max 5 symbols per campaign.
- Validate symbol formats during creation.

### Acceptance Criteria
- [ ] Tags stored as `Symbol` vec.
- [ ] Storage byte savings measured.
- [ ] Unit tests pass.

---

### [#81: feat(storage): add storage footprint regression assertions in test suite](https://github.com/StormSale/Storm-Contract/issues/81)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/81
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `infra`

### User Story
As a reviewer, I want tests to assert that data structures do not grow unexpectedly between commits.

### Technical Specification
- Write test asserting `core::mem::size_of::<Campaign>()` and `Sale`.
- Fail test if struct size increases without justification.

### Acceptance Criteria
- [ ] Size assertions active in test suite.
- [ ] Inadvertent padding or bloating caught in CI.
- [ ] Documentation updated.

---

### [#82: feat(storage): implement rent-aware budget top-up calculation](https://github.com/StormSale/Storm-Contract/issues/82)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/82
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an advertiser, I want budget top-ups to automatically offset any accrued rent shortfall so that the campaign remains self-sustaining.

### Technical Specification
- Calculate required rent fee buffer during `top_up_budget`.
- Deduct minimal rent deposit if needed and credit remainder to spendable budget.
- Return breakdown to caller.

### Acceptance Criteria
- [ ] Rent buffer calculation implemented.
- [ ] Budget reflects net spendable balance.
- [ ] Unit tests pass.

---

### [#83: feat(sbt): implement non-transferable Soulbound milestone badge minting contract](https://github.com/StormSale/Storm-Contract/issues/83)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/83
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`, `stellar-ecosystem`

### User Story
As a top-performing affiliate, I want to earn an on-chain non-transferable Soulbound badge verifying my sales volume milestones on Stellar.

### Technical Specification
- Implement Soulbound token contract standard interface.
- Support `mint(affiliate: Address, tier: u32)` restricted to StormSale contract.
- Permanently disallow `transfer` or `transfer_from`.

### Acceptance Criteria
- [ ] Soulbound badge contract created.
- [ ] Transfers strictly revert with `Error::SoulboundNonTransferable`.
- [ ] Minting restricted to authorized escrow contract.

---

### [#84: feat(sbt): add verification criteria for 1K XLM affiliate volume milestone](https://github.com/StormSale/Storm-Contract/issues/84)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/84
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an affiliate reaching 1,000 XLM in verified sales volume, I want the contract to authorize minting my Bronze Milestone Badge.

### Technical Specification
- Track cumulative claimed volume per affiliate in `storage.rs`.
- In `claim_payout`, check if cumulative volume >= 1,000 XLM.
- Trigger badge mint authorization event.

### Acceptance Criteria
- [ ] 1K XLM volume threshold tracked.
- [ ] Bronze badge eligibility unlocked upon reaching threshold.
- [ ] Milestone event emitted.

---

### [#85: feat(sbt): add verification criteria for 10K XLM affiliate volume milestone](https://github.com/StormSale/Storm-Contract/issues/85)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/85
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a veteran affiliate reaching 10,000 XLM in verified sales, I want to earn the Silver Milestone Badge.

### Technical Specification
- Check cumulative claimed volume >= 10,000 XLM.
- Authorize Silver badge tier minting.
- Prevent duplicate badge minting for same tier.

### Acceptance Criteria
- [ ] 10K XLM threshold verified.
- [ ] Silver badge minted only once.
- [ ] Unit tests pass.

---

### [#86: feat(sbt): add verification criteria for 100K XLM affiliate volume milestone](https://github.com/StormSale/Storm-Contract/issues/86)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/86
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an elite affiliate driving over 100,000 XLM in sales volume, I want to unlock the Gold Elite Milestone Badge.

### Technical Specification
- Verify cumulative volume >= 100,000 XLM.
- Mint Gold tier Soulbound token.
- Emit protocol-wide VIP affiliate event.

### Acceptance Criteria
- [ ] 100K XLM threshold verified.
- [ ] Gold tier token minted.
- [ ] Event emitted and tested.

---

### [#87: feat(sbt): enforce non-transferability invariant (revert on transfer, allow burn)](https://github.com/StormSale/Storm-Contract/issues/87)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/87
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`

### User Story
As a reputation auditor, I want badges bound to the earner wallet address forever so that reputation cannot be traded or bought on secondary markets.

### Technical Specification
- In SBT token contract, override transfer functions to return `Error::Unauthorized`.
- Allow affiliate to self-burn badge if desired (`burn`).

### Acceptance Criteria
- [ ] Transfer attempts revert unconditionally.
- [ ] Self-burn permitted.
- [ ] Invariant tested with fuzz suite.

---

### [#88: feat(sbt): implement affiliate badge portfolio query interface](https://github.com/StormSale/Storm-Contract/issues/88)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/88
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a frontend developer, I want a query returning all milestone badges earned by an affiliate address.

### Technical Specification
- Implement `get_affiliate_badges(affiliate: Address) -> Vec<BadgeMetadata>`.
- Return list of badge IDs, tiers, and mint timestamps.
- Optimize gas footprint.

### Acceptance Criteria
- [ ] Query returns array of earned badges.
- [ ] Returns empty array for new affiliates.
- [ ] Tested in test suite.

---

### [#89: feat(sbt): emit on-chain milestone achievement events with badge token IDs](https://github.com/StormSale/Storm-Contract/issues/89)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/89
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As an off-chain notification service, I want events emitted when badges are minted so that Discord/Telegram bots can announce achievements.

### Technical Specification
- Emit `("badge", symbol_short!("minted"))` with `(affiliate, tier, token_id)`.
- Document payload format in README.

### Acceptance Criteria
- [ ] Event emitted upon successful mint.
- [ ] Token ID and tier included.
- [ ] Snapshot test verified.

---

### [#90: feat(sbt): support advertiser-sponsored custom achievement badge tiers](https://github.com/StormSale/Storm-Contract/issues/90)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/90
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As a brand advertiser, I want to sponsor custom achievement badges for affiliates who drive specific conversion milestones in my campaigns.

### Technical Specification
- Add `create_custom_badge(advertiser: Address, campaign_id: u32, threshold: i128, metadata_hash: BytesN<32>)`.
- Track custom badge eligibility per campaign.
- Mint custom brand badge upon threshold qualification.

### Acceptance Criteria
- [ ] Advertiser can create custom badges.
- [ ] Campaign-specific volume qualifies affiliate.
- [ ] Tested with mock campaign.

---

### [#91: feat(sbt): implement cryptographic metadata URI resolution for milestone badges](https://github.com/StormSale/Storm-Contract/issues/91)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/91
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `stellar-ecosystem`

### User Story
As an explorer developer, I want badge token IDs to resolve to IPFS/Arweave cryptographic metadata URIs following standard NFT schemas.

### Technical Specification
- Implement `token_uri(token_id: u32) -> String`.
- Return base URI + IPFS CID for designated badge tier.
- Ensure compliant JSON schema representation.

### Acceptance Criteria
- [ ] `token_uri` returns valid URI string.
- [ ] IPFS CIDs mapped correctly per tier.
- [ ] Unit tests pass.

---

### [#92: feat(sbt): add milestone badge claiming deadline expiration logic](https://github.com/StormSale/Storm-Contract/issues/92)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/92
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a campaign organizer, I want seasonal achievement badges to carry a claiming deadline so that limited-edition badges are exclusive.

### Technical Specification
- Add optional `claim_deadline: Option<u64>` to badge definition.
- Revert claim attempts after deadline with `Error::BadgeClaimExpired`.

### Acceptance Criteria
- [ ] Deadline enforced when configured.
- [ ] Claims succeed before deadline and fail after.
- [ ] Tested with ledger time travel.

---

### [#93: feat(sbt): implement Soulbound badge revocation mechanism for fraudulent affiliates](https://github.com/StormSale/Storm-Contract/issues/93)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/93
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `security`

### User Story
As a platform compliance officer, I want the ability to revoke badges from affiliates found to have conducted ad fraud.

### Technical Specification
- Add `revoke_badge(admin: Address, badge_id: u32, reason_code: u32)`.
- Require Admin or Auditor authorization.
- Burn badge and emit `("badge", symbol_short!("revoked"))`.

### Acceptance Criteria
- [ ] Only authorized roles can revoke.
- [ ] Revoked badge removed from affiliate portfolio.
- [ ] Revocation event logged.

---

### [#94: feat(sbt): add badge-gated campaign access verification in contract](https://github.com/StormSale/Storm-Contract/issues/94)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/94
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As an enterprise advertiser, I want to restrict VIP campaigns so that only affiliates holding a Silver or Gold badge can join.

### Technical Specification
- Add `required_badge_tier: Option<u32>` to `Campaign` struct.
- In `log_sale`, verify affiliate holds required badge tier.
- Revert unqualified sales with `Error::BadgeRequirementNotMet`.

### Acceptance Criteria
- [ ] Campaign can require minimum badge tier.
- [ ] Unbadged affiliates rejected.
- [ ] Badged affiliates accepted cleanly.

---

### [#95: test(infra): implement property-based testing with proptest for escrow accounting invariants](https://github.com/StormSale/Storm-Contract/issues/95)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/95
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `infra`

### User Story
As a lead developer, I want randomized property tests asserting that contract token balance is always >= sum of all campaign budgets under all sequences of operations.

### Technical Specification
- Create `proptest` harness in `test_invariants.rs`.
- Generate arbitrary sequences of create, top-up, sale, audit, claim, and refund.
- Assert global solvency invariant holds after every step.

### Acceptance Criteria
- [ ] Proptest suite runs 10,000 iterations.
- [ ] Zero solvency violations discovered.
- [ ] Added to CI pipeline.

---

### [#96: test(infra): add cargo-fuzz harness for Soroban contract entrypoints](https://github.com/StormSale/Storm-Contract/issues/96)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/96
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`, `infra`

### User Story
As a security engineer, I want libFuzzer fuzzing contract entrypoint inputs to identify any potential panics, unexpected reverts, or memory exhaustion.

### Technical Specification
- Set up `fuzz/` directory with `cargo fuzz`.
- Define fuzz targets for `create_campaign`, `log_sale`, and `claim_payout`.
- Run continuous fuzzing in CI workflow.

### Acceptance Criteria
- [ ] `cargo-fuzz` targets configured and passing.
- [ ] No panics or unhandled exceptions under corrupt inputs.
- [ ] Fuzzing documentation added to CONTRIBUTING.md.

---

### [#97: test(infra): implement 100% error code branch coverage test suite in test.rs](https://github.com/StormSale/Storm-Contract/issues/97)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/97
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a QA lead, I want every single error enum variant in `errors.rs` triggered by at least one dedicated negative unit test.

### Technical Specification
- Audit all 11 error codes in `errors.rs`.
- Add unit tests triggering each specific error variant.
- Assert exact `Err(Ok(Error::<Variant>))` matches.

### Acceptance Criteria
- [ ] Every error enum code has dedicated test.
- [ ] 100% error branch coverage achieved.
- [ ] Verified via `cargo test`.

---

### [#98: test(infra): create differential testing suite comparing contract math against Python reference](https://github.com/StormSale/Storm-Contract/issues/98)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/98
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a mathematician, I want commission calculation outputs cross-checked against a Python reference model across 100,000 random inputs to ensure identical rounding.

### Technical Specification
- Implement Python reference script matching Soroban integer math.
- Generate test vector JSON with inputs and expected outputs.
- Assert Rust implementation matches JSON test vectors exactly.

### Acceptance Criteria
- [ ] 100,000 test vectors verified.
- [ ] Zero rounding divergence observed.
- [ ] Test harness committed.

---

### [#99: ci(infra): add automated GitHub Actions workflow for cargo clippy with zero warnings](https://github.com/StormSale/Storm-Contract/issues/99)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/99
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `infra`

### User Story
As a maintainer, I want CI to enforce `cargo clippy -- -D warnings` on every pull request to maintain pristine Rust code quality.

### Technical Specification
- Update `.github/workflows/ci.yml`.
- Add Clippy step with `--all-targets -- -D warnings`.
- Fail PR checks on any lint warning.

### Acceptance Criteria
- [ ] Clippy workflow active in CI.
- [ ] Zero warnings on current main branch.
- [ ] PR validation passes.

---

### [#100: ci(infra): add automated WebAssembly size profiling and budget limit gate in CI](https://github.com/StormSale/Storm-Contract/issues/100)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/100
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `infra`

### User Story
As a smart contract engineer, I want CI to build `stormsale.wasm` and verify the binary size remains under 64 KB to ensure ultra-low deployment fees.

### Technical Specification
- Add size check script in `.github/workflows/ci.yml`.
- Measure release wasm binary size.
- Fail build if size exceeds 65,536 bytes.

### Acceptance Criteria
- [ ] WASM size measured and posted to PR summary.
- [ ] Fails build if binary exceeds 64 KB limit.
- [ ] Size optimization docs added.

---

### [#101: test(infra): implement formal verification specs for campaign budget non-negativity](https://github.com/StormSale/Storm-Contract/issues/101)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/101
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As a cryptographic auditor, I want mathematical proof that `campaign.budget` can never transition below 0 under any possible ledger sequence.

### Technical Specification
- Write formal inductive proof specification.
- Use Kani or Prusti Rust formal verification tooling.
- Formally verify non-negativity invariant.

### Acceptance Criteria
- [ ] Formal verification harness configured.
- [ ] Budget >= 0 proven mathematically.
- [ ] Verification report committed to Docs.

---

### [#102: test(infra): create multi-agent simulation test simulating 1,000 concurrent affiliate claims](https://github.com/StormSale/Storm-Contract/issues/102)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/102
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `infra`

### User Story
As a scalability engineer, I want a simulation test modeling 1,000 concurrent affiliates claiming payouts against 50 campaigns simultaneously.

### Technical Specification
- Write simulation test in `test_simulation.rs`.
- Populate 50 campaigns and 1,000 affiliates.
- Process concurrent sales and claims; assert total token accounting reconciles to zero delta.

### Acceptance Criteria
- [ ] 1,000 concurrent claims simulated cleanly.
- [ ] Final balances match expected values to the stroop.
- [ ] Performance profiled.

---

### [#103: test(infra): add automated Stellar Testnet deployment and initialization integration script](https://github.com/StormSale/Storm-Contract/issues/103)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/103
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `stellar-ecosystem`

### User Story
As a deployment engineer, I want an idempotent bash/Python script that deploys `stormsale.wasm` to Stellar Testnet and runs initialization in one command.

### Technical Specification
- Create `scripts/deploy_testnet.sh`.
- Use `stellar keys`, `stellar contract deploy`, and `stellar contract invoke`.
- Output deployed contract ID to `.env`.

### Acceptance Criteria
- [ ] Script deploys and initializes contract on Testnet.
- [ ] Idempotent re-run handling.
- [ ] Tested and documented in README.

---

### [#104: ci(infra): configure cargo audit vulnerability scanning in daily GitHub Actions cron](https://github.com/StormSale/Storm-Contract/issues/104)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/104
- **Labels:** `contract`, `Drips`, `complexity: low`, `complexity`, `security`, `infra`

### User Story
As a security manager, I want automated dependency audits running daily to detect any newly disclosed CVEs in Cargo dependencies.

### Technical Specification
- Add `.github/workflows/security-audit.yml`.
- Run `cargo audit` on daily cron schedule and on PRs modifying `Cargo.lock`.
- Alert maintainers on discovered vulnerabilities.

### Acceptance Criteria
- [ ] Security audit workflow configured.
- [ ] Zero active vulnerabilities on current Cargo.lock.
- [ ] Daily cron active.

---

### [#105: test(infra): implement simulated network latency and reorg resilience tests](https://github.com/StormSale/Storm-Contract/issues/105)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/105
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `infra`

### User Story
As a Web3 developer, I want contract behavior verified against out-of-order ledger timestamps and sequence number jumps.

### Technical Specification
- Write test cases in `test.rs` manipulating `env.ledger().set(...)` with extreme timestamp shifts.
- Verify clearing periods and deadlines evaluate strictly based on ledger timestamp.

### Acceptance Criteria
- [ ] Out-of-order ledger tests pass.
- [ ] Timestamp boundary conditions verified.
- [ ] Edge cases handled cleanly.

---

### [#106: docs(infra): generate automated Soroban contract API documentation with cargo doc](https://github.com/StormSale/Storm-Contract/issues/106)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/106
- **Labels:** `documentation`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As an external integrator, I want comprehensive Rustdoc API documentation generated and published to GitHub Pages.

### Technical Specification
- Add full doc-comments (`///`) to all public functions in `lib.rs`.
- Configure GitHub Actions to run `cargo doc --no-deps`.
- Deploy HTML documentation to GitHub Pages.

### Acceptance Criteria
- [ ] 100% public item doc-comment coverage.
- [ ] `cargo doc` builds without broken links.
- [ ] Published to GitHub Pages.

---

### [#107: ci(infra): add automated snapshot testing workflow for contract invocation XDRs](https://github.com/StormSale/Storm-Contract/issues/107)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/107
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `infra`

### User Story
As a protocol maintainer, I want CI to assert that serialized invocation XDRs match committed snapshot files so that ABI breaks are immediately detected.

### Technical Specification
- Use Soroban SDK snapshot testing features.
- Commit snapshots in `contracts/stormsale/test_snapshots/`.
- CI fails if invocation XDRs change without explicit snapshot update.

### Acceptance Criteria
- [ ] Snapshot test step active in CI.
- [ ] Inadvertent ABI breaks detected automatically.
- [ ] Snapshot update instructions documented.

---

### [#108: feat(batch): implement bit-packed compact serialization for historical Sale structs](https://github.com/StormSale/Storm-Contract/issues/108)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/108
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `infra`

### User Story
As an architect, I want sale metadata bit-packed into compact byte vectors to reduce persistent storage rent costs over time.

### Technical Specification
- Pack timestamp (u40), commission (u64), flags (u8) into compact byte array.
- Write decoder/encoder functions with unit tests.
- Maintain backward compatibility with existing storage.

### Acceptance Criteria
- [ ] Struct size reduced by at least 40%.
- [ ] Serde functions verified with property tests.
- [ ] Zero data loss on roundtrip.

---

### [#109: feat(b2b): implement multi-seat operator permission matrix (Manager, Billing, Analyst) in storage](https://github.com/StormSale/Storm-Contract/issues/109)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/109
- **Labels:** `contract`, `Drips`, `complexity: high`, `complexity`, `security`

### User Story
As an enterprise B2B merchant, I want to assign granular operator capabilities (e.g. SalesLogger, EscrowManager, Viewer) to team member addresses rather than all-or-nothing operator access.

### Technical Specification
- Define `OperatorCapability` bitflags or enum in `storage.rs`.
- Store capabilities under `DataKey::OperatorCapabilities(campaign_id, operator)`.
- Enforce capability checks in `log_sale`, `top_up_budget`, and `refund_escrow`.

### Acceptance Criteria
- [ ] Granular operator capabilities stored in contract.
- [ ] `set_operator_capabilities(advertiser, campaign_id, operator, capabilities)` implemented.
- [ ] Unauthorized actions by scoped operators revert with `Error::Unauthorized`.

---

### [#110: feat(b2c): implement instant micro-commission claim fast-track for verified B2C creator affiliates](https://github.com/StormSale/Storm-Contract/issues/110)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/110
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As a verified B2C creator, I want micro-commissions (< 50 XLM) to bypass manual auditor waiting queues and settle instantly so that creator liquidity is immediate.

### Technical Specification
- Store `micro_payout_threshold: i128` on B2C campaigns.
- In `claim_payout`, if `sale.commission <= micro_payout_threshold` and `campaign.audience == AudienceType::B2C`, auto-approve audit check.
- Require merchant opt-in during campaign creation.

### Acceptance Criteria
- [ ] B2C micro-payout threshold supported in `Campaign`.
- [ ] Micro-commissions claimable without explicit `audit_sale` call.
- [ ] Unit tests verify auto-clearance threshold.

---

### [#111: feat(b2b): support corporate tax invoicing hash and business legal metadata anchoring on-chain](https://github.com/StormSale/Storm-Contract/issues/111)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/111
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: low`, `complexity`

### User Story
As a B2B finance department, I want monthly sales payouts to anchor an immutable SHA-256 invoice receipt hash on-chain for corporate audit compliance (1099-DA).

### Technical Specification
- Add entrypoint `anchor_invoice_receipt(advertiser: Address, campaign_id: u32, invoice_hash: BytesN<32>, period_month: u32)`.
- Store receipt under `DataKey::InvoiceReceipt(campaign_id, period_month)`.
- Emit invoice anchored event with URI hash.

### Acceptance Criteria
- [ ] Invoice hash stored in persistent storage.
- [ ] Advertiser auth enforced.
- [ ] Public query `get_invoice_receipt` implemented.

---

### [#112: feat(b2c): implement creator tipping and performance micro-bonus distribution entrypoint](https://github.com/StormSale/Storm-Contract/issues/112)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/112
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: medium`, `complexity`

### User Story
As an advertiser running a B2C campaign, I want to reward a standout creator with a direct one-off performance tip/bonus transferred instantly from escrow.

### Technical Specification
- Add `reward_creator_bonus(advertiser: Address, campaign_id: u32, creator: Address, bonus_amount: i128, memo: Symbol)` entrypoint.
- Deduct bonus directly from campaign budget.
- Transfer tokens immediately to creator wallet and emit celebratory event.

### Acceptance Criteria
- [ ] Bonus deducted from campaign escrow and transferred directly to creator.
- [ ] Event `("creator", symbol_short!("bonus"))` emitted.
- [ ] Fails if campaign budget is insufficient.

---

### [#113: feat(b2b): add net-term settlement escrow schedules (Net-15/Net-30) for enterprise B2B sales cycles](https://github.com/StormSale/Storm-Contract/issues/113)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/113
- **Labels:** `enhancement`, `contract`, `Drips`, `complexity: high`, `complexity`

### User Story
As an enterprise B2B merchant with long sales cycles, I want to configure Net-15 or Net-30 settlement escrow schedules where commissions release in tranches following invoice clearance.

### Technical Specification
- Support `NetTermSchedule { net_days: u32, auto_release_after: u64 }` in campaign config.
- Hold funds in staged clearing tranches.
- Release funds upon maturity or manual dispute window clearance.

### Acceptance Criteria
- [ ] Net-term schedule model implemented in `storage.rs`.
- [ ] Staged clearing tested against simulated ledger time.
- [ ] Invariant holds: scheduled funds cannot be claimed prematurely.

---

### [#114: feat(b2c): add social handle hash verification for B2C creator onboarding and identity binding](https://github.com/StormSale/Storm-Contract/issues/114)

- **Issue Link:** https://github.com/StormSale/Storm-Contract/issues/114
- **Labels:** `contract`, `Drips`, `complexity: medium`, `complexity`, `stellar-ecosystem`

### User Story
As a B2C creator affiliate, I want to bind my verified X/Telegram/TikTok handle hash to my wallet on-chain so that advertisers know who is promoting their product.

### Technical Specification
- Add entrypoint `bind_creator_handle(creator: Address, platform: Symbol, handle_hash: BytesN<32>)`.
- Store mapping `DataKey::CreatorHandle(creator, platform) -> BytesN<32>`.
- Allow advertisers to query creator social credentials on-chain.

### Acceptance Criteria
- [ ] Creator handle hash stored in persistent storage.
- [ ] Creator authorization enforced.
- [ ] Query helper `get_creator_handle` tested.

---

