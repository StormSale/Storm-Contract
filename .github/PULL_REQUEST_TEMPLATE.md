## Description

<!-- Briefly describe the changes introduced by this pull request. -->

## Linked Issue

Closes #<!-- Issue number if applicable -->

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change adding Soroban functionality)
- [ ] 💥 Breaking change (fix or feature causing existing functionality/storage to break)
- [ ] ⚡ Performance optimization (gas / CPU instruction reduction)
- [ ] 🧪 Tests (adding missing tests or fixing existing tests)
- [ ] 📚 Documentation update

## Soroban Contract Checklist

- [ ] All code adheres to project formatting (`cargo fmt --check`)
- [ ] Zero compiler/clippy warnings (`cargo clippy --all-targets -- -D warnings`)
- [ ] All unit and integration tests pass (`cargo test`)
- [ ] WASM target builds cleanly (`soroban contract build` or `cargo build --target wasm32-unknown-unknown --release`)
- [ ] Auth checks (`env.require_auth(...)`) are strictly verified on state-modifying functions
- [ ] Contract storage keys and TTL bumps are appropriately handled
- [ ] Reentrancy and unauthorized state modifications evaluated

## Verification & Testing

<!-- Detail the exact steps/commands executed to verify changes -->
```bash
cargo test
cargo clippy --all-targets
```
