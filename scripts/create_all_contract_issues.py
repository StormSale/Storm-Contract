import json, subprocess, time, os

pillars = {
    "Pillar 1: Multi-Asset Escrow & SAC Token Integration": [
        {
            "title": "feat(escrow): enforce minimum escrow deposit threshold per asset class to prevent spam campaigns",
            "labels": "Drips,complexity,complexity: medium,contract,stellar-ecosystem,security",
            "story": "As an ecosystem maintainer, I want campaigns to require a minimum deposit threshold per asset class (e.g. 50 XLM, 10 USDC) so that spam or zero-value campaigns do not pollute the contract state.",
            "spec": "- Define `MIN_BUDGET_XLM` and asset-specific threshold mapping in `storage.rs`.\n- Validate `budget >= min_budget` during `create_campaign`.\n- Return `Error::BudgetBelowMinimum` if threshold is not satisfied.",
            "criteria": "- [ ] Asset minimum thresholds configured in storage.\n- [ ] `create_campaign` rejects budget below threshold with explicit error.\n- [ ] Unit tests cover rejection and boundary conditions."
        },
        {
            "title": "feat(escrow): add safe math wrapper module for i128 decimal conversions across diverse SAC decimals",
            "labels": "Drips,complexity,complexity: high,contract,security,stellar-ecosystem",
            "story": "As a contract engineer, I want safe decimal normalization between 7-decimal XLM and arbitrary SAC tokens (e.g. 6-decimal USDC) so that rounding errors and truncation exploits are prevented.",
            "spec": "- Create `math.rs` module with `checked_mul_div` and decimal scaling functions.\n- Implement basis point commission math with checked arithmetic.\n- Reject operations that overflow `i128::MAX` or lose precision.",
            "criteria": "- [ ] Safe math module implemented with zero panics.\n- [ ] Multi-decimal scaling unit tests pass.\n- [ ] Overflow/underflow assertions verified."
        },
        {
            "title": "feat(escrow): implement asset balance reconciliation query for campaign budgets",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As an auditor, I want to query the total escrowed balance per asset across all active campaigns to reconcile contract token reserves with total campaign obligations.",
            "spec": "- Track `TotalEscrowed(Address)` in instance storage.\n- Update counter on `create_campaign`, `top_up_budget`, `refund_escrow`, and `claim_payout`.\n- Expose `get_total_escrowed(token: Address) -> i128`.",
            "criteria": "- [ ] `TotalEscrowed` tracked in storage.\n- [ ] Invariant holds: total token balance >= total escrowed.\n- [ ] Public query endpoint tested."
        },
        {
            "title": "feat(escrow): add fee-on-transfer asset detection and safety guards",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As a protocol architect, I want the contract to verify the actual received token amount during transfers so that fee-on-transfer or deflationary tokens do not cause escrow accounting insolvency.",
            "spec": "- Query contract balance before and after `client.transfer` in `create_campaign` and `top_up_budget`.\n- Credit only the net received amount to `campaign.budget`.\n- Revert if received amount is less than expected without explicit tolerance.",
            "criteria": "- [ ] Balance delta checked on budget deposits.\n- [ ] Discrepancies cause `Error::TransferAmountMismatch`.\n- [ ] Unit tests verify net balance crediting."
        },
        {
            "title": "feat(escrow): implement dynamic asset whitelist and deprecation management by Admin",
            "labels": "Drips,complexity,complexity: medium,contract,stellar-ecosystem",
            "story": "As a platform admin, I want to whitelist new Stellar asset contracts (SAC) and deprecate decommissioned tokens so that the platform can expand asset support safely.",
            "spec": "- Add `set_asset_status(admin: Address, token: Address, enabled: bool)` entrypoint.\n- Store asset status under `DataKey::AssetStatus(Address)`.\n- Ensure deprecated assets allow existing campaigns to refund/claim but block new campaign creation.",
            "criteria": "- [ ] Admin can enable/disable asset contracts.\n- [ ] Deprecated assets permit claim/refund but block `create_campaign`.\n- [ ] Role authorization verified."
        },
        {
            "title": "feat(oracle): add SEP-0040 price oracle interface for real-time XLM/USD conversion rates",
            "labels": "Drips,complexity,complexity: high,contract,stellar-ecosystem,enhancement",
            "story": "As an advertiser, I want to set campaign budgets in USD terms resolved on-chain via a SEP-0040 compliant price oracle so that fiat-pegged affiliate campaigns remain stable against XLM volatility.",
            "spec": "- Define `PriceOracleClient` interface matching SEP-0040 / Reflector specifications.\n- Store oracle contract address in admin instance storage.\n- Add entrypoint to convert requested USD budget to stroops at time of deposit.",
            "criteria": "- [ ] Oracle contract interface defined.\n- [ ] Mock oracle test verifies conversion rate lookup.\n- [ ] Stale price checks revert with `Error::OraclePriceStale`."
        },
        {
            "title": "feat(escrow): implement multi-currency campaign budget tracking in storage",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As a developer, I want campaign storage structs to record the token address alongside the budget amount so that multi-currency campaigns operate concurrently.",
            "spec": "- Update `Campaign` struct in `storage.rs` with `token: Address` field.\n- Migrate persistent storage deserialization to support versioned campaign records.\n- Ensure `claim_payout` routes transfers through the specific campaign's token client.",
            "criteria": "- [ ] `Campaign.token` field persisted.\n- [ ] `claim_payout` transfers tokens of the specific campaign asset.\n- [ ] Multi-token concurrent tests pass."
        },
        {
            "title": "feat(escrow): add emergency asset recovery function for accidentally sent unsupported tokens",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a platform admin, I want an emergency sweep function to recover tokens erroneously sent to the contract address that are not part of any campaign escrow.",
            "spec": "- Add `emergency_recover_tokens(admin: Address, token: Address, recipient: Address, amount: i128)`.\n- Enforce `admin.require_auth()`.\n- Calculate unallocated surplus = `token_client.balance(&contract) - total_escrowed(token)`.\n- Restrict withdrawal to surplus only.",
            "criteria": "- [ ] Only unallocated surplus can be swept.\n- [ ] Escrowed campaign funds cannot be touched.\n- [ ] Admin auth enforced."
        },
        {
            "title": "feat(escrow): support token allowance pre-authorization pattern alongside direct transfers",
            "labels": "Drips,complexity,complexity: medium,contract,stellar-ecosystem",
            "story": "As an advertiser, I want to deposit escrow funds via `transfer_from` using pre-approved SAC token allowances so that smart wallets and automated contracts can fund campaigns seamlessly.",
            "spec": "- Implement `create_campaign_with_allowance` and `top_up_with_allowance`.\n- Utilize `client.transfer_from(&contract, &advertiser, &contract, &amount)`.\n- Handle allowance expiration errors gracefully.",
            "criteria": "- [ ] `transfer_from` flow implemented for SAC tokens.\n- [ ] Insufficient allowance reverts with clear error.\n- [ ] Allowance deposit tested with mock SAC."
        },
        {
            "title": "feat(escrow): implement automated escrow deficit alert event when budget falls below threshold",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As an advertiser, I want the smart contract to emit an `escrow_low` event when a campaign's remaining budget falls below 20% of its initial budget so that automated bots can trigger a top-up.",
            "spec": "- Store `initial_budget` in `Campaign` struct.\n- In `log_sale`, calculate remaining percentage.\n- If `remaining <= initial_budget / 5`, emit `(\"camp\", symbol_short!(\"low_esc\"))` event.",
            "criteria": "- [ ] `initial_budget` tracked in `Campaign`.\n- [ ] Event emitted when budget crosses low watermark.\n- [ ] Unit test asserts event emission."
        },
        {
            "title": "feat(escrow): add fractional payout precision rounding guardrails for micro-commissions",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an affiliate, I want commission division to never round to 0 stroops on low-value sales so that micro-conversions are fairly compensated without truncation.",
            "spec": "- In commission calculation: `if commission == 0 && sale_amount > 0 { return Err(Error::CommissionTooSmall); }`.\n- Document minimum commissionable sale amounts for given basis points.",
            "criteria": "- [ ] Zero-commission truncation rejected.\n- [ ] Explicit error `CommissionTooSmall` returned.\n- [ ] Boundary tests pass."
        },
        {
            "title": "feat(escrow): support tiered budget deposit milestones with progressive unlocking",
            "labels": "Drips,complexity,complexity: high,contract,enhancement",
            "story": "As an advertiser, I want to deposit escrow in progressive tranches released upon affiliate sales milestones so that working capital is managed efficiently.",
            "spec": "- Add `TrancheConfig { milestone_volume: i128, release_amount: i128 }` to storage.\n- Auto-unlock subsequent tranches when cumulative sales reach milestone volume.\n- Emit milestone unlock events.",
            "criteria": "- [ ] Tranche data structures implemented.\n- [ ] Progressive unlock tested across multi-stage sales.\n- [ ] Unearned tranches remain refundable."
        },
        {
            "title": "feat(escrow): add multi-asset campaign budget breakdown query",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As a frontend integrator, I want an endpoint returning campaign financial health (initial budget, spent, remaining, token address, asset symbol) in a single Soroban call.",
            "spec": "- Implement `get_campaign_financials(campaign_id: u32) -> CampaignFinancials`.\n- Return struct containing `budget`, `spent`, `pending_claims`, `token`.\n- Extend TTL on query.",
            "criteria": "- [ ] Struct `CampaignFinancials` defined.\n- [ ] Public query returns accurate aggregates.\n- [ ] Tested in test suite."
        },
        {
            "title": "feat(escrow): implement asset-specific maximum clearing period limit enforcement",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As an affiliate, I want clearing periods to be capped at a maximum (e.g. 30 days / 2,592,000s) so that advertisers cannot lock affiliate commissions indefinitely.",
            "spec": "- Define `MAX_CLEARING_PERIOD = 2_592_000u32` (30 days).\n- In `create_campaign`, enforce `clearing_period <= MAX_CLEARING_PERIOD`.\n- Return `Error::ClearingPeriodExceedsMax` on violation.",
            "criteria": "- [ ] Max clearing period constant enforced.\n- [ ] Reverts when exceeding 30 days.\n- [ ] Tests verify lower and upper bounds."
        }
    ],

    "Pillar 2: Two-Tier Referral & Commission Architecture": [
        {
            "title": "feat(referral): store parent recruiter address relationship in persistent storage",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an affiliate, I want to register under a parent recruiter address so that our referral relationship is cryptographically recorded on the Stellar ledger.",
            "spec": "- Add `DataKey::Recruiter(Address)` mapping affiliate to parent recruiter.\n- Add entrypoint `register_recruiter(affiliate: Address, recruiter: Address)`.\n- Prevent self-referral (`affiliate != recruiter`).",
            "criteria": "- [ ] Recruiter mapping stored persistently.\n- [ ] Self-referral rejected with `Error::InvalidRecruiter`.\n- [ ] Recruiter lookup helper implemented."
        },
        {
            "title": "feat(referral): calculate automated two-tier commission split upon sale logging",
            "labels": "Drips,complexity,complexity: high,contract,enhancement",
            "story": "As a recruiter, I want the smart contract to automatically calculate and deduct my second-tier commission override from campaign escrow when my sub-affiliate makes a sale.",
            "spec": "- Look up recruiter for `affiliate` in `log_sale`.\n- If recruiter exists, calculate override = `(sale_amount * override_rate) / 10000`.\n- Deduct `affiliate_commission + recruiter_override` from `campaign.budget`.\n- Store separate `Sale` record for recruiter.",
            "criteria": "- [ ] Two-tier split calculated and deducted in `log_sale`.\n- [ ] Both records created in persistent storage.\n- [ ] Budget reflects combined deduction."
        },
        {
            "title": "feat(referral): enforce maximum recruiter override percentage cap invariant (<= 5%)",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As an advertiser, I want recruiter override rates to never exceed 500 basis points (5%) so that campaign budgets are protected from predatory referral fee stacking.",
            "spec": "- Define `MAX_OVERRIDE_BPS: u32 = 500`.\n- In campaign/referral configuration, enforce `override_rate <= MAX_OVERRIDE_BPS`.\n- Revert with `Error::OverrideRateExceedsCap` if exceeded.",
            "criteria": "- [ ] Maximum cap enforced in code.\n- [ ] Violations revert with explicit error.\n- [ ] Unit tests verify cap validation."
        },
        {
            "title": "feat(referral): implement circular referral graph cycle detection guard",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As a security auditor, I want the contract to prevent circular referral loops (e.g. Alice recruited Bob, Bob recruits Alice) so that infinite recursive payouts are impossible.",
            "spec": "- In `register_recruiter`, traverse recruiter ancestors up to 5 hops.\n- If `target == recruiter`, return `Error::CircularReferralDetected`.\n- Fail closed if cycle is found.",
            "criteria": "- [ ] Cycle detection algorithm implemented.\n- [ ] Loops of length 1, 2, and 3 successfully rejected.\n- [ ] Verified with unit tests."
        },
        {
            "title": "feat(referral): add dedicated claim_recruiter_payout entrypoint for sub-affiliate overrides",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As a recruiter, I want a dedicated entrypoint to claim my accumulated second-tier overrides independently of the primary selling affiliate.",
            "spec": "- Add `claim_recruiter_payout(env: Env, recruiter: Address, campaign_id: u32, sub_affiliate: Address)`.\n- Verify clearing period and auditor approval.\n- Transfer override tokens to recruiter and mark claimed.",
            "criteria": "- [ ] Independent recruiter claim entrypoint.\n- [ ] Auth enforced on recruiter address.\n- [ ] Token balance updated and claimed flag set."
        },
        {
            "title": "feat(referral): emit specialized two-tier commission split event on verified conversion",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As an indexer, I want specialized events emitted when a two-tier commission is logged so that off-chain explorers can visualize the referral network tree.",
            "spec": "- Emit `(\"referral\", symbol_short!(\"split\"))` with topics `(campaign_id, affiliate, recruiter)` and data `(direct_comm, override_comm)`.\n- Document event schema in README.",
            "criteria": "- [ ] Event emitted on two-tier sale logging.\n- [ ] Direct and override amounts included.\n- [ ] Snapshot test asserts event structure."
        },
        {
            "title": "feat(referral): implement recruiter address revocation and reassignment by admin/advertiser",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an advertiser, I want the ability to reassign or revoke an abusive recruiter relationship with proper authorization.",
            "spec": "- Add `reassign_recruiter(env: Env, caller: Address, affiliate: Address, new_recruiter: Address)`.\n- Require Advertiser or Admin authorization.\n- Update storage key `DataKey::Recruiter(affiliate)`.",
            "criteria": "- [ ] Reassignment restricted to authorized roles.\n- [ ] Reassigned recruiter applies to future sales.\n- [ ] Existing pending claims remain untouched."
        },
        {
            "title": "feat(referral): add aggregate sub-affiliate volume tracking per recruiter address",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As a recruiter, I want to query the total sales volume generated by my direct sub-affiliates to assess team performance.",
            "spec": "- Track `RecruiterVolume(Address)` in persistent storage.\n- Increment volume upon successful `log_sale`.\n- Expose query `get_recruiter_volume(recruiter: Address) -> i128`.",
            "criteria": "- [ ] Cumulative volume tracked accurately.\n- [ ] Query returns correct sum across sub-affiliates.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(referral): enforce strict 2-tier maximum tree depth invariant in storage",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As a protocol maintainer, I want the contract to enforce a strict maximum depth of 2 tiers so that multi-level pyramid structures are structurally prohibited.",
            "spec": "- Store recruiter depth metadata on registration.\n- If recruiter already has a parent, disallow third-level override deductions.\n- Return `Error::MaxReferralDepthExceeded`.",
            "criteria": "- [ ] Depth limited to direct recruiter only.\n- [ ] Multi-tier MLM structures prevented.\n- [ ] Verified with regression tests."
        },
        {
            "title": "feat(referral): implement separate escrow reserve guarantee for pending recruiter overrides",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a recruiter, I want campaign escrow accounting to reserve funds for my override so that merchant budget top-ups or refunds cannot leave my override unbacked.",
            "spec": "- In `Campaign`, track `reserved_overrides: i128`.\n- In `refund_escrow`, compute refundable amount as `budget - pending_claims - reserved_overrides`.\n- Prevent refunding locked commissions.",
            "criteria": "- [ ] Invariant holds: contract balance >= total pending + reserved overrides.\n- [ ] Refund cannot withdraw reserved override funds.\n- [ ] Accounting verified in unit tests."
        },
        {
            "title": "feat(referral): allow advertisers to set custom recruiter override rates per campaign",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an advertiser, I want to configure the recruiter override basis points at campaign creation instead of using a global protocol default.",
            "spec": "- Add `override_rate: u32` parameter to `create_campaign`.\n- Store `override_rate` in `Campaign` struct.\n- Use campaign-specific rate in `log_sale` calculations.",
            "criteria": "- [ ] Campaign struct stores custom override rate.\n- [ ] Defaults to 0 if no override desired.\n- [ ] Tested with varying campaign rates."
        },
        {
            "title": "feat(referral): add query method to inspect affiliate recruiter and override configuration",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As a frontend developer, I want a query endpoint to fetch an affiliate's recruiter, override percentage, and registration timestamp in a single call.",
            "spec": "- Implement `get_affiliate_recruiter_info(affiliate: Address) -> RecruiterInfo`.\n- Return struct with `recruiter`, `override_rate`, `registered_at`.\n- Handle unrecruited affiliates cleanly.",
            "criteria": "- [ ] `RecruiterInfo` struct returned.\n- [ ] Returns empty/None for organic affiliates.\n- [ ] Query tested in unit suite."
        },
        {
            "title": "feat(referral): support grace period for recruiter claims after campaign closure",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As a recruiter, I want a 14-day grace period after campaign closure to claim all earned overrides before remaining funds are fully liquidated.",
            "spec": "- Store `closed_at: Option<u64>` on campaign closure/refund.\n- Allow `claim_recruiter_payout` during grace period.\n- Revert claim attempts only after grace period expires.",
            "criteria": "- [ ] Grace period timestamp verified.\n- [ ] Claims succeed during grace period.\n- [ ] Claims rejected after expiration with `Error::GracePeriodExpired`."
        },
        {
            "title": "feat(referral): implement batch recruiter override claim method",
            "labels": "Drips,complexity,complexity: high,contract,enhancement",
            "story": "As a large recruiter, I want to claim overrides across multiple sub-affiliates and campaigns in a single transaction to reduce fee overhead.",
            "spec": "- Add `batch_claim_recruiter_payouts(env: Env, recruiter: Address, claims: Vec<(u32, Address)>)`.\n- Iterate through `(campaign_id, sub_affiliate)` tuples.\n- Consolidate token transfers into a single aggregate payment.",
            "criteria": "- [ ] Vector of claims processed in single call.\n- [ ] Consolidated token transfer executed.\n- [ ] Partial failure handling tested."
        },
        {
            "title": "feat(referral): add recruiter tier performance ranking and multiplier logic",
            "labels": "Drips,complexity,complexity: high,contract,enhancement",
            "story": "As an ecosystem manager, I want recruiters who drive over 50,000 XLM in verified volume to earn a 1.2x bonus multiplier on overrides funded from protocol incentives.",
            "spec": "- Define performance tiers based on `RecruiterVolume`.\n- Apply bonus multiplier if recruiter qualifies for VIP tier.\n- Cap total override within protocol limits.",
            "criteria": "- [ ] Tier qualification logic verified.\n- [ ] Multiplier applied only to eligible recruiters.\n- [ ] Verified in test suite."
        }
    ],

    "Pillar 3: Batch Operations, Compression & Merkle Ingestion": [
        {
            "title": "feat(batch): implement log_batch_sales_merkle for bulk off-chain conversion roots",
            "labels": "Drips,complexity,complexity: high,contract,stellar-ecosystem,enhancement",
            "story": "As an advertiser processing thousands of daily sales, I want to anchor a 32-byte Merkle root of sales on Soroban rather than submitting thousands of individual ledger transactions.",
            "spec": "- Add `log_batch_sales_merkle(advertiser: Address, campaign_id: u32, merkle_root: BytesN<32>, total_commissions: i128, sale_count: u32)`.\n- Deduct `total_commissions` from campaign budget upfront into batch escrow.\n- Store root under `DataKey::BatchRoot(campaign_id, batch_id)`.",
            "criteria": "- [ ] Merkle root stored in persistent storage.\n- [ ] Budget deducted and batch escrow reserved.\n- [ ] Event emitted with batch ID and root."
        },
        {
            "title": "feat(batch): implement Merkle proof verification for individual commission claims",
            "labels": "Drips,complexity,complexity: high,contract,security,stellar-ecosystem",
            "story": "As an affiliate included in a batch sale, I want to submit a cryptographic Merkle proof to claim my commission directly against the on-chain root.",
            "spec": "- Implement `claim_merkle_payout(affiliate: Address, campaign_id: u32, batch_id: u32, amount: i128, proof: Vec<BytesN<32>>)`.\n- Verify leaf hash matches Merkle root using sha256.\n- Enforce double-spend protection via leaf nullifier bitmap.",
            "criteria": "- [ ] Cryptographic Merkle proof verifier passes.\n- [ ] Double-claim prevention nullifier verified.\n- [ ] Payout transferred to affiliate."
        },
        {
            "title": "feat(batch): implement batch_claim_payouts for claiming multiple sales in one transaction",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an affiliate with sales across multiple campaigns, I want to claim all cleared payouts in one atomic transaction to minimize wallet interactions.",
            "spec": "- Add `batch_claim_payouts(affiliate: Address, campaign_ids: Vec<u32>)`.\n- Loop through campaigns, verify auditor approval and clearing period.\n- Transfer aggregated commission in a single token transfer.",
            "criteria": "- [ ] Vector of campaign IDs processed.\n- [ ] Single consolidated token transfer executed.\n- [ ] All sales marked claimed atomically."
        },
        {
            "title": "feat(batch): optimize Soroban read/write footprint for multi-sale settlements",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a protocol developer, I want batch methods to use compact footprints so that transaction simulation fees remain well within Stellar ledger resource limits.",
            "spec": "- Refactor storage keys to group related campaign metrics into composite entries.\n- Profile Soroban CPU instructions and RAM usage for 10, 25, and 50 claims.\n- Document ledger footprint footprints.",
            "criteria": "- [ ] Footprint reduction verified via simulation.\n- [ ] Gas/fee benchmarks documented in README.\n- [ ] Resource limits respected."
        },
        {
            "title": "feat(batch): implement bit-packed compact serialization for historical Sale structs",
            "labels": "Drips,complexity,complexity: high,contract,storage",
            "story": "As an architect, I want sale metadata bit-packed into compact byte vectors to reduce persistent storage rent costs over time.",
            "spec": "- Pack timestamp (u40), commission (u64), flags (u8) into compact byte array.\n- Write decoder/encoder functions with unit tests.\n- Maintain backward compatibility with existing storage.",
            "criteria": "- [ ] Struct size reduced by at least 40%.\n- [ ] Serde functions verified with property tests.\n- [ ] Zero data loss on roundtrip."
        },
        {
            "title": "feat(batch): add batch campaign status toggle (pause/resume multiple campaigns)",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As an enterprise advertiser managing 20+ campaigns, I want to pause or resume multiple campaigns simultaneously in an emergency.",
            "spec": "- Implement `batch_set_campaign_status(advertiser: Address, campaign_ids: Vec<u32>, active: bool)`.\n- Verify caller owns all specified campaigns.\n- Update active flags and emit batch status event.",
            "criteria": "- [ ] Batch toggle entrypoint implemented.\n- [ ] Ownership verified across all IDs.\n- [ ] Event emitted with updated IDs."
        },
        {
            "title": "feat(batch): add batch_top_up_budget for multi-campaign advertisers",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an advertiser, I want to replenish budgets across multiple campaigns with varying amounts in one transaction.",
            "spec": "- Add `batch_top_up_budget(advertiser: Address, topups: Vec<(u32, i128)>)`.\n- Calculate total sum, execute single transfer from advertiser.\n- Increment budgets of respective campaigns.",
            "criteria": "- [ ] Single token transfer for total sum.\n- [ ] Individual campaign budgets incremented correctly.\n- [ ] Reverts atomically if any campaign ID invalid."
        },
        {
            "title": "feat(batch): implement batch auditor approvals using bitfield verification",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an auditor, I want to approve up to 64 logged conversions in a single operation using an encoded bitfield to streamline compliance reviews.",
            "spec": "- Add `batch_audit_sales(auditor: Address, campaign_id: u32, affiliates: Vec<Address>)`.\n- Enforce Auditor role.\n- Batch-update `approved_by_auditor = true`.",
            "criteria": "- [ ] Auditor role verified once per batch.\n- [ ] Multiple sales approved atomically.\n- [ ] Audit event emitted."
        },
        {
            "title": "feat(batch): support EIP-712 / SEP-style off-chain signed conversion vouchers",
            "labels": "Drips,complexity,complexity: high,contract,security,stellar-ecosystem",
            "story": "As a merchant with an e-commerce backend, I want to issue Ed25519-signed conversion vouchers so that affiliates can submit and log their own sales trustlessly.",
            "spec": "- Add `log_sale_with_voucher(affiliate: Address, voucher: ConversionVoucher, signature: BytesN<64>)`.\n- Verify signature against advertiser public key using `env.crypto().ed25519_verify`.\n- Prevent replay using nonce bitmap.",
            "criteria": "- [ ] Cryptographic Ed25519 signature verification passes.\n- [ ] Nonce nullifier prevents replay attacks.\n- [ ] Commission logged to affiliate."
        },
        {
            "title": "feat(batch): implement vectorized signature verification for multi-advertiser sales",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As a network aggregator, I want to batch-submit vouchers from distinct advertisers in a single call.",
            "spec": "- Implement vectorized loop validating multiple `(advertiser, voucher, signature)` tuples.\n- Short-circuit on invalid signature or skip failed vouchers with error report.\n- Commit valid conversions.",
            "criteria": "- [ ] Vectorized verification passes.\n- [ ] Invalid signatures isolated.\n- [ ] Tests verify multi-signer batches."
        },
        {
            "title": "feat(batch): add bulk campaign metadata query endpoint to minimize RPC round-trips",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As a frontend developer, I want to query a list of campaign IDs and receive their metadata in an array in a single query.",
            "spec": "- Implement `get_campaigns_bulk(campaign_ids: Vec<u32>) -> Vec<Campaign>`.\n- Skip non-existent IDs gracefully.\n- Extend TTL on accessed entries.",
            "criteria": "- [ ] Bulk query returns array of Campaign structs.\n- [ ] Handles mixed valid/invalid IDs safely.\n- [ ] Unit tests verify bulk query."
        },
        {
            "title": "feat(batch): implement Merkle tree depth and leaf validation constraints",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a protocol engineer, I want Merkle trees bounded to maximum depth of 16 (65,536 sales) to prevent unbounded computation in proof verification.",
            "spec": "- Enforce `proof.len() <= 16` in proof verification.\n- Reject oversized proofs with `Error::MerkleProofTooDeep`.\n- Assert canonical leaf hashing format `sha256(leaf)`.",
            "criteria": "- [ ] Proof length capped at 16 elements.\n- [ ] Oversized proofs rejected immediately.\n- [ ] Canonical hashing validated."
        },
        {
            "title": "feat(batch): add batch sale revocation mechanism for disputed conversions prior to clearing",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an auditor, I want the ability to reject a batch of fraudulent sales before their clearing period concludes, returning the locked commissions to campaign escrow.",
            "spec": "- Add `batch_reject_sales(auditor: Address, campaign_id: u32, affiliates: Vec<Address>)`.\n- Require Auditor role authorization.\n- Credit commission amounts back to `campaign.budget` and delete or mark sales rejected.",
            "criteria": "- [ ] Auditor auth verified.\n- [ ] Commissions refunded back to campaign budget.\n- [ ] Sales marked rejected; cannot be claimed."
        },
        {
            "title": "feat(batch): implement pagination cursors for large campaign sale sets",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an indexer, I want paginated read access to a campaign's sales using a cursor to prevent memory limit exhaustion on large datasets.",
            "spec": "- Implement `get_sales_paginated(campaign_id: u32, start_index: u32, limit: u32) -> Vec<Sale>`.\n- Enforce maximum limit of 50 per page.\n- Return slice of sales.",
            "criteria": "- [ ] Paginated access returns requested slice.\n- [ ] Max page limit enforced.\n- [ ] Cursor boundaries tested."
        },
        {
            "title": "feat(batch): add batch claim failure isolation (partial settlement pattern)",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As an affiliate claiming 10 sales, I want valid sales to succeed even if 1 sale fails clearance so that the entire batch is not blocked.",
            "spec": "- Implement try-catch / Result matching within batch iteration.\n- Return struct `BatchClaimResult { successful: u32, failed: u32, total_claimed: i128 }`.\n- Settle valid claims.",
            "criteria": "- [ ] Partial successes settle cleanly.\n- [ ] Failed claim details returned in result struct.\n- [ ] Comprehensive test with mixed valid/invalid claims."
        }
    ],

    "Pillar 4: Security, Access Control & Circuit Breakers": [
        {
            "title": "feat(security): implement global emergency pause circuit breaker (pause/unpause)",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a security administrator, I want to pause critical protocol state during active exploit detection so that user escrow funds cannot be drained.",
            "spec": "- Add `pause(admin: Address)` and `unpause(admin: Address)` entrypoints.\n- Store boolean under `DataKey::Paused`.\n- Gate `create_campaign`, `top_up_budget`, `log_sale`, and `claim_payout` with `require_not_paused`.",
            "criteria": "- [ ] Admin auth enforced on pause/unpause.\n- [ ] Protocol operations revert with `Error::ProtocolPaused` when paused.\n- [ ] Unit tests cover pause and unpause cycles."
        },
        {
            "title": "feat(security): add advertiser campaign-level pause and unpause controls",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As an advertiser, I want to pause my campaign instantly if my merchant checkout server experiences fraud or downtime.",
            "spec": "- Add `pause_campaign(advertiser: Address, campaign_id: u32)`.\n- Add `resume_campaign(advertiser: Address, campaign_id: u32)`.\n- Revert new sales with `Error::CampaignInactive` when paused.",
            "criteria": "- [ ] Advertiser can pause/resume own campaign.\n- [ ] Logging sales to paused campaign fails.\n- [ ] Existing cleared claims remain payable."
        },
        {
            "title": "feat(security): implement affiliate fraud pause flag to freeze disputed commission claims",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an auditor, I want to flag a suspicious affiliate address so that their pending payouts are frozen while an investigation proceeds.",
            "spec": "- Store `DataKey::AffiliateBlacklist(Address)`.\n- Add `set_affiliate_frozen(auditor: Address, affiliate: Address, frozen: bool)`.\n- Block `claim_payout` if affiliate is frozen.",
            "criteria": "- [ ] Auditor role verified.\n- [ ] Frozen affiliates cannot claim payouts.\n- [ ] Unfreezing restores claim eligibility."
        },
        {
            "title": "feat(security): add timelock delay requirement for critical admin governance parameters",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As a community participant, I want protocol parameter changes (fees, whitelists) subject to a 48-hour timelock delay before taking effect.",
            "spec": "- Implement two-phase commit: `queue_parameter_change` and `execute_parameter_change`.\n- Store proposed change and `executable_after = env.ledger().timestamp() + 172_800`.\n- Revert execution before timelock matures.",
            "criteria": "- [ ] Timelock period enforced.\n- [ ] Premature execution reverts with `Error::TimelockNotMatured`.\n- [ ] Tested with simulated ledger timestamps."
        },
        {
            "title": "feat(security): implement reentrancy protection guard for external token transfer invocations",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a smart contract auditor, I want a reentrancy guard invariant so that malicious token contracts cannot re-enter the escrow during payout execution.",
            "spec": "- Add reentrancy lock in instance storage `DataKey::Locked`.\n- Enforce checks-effects-interactions pattern across all payout functions.\n- Set lock before transfer and clear after transfer.",
            "criteria": "- [ ] State changes committed before external token calls.\n- [ ] Reentrant calls revert with `Error::ReentrancyDetected`.\n- [ ] Formal review passed."
        },
        {
            "title": "feat(security): support contract upgradability via env.deployer().update_current_contract_wasm",
            "labels": "Drips,complexity,complexity: high,contract,security,stellar-ecosystem",
            "story": "As a protocol admin, I want to upgrade the contract WASM bytecode in-place using Soroban native deployer updates without migrating state.",
            "spec": "- Add `upgrade(admin: Address, new_wasm_hash: BytesN<32>)`.\n- Require Admin authorization.\n- Invoke `env.deployer().update_current_contract_wasm(new_wasm_hash)`.",
            "criteria": "- [ ] Upgrade entrypoint implemented.\n- [ ] Restricted exclusively to Admin.\n- [ ] Event emitted with new WASM hash."
        },
        {
            "title": "feat(security): add multi-sig threshold authorization requirement for contract upgrades",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As an institutional user, I want contract upgrades to require M-of-N multi-sig authorization rather than a single private key.",
            "spec": "- Define multi-sig signer threshold in admin storage.\n- Implement proposal and approval collection for upgrades.\n- Execute upgrade only when required approvals are met.",
            "criteria": "- [ ] Multi-sig threshold enforced.\n- [ ] Upgrade rejected with insufficient signatures.\n- [ ] Integration tests verify M-of-N threshold."
        },
        {
            "title": "feat(security): implement strict zero-address and contract-as-affiliate validation guards",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As a contract engineer, I want affiliate addresses checked against zero/null addresses and self-referential addresses to eliminate phantom payouts.",
            "spec": "- In `log_sale`, verify `affiliate != env.current_contract_address()`.\n- Verify `affiliate != advertiser`.\n- Revert with `Error::InvalidAffiliate` if violated.",
            "criteria": "- [ ] Contract address cannot be designated as affiliate.\n- [ ] Advertiser cannot log sale to self.\n- [ ] Guard tests pass."
        },
        {
            "title": "feat(security): enforce storage partition isolation between distinct campaign IDs",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an advertiser, I want absolute cryptographic guarantees that sales logged in Campaign A can never deduct budget from Campaign B.",
            "spec": "- Audit key derivation for `DataKey::Campaign(id)` and `DataKey::Sale(id, affiliate)`.\n- Add invariant assertion verifying campaign budget deductions only match associated sales.\n- Property test invariant with random IDs.",
            "criteria": "- [ ] Storage keys strictly isolated by ID.\n- [ ] Cross-campaign contamination mathematically impossible.\n- [ ] Verified via property tests."
        },
        {
            "title": "feat(security): add rate-limiting counter for rapid-fire sale logging from single advertiser",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a platform protector, I want a rate limiter on sales logged per ledger block per advertiser to mitigate DDoS or runaway bot loops.",
            "spec": "- Track `SalesLoggedThisLedger(Address, u32)` in temporary storage.\n- Enforce maximum 100 sales per block per advertiser.\n- Revert excess sales with `Error::RateLimitExceeded`.",
            "criteria": "- [ ] Temporary counter tracks sales per block.\n- [ ] Resets on next ledger block automatically.\n- [ ] Over-limit requests rejected."
        },
        {
            "title": "feat(security): implement maximum commission rate sanity cap (<= 50%)",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As an advertiser, I want a safety cap on commission rates (e.g. max 5000 bps / 50%) so that fat-finger mistakes during campaign creation do not bankrupt budget escrows.",
            "spec": "- Define `MAX_COMMISSION_BPS: u32 = 5000` (50%).\n- In `create_campaign`, enforce `commission_rate <= MAX_COMMISSION_BPS`.\n- Revert with `Error::CommissionRateExceedsCap`.",
            "criteria": "- [ ] 50% max commission rate enforced.\n- [ ] Campaign creation with 5001 bps rejected.\n- [ ] Boundary tests pass."
        },
        {
            "title": "feat(security): add minimum clearing period threshold (>= 1 hour) to prevent flash claims",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As an advertiser, I want clearing periods to require at least 3,600 seconds (1 hour) so that fraudulent sales cannot be flash-claimed in the same block.",
            "spec": "- Define `MIN_CLEARING_PERIOD = 3_600u32`.\n- In `create_campaign`, enforce `clearing_period >= MIN_CLEARING_PERIOD`.\n- Return `Error::ClearingPeriodTooShort`.",
            "criteria": "- [ ] 1-hour minimum clearing period enforced.\n- [ ] 0-second clearing periods rejected.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(security): implement two-step admin transfer pattern (nominate and accept)",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As the platform founder, I want admin transfers to follow a two-step nominate/accept pattern so that ownership is never lost to a mistyped address.",
            "spec": "- Add `nominate_admin(current_admin: Address, nominated: Address)`.\n- Add `accept_admin(nominated: Address)`.\n- Transfer ownership only when nominated address signs acceptance.",
            "criteria": "- [ ] Two-step admin transfer implemented.\n- [ ] Only nominated address can accept.\n- [ ] Reassignment event emitted."
        },
        {
            "title": "feat(security): add audit trail event logging for all administrative role updates",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As an auditor, I want every role grant and revocation logged with timestamp and target address so that access changes are permanently auditable.",
            "spec": "- In `grant_role`, emit `(\"admin\", symbol_short!(\"role\"))` with `(target, role)`.\n- Document role event indexing guide in README.",
            "criteria": "- [ ] Event emitted on every role grant.\n- [ ] Role transitions traceable in ledger history.\n- [ ] Snapshot test verified."
        },
        {
            "title": "feat(security): implement blacklisted wallet screening interface in entrypoints",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As an enterprise compliance team, I want sanctions-screened addresses blocked at the contract level from creating campaigns or claiming rewards.",
            "spec": "- Add `is_sanctioned(address: Address) -> bool` check in entrypoints.\n- Admin or compliance oracle can update blacklist registry.\n- Deny access with `Error::SanctionedAddress`.",
            "criteria": "- [ ] Blacklist registry stored in storage.\n- [ ] Screened addresses blocked from all write methods.\n- [ ] Compliance test suite verified."
        }
    ],

    "Pillar 5: State Footprint, Rent Archival & TTL Automation": [
        {
            "title": "feat(storage): automate persistent storage TTL extension on active campaign interactions",
            "labels": "Drips,complexity,complexity: low,contract,infra",
            "story": "As a campaign owner, I want every interaction with my campaign to automatically bump its storage TTL so that my campaign never expires while actively running.",
            "spec": "- Add `extend_campaign_ttl` call inside `top_up_budget`, `log_sale`, and `audit_sale`.\n- Bump to at least 100,000 ledgers.\n- Verify storage rent is preserved.",
            "criteria": "- [ ] TTL automatically extended on all active campaign calls.\n- [ ] Expiration risk eliminated for active campaigns.\n- [ ] Simulation tests pass."
        },
        {
            "title": "feat(storage): automate instance storage TTL extension on protocol state calls",
            "labels": "Drips,complexity,complexity: low,contract,infra",
            "story": "As the contract admin, I want instance storage (Admin, Token, CampaignCount) automatically extended on every transaction so that global contract configuration never expires.",
            "spec": "- Add `env.storage().instance().extend_ttl(100_000, 200_000)` in facade functions.\n- Ensure threshold and extension parameters align with Stellar recommendations.",
            "criteria": "- [ ] Instance TTL bumped on protocol calls.\n- [ ] Threshold parameters audited.\n- [ ] Verified via cargo test."
        },
        {
            "title": "feat(storage): implement claimed sale data pruning to temporary storage",
            "labels": "Drips,complexity,complexity: high,contract,infra",
            "story": "As an ecosystem architect, I want claimed and settled sales to be pruned or archived to Temporary storage to minimize persistent ledger rent.",
            "spec": "- Upon successful `claim_payout`, delete persistent `DataKey::Sale` entry.\n- Record receipt hash in temporary storage with 30-day TTL.\n- Save persistent rent for old settled transactions.",
            "criteria": "- [ ] Claimed sales pruned from persistent storage.\n- [ ] Receipt hash verifiable in temporary storage.\n- [ ] Rent cost reduction verified."
        },
        {
            "title": "feat(storage): add closed campaign archival mechanism to eliminate persistent rent overhead",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As an advertiser who has refunded and closed a campaign, I want to archive its state so that ongoing rent is no longer incurred.",
            "spec": "- Implement `archive_campaign(advertiser: Address, campaign_id: u32)`.\n- Verify budget is 0 and no pending claims exist.\n- Remove persistent campaign entry and emit archival event.",
            "criteria": "- [ ] Campaign can be archived when budget is 0.\n- [ ] Persistent entry removed cleanly.\n- [ ] Archival event emitted."
        },
        {
            "title": "feat(storage): implement rent fee estimation helper query for prospective campaigns",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As a frontend user, I want a query endpoint that calculates estimated rent cost for running a campaign for 30, 90, or 365 days.",
            "spec": "- Implement `estimate_rent_cost(duration_ledgers: u32) -> i128`.\n- Base calculation on current Stellar network rent rate per byte.\n- Return stroop estimate.",
            "criteria": "- [ ] Rent estimator implemented.\n- [ ] Estimates scale with requested ledger duration.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(storage): create dedicated extend_campaign_ttl entrypoint for automated keeper bots",
            "labels": "Drips,complexity,complexity: low,contract,infra",
            "story": "As a DevOps engineer, I want a permissionless entrypoint to bump TTL on any campaign so that automated keeper bots can maintain ledger state health.",
            "spec": "- Add public `bump_campaign_ttl(campaign_id: u32)`.\n- Extend persistent TTL by 200,000 ledgers.\n- Anyone can call (permissionless keeper pattern).",
            "criteria": "- [ ] Permissionless TTL bump entrypoint.\n- [ ] Bumps TTL on valid campaign.\n- [ ] Tested with mock ledger."
        },
        {
            "title": "feat(storage): audit and separate Temporary vs Persistent storage across all data keys",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a protocol architect, I want an audit of all `DataKey` entries to ensure ephemeral state uses Temporary storage and immutable state uses Persistent storage.",
            "spec": "- Audit `storage.rs` data keys.\n- Migrate nonces, rate-limit counters, and short-term locks to Temporary storage.\n- Keep campaigns and balances in Persistent storage.",
            "criteria": "- [ ] Temporary storage used for short-lived state.\n- [ ] Persistent storage reserved for financial balances.\n- [ ] Comprehensive audit report in PR."
        },
        {
            "title": "feat(storage): implement compact key hashing scheme to minimize ledger entry byte sizes",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a gas optimizer, I want storage keys represented as short symbols or packed 16-byte hashes rather than verbose enum variants.",
            "spec": "- Refactor `DataKey` enum to minimize discriminant overhead.\n- Benchmark key byte footprint reduction.\n- Update storage accessor helpers.",
            "criteria": "- [ ] Storage key size reduced.\n- [ ] All existing read/write helpers updated.\n- [ ] Benchmarks documented."
        },
        {
            "title": "feat(storage): add automated TTL health inspection query returning remaining ledger blocks",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As a monitoring service, I want to query the exact remaining TTL (in ledgers) of a campaign so that alerting systems can warn of impending expiration.",
            "spec": "- Implement `get_campaign_ttl_status(campaign_id: u32) -> TTLStatus`.\n- Return struct with `live_until_ledger`, `ledgers_remaining`, `health_status`.\n- Handle expired or missing campaigns cleanly.",
            "criteria": "- [ ] `TTLStatus` returned accurately.\n- [ ] Status categorized as Healthy, Warning, or Critical.\n- [ ] Query tested in unit suite."
        },
        {
            "title": "feat(storage): implement batch TTL extension for multi-campaign merchant portfolios",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a keeper bot, I want to extend the TTL on up to 50 campaigns in a single transaction to reduce operational bot transaction fees.",
            "spec": "- Add `batch_bump_campaign_ttl(campaign_ids: Vec<u32>)`.\n- Loop through IDs and extend persistent TTL.\n- Skip non-existent campaigns without failing batch.",
            "criteria": "- [ ] Bulk TTL bump handles up to 50 IDs.\n- [ ] Resilient to missing or closed campaigns.\n- [ ] Unit test verifies batch extension."
        },
        {
            "title": "feat(storage): benchmark Soroban CPU instructions and memory consumption across operations",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a performance engineer, I want automated benchmarks measuring CPU instructions and RAM usage for every contract entrypoint to prevent gas spikes.",
            "spec": "- Create benchmark harness using Soroban SDK metering testutils.\n- Assert CPU instruction limits (< 200,000 instructions per call).\n- Fail CI if CPU instructions regress by > 10%.",
            "criteria": "- [ ] Metering benchmark tests implemented.\n- [ ] Instruction and memory budgets asserted.\n- [ ] Baseline metrics committed to docs."
        },
        {
            "title": "feat(storage): implement stale campaign sweep logic with rent rebate incentive for caller",
            "labels": "Drips,complexity,complexity: high,contract,enhancement",
            "story": "As a community participant, I want to earn a micro-reward for sweeping completely exhausted and inactive campaigns from persistent storage.",
            "spec": "- Add `sweep_closed_campaign(caller: Address, campaign_id: u32)`.\n- Verify campaign has been closed > 90 days with 0 balance.\n- Delete storage entry and award micro-incentive to caller.",
            "criteria": "- [ ] Safe sweep condition verified.\n- [ ] Storage deleted and rent returned.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(storage): optimize string storage by migrating campaign metadata tags to symbol hashes",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a contract engineer, I want campaign tags stored as 32-bit symbol hashes instead of raw UTF-8 strings to save byte rent.",
            "spec": "- Replace string tags in `Campaign` with `Vec<Symbol>`.\n- Limit tags to max 5 symbols per campaign.\n- Validate symbol formats during creation.",
            "criteria": "- [ ] Tags stored as `Symbol` vec.\n- [ ] Storage byte savings measured.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(storage): add storage footprint regression assertions in test suite",
            "labels": "Drips,complexity,complexity: low,contract,infra",
            "story": "As a reviewer, I want tests to assert that data structures do not grow unexpectedly between commits.",
            "spec": "- Write test asserting `core::mem::size_of::<Campaign>()` and `Sale`.\n- Fail test if struct size increases without justification.",
            "criteria": "- [ ] Size assertions active in test suite.\n- [ ] Inadvertent padding or bloating caught in CI.\n- [ ] Documentation updated."
        },
        {
            "title": "feat(storage): implement rent-aware budget top-up calculation",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an advertiser, I want budget top-ups to automatically offset any accrued rent shortfall so that the campaign remains self-sustaining.",
            "spec": "- Calculate required rent fee buffer during `top_up_budget`.\n- Deduct minimal rent deposit if needed and credit remainder to spendable budget.\n- Return breakdown to caller.",
            "criteria": "- [ ] Rent buffer calculation implemented.\n- [ ] Budget reflects net spendable balance.\n- [ ] Unit tests pass."
        }
    ],

    "Pillar 6: Gamification, Badges & Non-Transferable Soulbound Tokens": [
        {
            "title": "feat(sbt): implement non-transferable Soulbound milestone badge minting contract",
            "labels": "Drips,complexity,complexity: high,contract,stellar-ecosystem,enhancement",
            "story": "As a top-performing affiliate, I want to earn an on-chain non-transferable Soulbound badge verifying my sales volume milestones on Stellar.",
            "spec": "- Implement Soulbound token contract standard interface.\n- Support `mint(affiliate: Address, tier: u32)` restricted to StormSale contract.\n- Permanently disallow `transfer` or `transfer_from`.",
            "criteria": "- [ ] Soulbound badge contract created.\n- [ ] Transfers strictly revert with `Error::SoulboundNonTransferable`.\n- [ ] Minting restricted to authorized escrow contract."
        },
        {
            "title": "feat(sbt): add verification criteria for 1K XLM affiliate volume milestone",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an affiliate reaching 1,000 XLM in verified sales volume, I want the contract to authorize minting my Bronze Milestone Badge.",
            "spec": "- Track cumulative claimed volume per affiliate in `storage.rs`.\n- In `claim_payout`, check if cumulative volume >= 1,000 XLM.\n- Trigger badge mint authorization event.",
            "criteria": "- [ ] 1K XLM volume threshold tracked.\n- [ ] Bronze badge eligibility unlocked upon reaching threshold.\n- [ ] Milestone event emitted."
        },
        {
            "title": "feat(sbt): add verification criteria for 10K XLM affiliate volume milestone",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As a veteran affiliate reaching 10,000 XLM in verified sales, I want to earn the Silver Milestone Badge.",
            "spec": "- Check cumulative claimed volume >= 10,000 XLM.\n- Authorize Silver badge tier minting.\n- Prevent duplicate badge minting for same tier.",
            "criteria": "- [ ] 10K XLM threshold verified.\n- [ ] Silver badge minted only once.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(sbt): add verification criteria for 100K XLM affiliate volume milestone",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As an elite affiliate driving over 100,000 XLM in sales volume, I want to unlock the Gold Elite Milestone Badge.",
            "spec": "- Verify cumulative volume >= 100,000 XLM.\n- Mint Gold tier Soulbound token.\n- Emit protocol-wide VIP affiliate event.",
            "criteria": "- [ ] 100K XLM threshold verified.\n- [ ] Gold tier token minted.\n- [ ] Event emitted and tested."
        },
        {
            "title": "feat(sbt): enforce non-transferability invariant (revert on transfer, allow burn)",
            "labels": "Drips,complexity,complexity: low,contract,security",
            "story": "As a reputation auditor, I want badges bound to the earner wallet address forever so that reputation cannot be traded or bought on secondary markets.",
            "spec": "- In SBT token contract, override transfer functions to return `Error::Unauthorized`.\n- Allow affiliate to self-burn badge if desired (`burn`).",
            "criteria": "- [ ] Transfer attempts revert unconditionally.\n- [ ] Self-burn permitted.\n- [ ] Invariant tested with fuzz suite."
        },
        {
            "title": "feat(sbt): implement affiliate badge portfolio query interface",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As a frontend developer, I want a query returning all milestone badges earned by an affiliate address.",
            "spec": "- Implement `get_affiliate_badges(affiliate: Address) -> Vec<BadgeMetadata>`.\n- Return list of badge IDs, tiers, and mint timestamps.\n- Optimize gas footprint.",
            "criteria": "- [ ] Query returns array of earned badges.\n- [ ] Returns empty array for new affiliates.\n- [ ] Tested in test suite."
        },
        {
            "title": "feat(sbt): emit on-chain milestone achievement events with badge token IDs",
            "labels": "Drips,complexity,complexity: low,contract,enhancement",
            "story": "As an off-chain notification service, I want events emitted when badges are minted so that Discord/Telegram bots can announce achievements.",
            "spec": "- Emit `(\"badge\", symbol_short!(\"minted\"))` with `(affiliate, tier, token_id)`.\n- Document payload format in README.",
            "criteria": "- [ ] Event emitted upon successful mint.\n- [ ] Token ID and tier included.\n- [ ] Snapshot test verified."
        },
        {
            "title": "feat(sbt): support advertiser-sponsored custom achievement badge tiers",
            "labels": "Drips,complexity,complexity: high,contract,enhancement",
            "story": "As a brand advertiser, I want to sponsor custom achievement badges for affiliates who drive specific conversion milestones in my campaigns.",
            "spec": "- Add `create_custom_badge(advertiser: Address, campaign_id: u32, threshold: i128, metadata_hash: BytesN<32>)`.\n- Track custom badge eligibility per campaign.\n- Mint custom brand badge upon threshold qualification.",
            "criteria": "- [ ] Advertiser can create custom badges.\n- [ ] Campaign-specific volume qualifies affiliate.\n- [ ] Tested with mock campaign."
        },
        {
            "title": "feat(sbt): implement cryptographic metadata URI resolution for milestone badges",
            "labels": "Drips,complexity,complexity: low,contract,stellar-ecosystem",
            "story": "As an explorer developer, I want badge token IDs to resolve to IPFS/Arweave cryptographic metadata URIs following standard NFT schemas.",
            "spec": "- Implement `token_uri(token_id: u32) -> String`.\n- Return base URI + IPFS CID for designated badge tier.\n- Ensure compliant JSON schema representation.",
            "criteria": "- [ ] `token_uri` returns valid URI string.\n- [ ] IPFS CIDs mapped correctly per tier.\n- [ ] Unit tests pass."
        },
        {
            "title": "feat(sbt): add milestone badge claiming deadline expiration logic",
            "labels": "Drips,complexity,complexity: medium,contract,enhancement",
            "story": "As a campaign organizer, I want seasonal achievement badges to carry a claiming deadline so that limited-edition badges are exclusive.",
            "spec": "- Add optional `claim_deadline: Option<u64>` to badge definition.\n- Revert claim attempts after deadline with `Error::BadgeClaimExpired`.",
            "criteria": "- [ ] Deadline enforced when configured.\n- [ ] Claims succeed before deadline and fail after.\n- [ ] Tested with ledger time travel."
        },
        {
            "title": "feat(sbt): implement Soulbound badge revocation mechanism for fraudulent affiliates",
            "labels": "Drips,complexity,complexity: medium,contract,security",
            "story": "As a platform compliance officer, I want the ability to revoke badges from affiliates found to have conducted ad fraud.",
            "spec": "- Add `revoke_badge(admin: Address, badge_id: u32, reason_code: u32)`.\n- Require Admin or Auditor authorization.\n- Burn badge and emit `(\"badge\", symbol_short!(\"revoked\"))`.",
            "criteria": "- [ ] Only authorized roles can revoke.\n- [ ] Revoked badge removed from affiliate portfolio.\n- [ ] Revocation event logged."
        },
        {
            "title": "feat(sbt): add badge-gated campaign access verification in contract",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As an enterprise advertiser, I want to restrict VIP campaigns so that only affiliates holding a Silver or Gold badge can join.",
            "spec": "- Add `required_badge_tier: Option<u32>` to `Campaign` struct.\n- In `log_sale`, verify affiliate holds required badge tier.\n- Revert unqualified sales with `Error::BadgeRequirementNotMet`.",
            "criteria": "- [ ] Campaign can require minimum badge tier.\n- [ ] Unbadged affiliates rejected.\n- [ ] Badged affiliates accepted cleanly."
        }
    ],

    "Pillar 7: Testing, CI/CD, Fuzzing & Formal Verification": [
        {
            "title": "test(infra): implement property-based testing with proptest for escrow accounting invariants",
            "labels": "Drips,complexity,complexity: high,contract,infra",
            "story": "As a lead developer, I want randomized property tests asserting that contract token balance is always >= sum of all campaign budgets under all sequences of operations.",
            "spec": "- Create `proptest` harness in `test_invariants.rs`.\n- Generate arbitrary sequences of create, top-up, sale, audit, claim, and refund.\n- Assert global solvency invariant holds after every step.",
            "criteria": "- [ ] Proptest suite runs 10,000 iterations.\n- [ ] Zero solvency violations discovered.\n- [ ] Added to CI pipeline."
        },
        {
            "title": "test(infra): add cargo-fuzz harness for Soroban contract entrypoints",
            "labels": "Drips,complexity,complexity: high,contract,security,infra",
            "story": "As a security engineer, I want libFuzzer fuzzing contract entrypoint inputs to identify any potential panics, unexpected reverts, or memory exhaustion.",
            "spec": "- Set up `fuzz/` directory with `cargo fuzz`.\n- Define fuzz targets for `create_campaign`, `log_sale`, and `claim_payout`.\n- Run continuous fuzzing in CI workflow.",
            "criteria": "- [ ] `cargo-fuzz` targets configured and passing.\n- [ ] No panics or unhandled exceptions under corrupt inputs.\n- [ ] Fuzzing documentation added to CONTRIBUTING.md."
        },
        {
            "title": "test(infra): implement 100% error code branch coverage test suite in test.rs",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a QA lead, I want every single error enum variant in `errors.rs` triggered by at least one dedicated negative unit test.",
            "spec": "- Audit all 11 error codes in `errors.rs`.\n- Add unit tests triggering each specific error variant.\n- Assert exact `Err(Ok(Error::<Variant>))` matches.",
            "criteria": "- [ ] Every error enum code has dedicated test.\n- [ ] 100% error branch coverage achieved.\n- [ ] Verified via `cargo test`."
        },
        {
            "title": "test(infra): create differential testing suite comparing contract math against Python reference",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a mathematician, I want commission calculation outputs cross-checked against a Python reference model across 100,000 random inputs to ensure identical rounding.",
            "spec": "- Implement Python reference script matching Soroban integer math.\n- Generate test vector JSON with inputs and expected outputs.\n- Assert Rust implementation matches JSON test vectors exactly.",
            "criteria": "- [ ] 100,000 test vectors verified.\n- [ ] Zero rounding divergence observed.\n- [ ] Test harness committed."
        },
        {
            "title": "ci(infra): add automated GitHub Actions workflow for cargo clippy with zero warnings",
            "labels": "Drips,complexity,complexity: low,contract,infra",
            "story": "As a maintainer, I want CI to enforce `cargo clippy -- -D warnings` on every pull request to maintain pristine Rust code quality.",
            "spec": "- Update `.github/workflows/ci.yml`.\n- Add Clippy step with `--all-targets -- -D warnings`.\n- Fail PR checks on any lint warning.",
            "criteria": "- [ ] Clippy workflow active in CI.\n- [ ] Zero warnings on current main branch.\n- [ ] PR validation passes."
        },
        {
            "title": "ci(infra): add automated WebAssembly size profiling and budget limit gate in CI",
            "labels": "Drips,complexity,complexity: low,contract,infra",
            "story": "As a smart contract engineer, I want CI to build `stormsale.wasm` and verify the binary size remains under 64 KB to ensure ultra-low deployment fees.",
            "spec": "- Add size check script in `.github/workflows/ci.yml`.\n- Measure release wasm binary size.\n- Fail build if size exceeds 65,536 bytes.",
            "criteria": "- [ ] WASM size measured and posted to PR summary.\n- [ ] Fails build if binary exceeds 64 KB limit.\n- [ ] Size optimization docs added."
        },
        {
            "title": "test(infra): implement formal verification specs for campaign budget non-negativity",
            "labels": "Drips,complexity,complexity: high,contract,security",
            "story": "As a cryptographic auditor, I want mathematical proof that `campaign.budget` can never transition below 0 under any possible ledger sequence.",
            "spec": "- Write formal inductive proof specification.\n- Use Kani or Prusti Rust formal verification tooling.\n- Formally verify non-negativity invariant.",
            "criteria": "- [ ] Formal verification harness configured.\n- [ ] Budget >= 0 proven mathematically.\n- [ ] Verification report committed to Docs."
        },
        {
            "title": "test(infra): create multi-agent simulation test simulating 1,000 concurrent affiliate claims",
            "labels": "Drips,complexity,complexity: high,contract,infra",
            "story": "As a scalability engineer, I want a simulation test modeling 1,000 concurrent affiliates claiming payouts against 50 campaigns simultaneously.",
            "spec": "- Write simulation test in `test_simulation.rs`.\n- Populate 50 campaigns and 1,000 affiliates.\n- Process concurrent sales and claims; assert total token accounting reconciles to zero delta.",
            "criteria": "- [ ] 1,000 concurrent claims simulated cleanly.\n- [ ] Final balances match expected values to the stroop.\n- [ ] Performance profiled."
        },
        {
            "title": "test(infra): add automated Stellar Testnet deployment and initialization integration script",
            "labels": "Drips,complexity,complexity: low,contract,stellar-ecosystem",
            "story": "As a deployment engineer, I want an idempotent bash/Python script that deploys `stormsale.wasm` to Stellar Testnet and runs initialization in one command.",
            "spec": "- Create `scripts/deploy_testnet.sh`.\n- Use `stellar keys`, `stellar contract deploy`, and `stellar contract invoke`.\n- Output deployed contract ID to `.env`.",
            "criteria": "- [ ] Script deploys and initializes contract on Testnet.\n- [ ] Idempotent re-run handling.\n- [ ] Tested and documented in README."
        },
        {
            "title": "ci(infra): configure cargo audit vulnerability scanning in daily GitHub Actions cron",
            "labels": "Drips,complexity,complexity: low,contract,security,infra",
            "story": "As a security manager, I want automated dependency audits running daily to detect any newly disclosed CVEs in Cargo dependencies.",
            "spec": "- Add `.github/workflows/security-audit.yml`.\n- Run `cargo audit` on daily cron schedule and on PRs modifying `Cargo.lock`.\n- Alert maintainers on discovered vulnerabilities.",
            "criteria": "- [ ] Security audit workflow configured.\n- [ ] Zero active vulnerabilities on current Cargo.lock.\n- [ ] Daily cron active."
        },
        {
            "title": "test(infra): implement simulated network latency and reorg resilience tests",
            "labels": "Drips,complexity,complexity: high,contract,infra",
            "story": "As a Web3 developer, I want contract behavior verified against out-of-order ledger timestamps and sequence number jumps.",
            "spec": "- Write test cases in `test.rs` manipulating `env.ledger().set(...)` with extreme timestamp shifts.\n- Verify clearing periods and deadlines evaluate strictly based on ledger timestamp.",
            "criteria": "- [ ] Out-of-order ledger tests pass.\n- [ ] Timestamp boundary conditions verified.\n- [ ] Edge cases handled cleanly."
        },
        {
            "title": "docs(infra): generate automated Soroban contract API documentation with cargo doc",
            "labels": "Drips,complexity,complexity: low,contract,documentation",
            "story": "As an external integrator, I want comprehensive Rustdoc API documentation generated and published to GitHub Pages.",
            "spec": "- Add full doc-comments (`///`) to all public functions in `lib.rs`.\n- Configure GitHub Actions to run `cargo doc --no-deps`.\n- Deploy HTML documentation to GitHub Pages.",
            "criteria": "- [ ] 100% public item doc-comment coverage.\n- [ ] `cargo doc` builds without broken links.\n- [ ] Published to GitHub Pages."
        },
        {
            "title": "ci(infra): add automated snapshot testing workflow for contract invocation XDRs",
            "labels": "Drips,complexity,complexity: medium,contract,infra",
            "story": "As a protocol maintainer, I want CI to assert that serialized invocation XDRs match committed snapshot files so that ABI breaks are immediately detected.",
            "spec": "- Use Soroban SDK snapshot testing features.\n- Commit snapshots in `contracts/stormsale/test_snapshots/`.\n- CI fails if invocation XDRs change without explicit snapshot update.",
            "criteria": "- [ ] Snapshot test step active in CI.\n- [ ] Inadvertent ABI breaks detected automatically.\n- [ ] Snapshot update instructions documented."
        }
    ]
}

