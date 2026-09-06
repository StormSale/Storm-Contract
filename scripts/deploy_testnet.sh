#!/usr/bin/env bash
set -e

# ==============================================================================
# StormSale Soroban Contract Testnet Deployment & Initialization Script
# ==============================================================================

NETWORK="testnet"
RPC_URL="https://soroban-testnet.stellar.org"
NETWORK_PASSPHRASE="Test SDF Network ; September 2015"
NATIVE_XLM_SAC="CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC"
ACCOUNT_NAME="${STELLAR_ACCOUNT:-stormsale-deployer}"

echo "========================================================"
echo "⚡ StormSale Soroban Deployment: ${NETWORK}"
echo "========================================================"

# Check for Stellar CLI
if ! command -v stellar &> /dev/null; then
    echo "❌ stellar CLI could not be found."
    echo "👉 Install with: cargo install --locked stellar-cli --features opt"
    exit 1
fi

# 1. Ensure Deployer Account Exists on Testnet
echo "🔑 Verifying deployer account identity: ${ACCOUNT_NAME}..."
if ! stellar keys address "${ACCOUNT_NAME}" &> /dev/null; then
    echo "Creating and funding new testnet identity: ${ACCOUNT_NAME}..."
    stellar keys generate --network "${NETWORK}" "${ACCOUNT_NAME}" --fund
else
    echo "Deployer address: $(stellar keys address "${ACCOUNT_NAME}")"
fi

DEPLOYER_ADDRESS=$(stellar keys address "${ACCOUNT_NAME}")

# 2. Build WebAssembly Binary
echo "🔨 Compiling contract to wasm32-unknown-unknown..."
cargo build --manifest-path contracts/stormsale/Cargo.toml --target wasm32-unknown-unknown --release

WASM_PATH="target/wasm32-unknown-unknown/release/stormsale.wasm"

if [ ! -f "${WASM_PATH}" ]; then
    echo "❌ Compiled WASM not found at ${WASM_PATH}"
    exit 1
fi

# 3. Deploy Contract to Testnet
echo "🚀 Deploying WASM to Stellar Testnet..."
CONTRACT_ID=$(stellar contract deploy \
  --wasm "${WASM_PATH}" \
  --source "${ACCOUNT_NAME}" \
  --network "${NETWORK}")

echo "✅ Contract Deployed Successfully!"
echo "📄 Contract ID: ${CONTRACT_ID}"

# 4. Initialize Contract
echo "⚙️ Initializing StormSale contract..."
stellar contract invoke \
  --id "${CONTRACT_ID}" \
  --source "${ACCOUNT_NAME}" \
  --network "${NETWORK}" \
  -- \
  init \
  --admin "${DEPLOYER_ADDRESS}" \
  --token "${NATIVE_XLM_SAC}"

echo "✅ Contract Initialized with Admin: ${DEPLOYER_ADDRESS} and Token SAC: ${NATIVE_XLM_SAC}"

# 5. Save Contract ID to JSON registries
mkdir -p .stellar/contract-ids
cat <<EOF > .stellar/contract-ids/testnet.json
{
  "network": "testnet",
  "rpcUrl": "${RPC_URL}",
  "networkPassphrase": "${NETWORK_PASSPHRASE}",
  "admin": "${DEPLOYER_ADDRESS}",
  "contracts": {
    "stormsale_escrow": "${CONTRACT_ID}",
    "native_xlm_sac": "${NATIVE_XLM_SAC}"
  }
}
EOF

echo "💾 Saved to .stellar/contract-ids/testnet.json"

# Sync with frontend repo if present
if [ -d "../StormSale/.stellar/contract-ids" ]; then
    cp .stellar/contract-ids/testnet.json ../StormSale/.stellar/contract-ids/testnet.json
    echo "🔄 Synced contract ID to StormSale frontend configuration!"
fi

echo "========================================================"
echo "🎉 Deployment complete! View on Stellar Expert:"
echo "👉 https://stellar.expert/explorer/testnet/contract/${CONTRACT_ID}"
echo "========================================================"
