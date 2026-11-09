import subprocess, time

b2b_b2c_issues = [
    {
        "title": "feat(b2b): implement multi-seat operator permission matrix (Manager, Billing, Analyst) in storage",
        "labels": "Drips,complexity,complexity: high,contract,security",
        "body": """### User Story
As an enterprise B2B merchant, I want to assign granular operator capabilities (e.g. SalesLogger, EscrowManager, Viewer) to team member addresses rather than all-or-nothing operator access.

### Technical Specification
- Define `OperatorCapability` bitflags or enum in `storage.rs`.
- Store capabilities under `DataKey::OperatorCapabilities(campaign_id, operator)`.
- Enforce capability checks in `log_sale`, `top_up_budget`, and `refund_escrow`.

### Acceptance Criteria
- [ ] Granular operator capabilities stored in contract.
- [ ] `set_operator_capabilities(advertiser, campaign_id, operator, capabilities)` implemented.
- [ ] Unauthorized actions by scoped operators revert with `Error::Unauthorized`."""
    },
    {
        "title": "feat(b2c): implement instant micro-commission claim fast-track for verified B2C creator affiliates",
        "labels": "Drips,complexity,complexity: medium,contract,enhancement",
        "story": "As a verified B2C creator, I want micro-commissions (< 50 XLM) to bypass manual auditor waiting queues and settle instantly so that creator liquidity is immediate.",
        "body": """### User Story
As a verified B2C creator, I want micro-commissions (< 50 XLM) to bypass manual auditor waiting queues and settle instantly so that creator liquidity is immediate.

### Technical Specification
- Store `micro_payout_threshold: i128` on B2C campaigns.
- In `claim_payout`, if `sale.commission <= micro_payout_threshold` and `campaign.audience == AudienceType::B2C`, auto-approve audit check.
- Require merchant opt-in during campaign creation.

### Acceptance Criteria
- [ ] B2C micro-payout threshold supported in `Campaign`.
- [ ] Micro-commissions claimable without explicit `audit_sale` call.
- [ ] Unit tests verify auto-clearance threshold."""
    },
    {
        "title": "feat(b2b): support corporate tax invoicing hash and business legal metadata anchoring on-chain",
        "labels": "Drips,complexity,complexity: low,contract,enhancement",
        "body": """### User Story
As a B2B finance department, I want monthly sales payouts to anchor an immutable SHA-256 invoice receipt hash on-chain for corporate audit compliance (1099-DA).

### Technical Specification
- Add entrypoint `anchor_invoice_receipt(advertiser: Address, campaign_id: u32, invoice_hash: BytesN<32>, period_month: u32)`.
- Store receipt under `DataKey::InvoiceReceipt(campaign_id, period_month)`.
- Emit invoice anchored event with URI hash.

### Acceptance Criteria
- [ ] Invoice hash stored in persistent storage.
- [ ] Advertiser auth enforced.
- [ ] Public query `get_invoice_receipt` implemented."""
    },
    {
        "title": "feat(b2c): implement creator tipping and performance micro-bonus distribution entrypoint",
        "labels": "Drips,complexity,complexity: medium,contract,enhancement",
        "body": """### User Story
As an advertiser running a B2C campaign, I want to reward a standout creator with a direct one-off performance tip/bonus transferred instantly from escrow.

### Technical Specification
- Add `reward_creator_bonus(advertiser: Address, campaign_id: u32, creator: Address, bonus_amount: i128, memo: Symbol)` entrypoint.
- Deduct bonus directly from campaign budget.
- Transfer tokens immediately to creator wallet and emit celebratory event.

### Acceptance Criteria
- [ ] Bonus deducted from campaign escrow and transferred directly to creator.
- [ ] Event `(\"creator\", symbol_short!(\"bonus\"))` emitted.
- [ ] Fails if campaign budget is insufficient."""
    },
    {
        "title": "feat(b2b): add net-term settlement escrow schedules (Net-15/Net-30) for enterprise B2B sales cycles",
        "labels": "Drips,complexity,complexity: high,contract,enhancement",
        "body": """### User Story
As an enterprise B2B merchant with long sales cycles, I want to configure Net-15 or Net-30 settlement escrow schedules where commissions release in tranches following invoice clearance.

### Technical Specification
- Support `NetTermSchedule { net_days: u32, auto_release_after: u64 }` in campaign config.
- Hold funds in staged clearing tranches.
- Release funds upon maturity or manual dispute window clearance.

### Acceptance Criteria
- [ ] Net-term schedule model implemented in `storage.rs`.
- [ ] Staged clearing tested against simulated ledger time.
- [ ] Invariant holds: scheduled funds cannot be claimed prematurely."""
    },
    {
        "title": "feat(b2c): add social handle hash verification for B2C creator onboarding and identity binding",
        "labels": "Drips,complexity,complexity: medium,contract,stellar-ecosystem",
        "body": """### User Story
As a B2C creator affiliate, I want to bind my verified X/Telegram/TikTok handle hash to my wallet on-chain so that advertisers know who is promoting their product.

### Technical Specification
- Add entrypoint `bind_creator_handle(creator: Address, platform: Symbol, handle_hash: BytesN<32>)`.
- Store mapping `DataKey::CreatorHandle(creator, platform) -> BytesN<32>`.
- Allow advertisers to query creator social credentials on-chain.

### Acceptance Criteria
- [ ] Creator handle hash stored in persistent storage.
- [ ] Creator authorization enforced.
- [ ] Query helper `get_creator_handle` tested."""
    }
]

print("Creating B2B & B2C targeted issues...")
for issue in b2b_b2c_issues:
    cmd = [
        "gh", "issue", "create",
        "--repo", "StormSale/Storm-Contract",
        "--title", issue["title"],
        "--label", issue["labels"],
        "--body", issue["body"]
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print("Created:", res.stdout.strip())
    time.sleep(1)

print("All B2B & B2C contract issues created successfully!")
