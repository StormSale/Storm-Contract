#!/bin/bash

# Create the pre-commit hook file
cat << 'EOF' > .git/hooks/pre-commit
#!/bin/bash
# Pre-commit hook to run cargo fmt and cargo clippy

echo "🦀 Running Cargo Fmt..."
cd contracts/stormsale || exit
cargo fmt -- --check
if [ $? -ne 0 ]; then
    echo "❌ Code format check failed! Run 'cargo fmt' inside contracts/stormsale to fix it."
    exit 1
fi

echo "🦀 Running Cargo Clippy..."
cargo clippy --all-targets --all-features -- -D warnings
if [ $? -ne 0 ]; then
    echo "❌ Clippy found warnings or errors! Please fix them before committing."
    exit 1
fi

echo "✅ All checks passed! Committing..."
exit 0
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully! Every commit will now be automatically linted and formatted using Rust's Clippy and Fmt."