total_issues = sum(len(v) for v in pillars.values())
print(f"Total issues defined: {total_issues}")

# Write Markdown guide
guide_path = "/home/abujulaybeeb/Documents/Storm/issues/contract_100_production_issues.md"
with open(guide_path, "w") as f:
    f.write("# ⚡ StormSale Smart Contract: 100 Production Issues Roadmap\n\n")
    f.write("This roadmap establishes 100 production-grade issues for the `StormSale/Storm-Contract` repository to migrate the Soroban smart contracts beyond MVP into a commercial, hardened protocol.\n\n---\n\n")
    
    count = 1
    # Issue #1 already existed, #9 was the first created in this run
    for pillar_name, issue_list in pillars.items():
        f.write(f"## {pillar_name}\n\n")
        for item in issue_list:
            f.write(f"### #{count}: {item['title']}\n")
            f.write(f"- **Labels:** `{item['labels']}`\n")
            f.write(f"- **User Story:** {item['story']}\n")
            f.write(f"- **Technical Specification:**\n{item['spec']}\n")
            f.write(f"- **Acceptance Criteria:**\n{item['criteria']}\n\n")
            count += 1

print(f"Wrote {guide_path}")

# Create issues via gh issue create
print("Creating issues on GitHub via gh CLI...")
created_count = 0
for pillar_name, issue_list in pillars.items():
    print(f"\n--- Processing {pillar_name} ---")
    for item in issue_list:
        body = f"### User Story\n{item['story']}\n\n### Technical Specification\n{item['spec']}\n\n### Acceptance Criteria\n{item['criteria']}"
        cmd = [
            "gh", "issue", "create",
            "--repo", "StormSale/Storm-Contract",
            "--title", item["title"],
            "--label", item["labels"],
            "--body", body
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            url = res.stdout.strip()
            created_count += 1
            print(f"[{created_count}/{total_issues}] Created: {url}")
            time.sleep(1) # respectful rate-limiting
        except subprocess.CalledProcessError as e:
            print(f"Error creating issue '{item['title']}': {e.stderr}")
            time.sleep(3)

print(f"\nSuccessfully created {created_count} issues on GitHub!")
