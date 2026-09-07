# Smart Contract Security Policy

## Scope

This security policy covers the Soroban smart contracts in the `Storm-Contract` repository (`contracts/stormsale`).

---

## Reporting Security Vulnerabilities

If you discover a smart contract vulnerability (e.g., reentrancy, authorization bypass, token escrow drain, integer overflow, or storage griefing), please notify us immediately through responsible disclosure:

- **Security Contact**: `abujulaybeeb08@gmail.com`
- **Emergency Telegram**: Contact `@AJDEV_Official` (or repo maintainers)
- **Do NOT disclose publicly** or exploit testnet/mainnet contracts.

---

## Security Best Practices Followed

- **Strict Access Control**: Every state change checks caller authorization via `address.require_auth()`.
- **Budget Escrow Boundaries**: Payouts are mathematically capped to the remaining campaign budget.
- **Stateless Facade**: Logic delegation prevents cross-module state inconsistency.
- **Audit Logging**: Contract events are emitted on campaign creation, sale logging, and payout settlements.
