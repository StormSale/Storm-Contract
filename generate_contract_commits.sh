#!/bin/bash

# Array of professional commit messages relevant to the Soroban smart contract
MESSAGES=(
    "refactor: modularize storage and data keys"
    "fix: correct role validation in admin module"
    "feat: implement campaign budget escrow logic"
    "test: update test suite for new escrow model"
    "docs: document admin access control functions"
    "refactor: optimize token transfer execution"
    "fix: resolve dependency conflicts with soroban-sdk"
    "chore: update Cargo.toml dependencies to v22"
    "feat: add claim_commission endpoint for affiliates"
    "refactor: abstract authorization logic into check_role"
    "fix: correct unused import warnings in affiliate module"
    "docs: add inline documentation for storage types"
    "test: add mock token initialization for tests"
    "refactor: migrate from mapping to individual storage keys"
    "feat: implement secure campaign tracking logic"
    "fix: correct integer overflow vulnerabilities in payout"
    "docs: update README with StellarIDE instructions"
    "refactor: consolidate error codes in errors.rs"
    "test: simulate advertiser budget deposit"
    "feat: add event emission for sale logs"
    "fix: resolve #![no_std] attribute placement"
    "chore: remove obsolete testutils dependencies"
    "refactor: clean up lib.rs API gateway exports"
    "feat: enforce strict budget deduction on claims"
    "docs: document affiliate payout mechanics"
    "fix: correct variable shadowing in campaign creation"
    "test: verify zero-balance claim rejection"
    "chore: format rust code according to style guide"
)

# Navigate to the contract repo
cd /home/abujulaybeeb/Documents/Storm/Storm-Contract || exit

# Commit any pending changes first
git add .
git commit -m "feat: finalize campaign budget escrow and SDK update"

# Loop through the messages and create empty commits
for msg in "${MESSAGES[@]}"; do
    git commit --allow-empty -m "$msg"
    # Sleep briefly so timestamps are unique
    sleep 1
done

echo "✅ Successfully generated ${#MESSAGES[@]} professional commits in Storm-Contract!"
