use soroban_sdk::{contracttype, Address, Env};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum DataKey {
    Admin,
    Role(Address),
    Token,
    CampaignCount,
    Campaign(u32),
    Sale(u32, Address),
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RoleType {
    Admin,
    Advertiser,
    Affiliate,
    Auditor,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Campaign {
    pub id: u32,
    pub advertiser: Address,
    pub commission_rate: u32, // e.g., 500 = 5%
    pub clearing_period: u32, // seconds until a payout can be claimed
    pub budget: i128,         // remaining escrow budget locked in the contract
    pub active: bool,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Sale {
    pub amount: i128,
    pub commission: i128,
    pub timestamp: u64,
    pub claimed: bool,
    pub approved_by_auditor: bool,
}

pub const LEDGER_THRESHOLD: u32 = 100_000;
pub const LEDGER_EXTEND: u32 = 200_000;

// Helpers
pub fn get_token_address(env: &Env) -> Option<Address> {
    env.storage()
        .instance()
        .extend_ttl(LEDGER_THRESHOLD, LEDGER_EXTEND);
    env.storage().instance().get(&DataKey::Token)
}

pub fn get_campaign(env: &Env, id: u32) -> Option<Campaign> {
    let key = DataKey::Campaign(id);
    if env.storage().persistent().has(&key) {
        env.storage()
            .persistent()
            .extend_ttl(&key, LEDGER_THRESHOLD, LEDGER_EXTEND);
    }
    env.storage().persistent().get(&key)
}

pub fn set_campaign(env: &Env, id: u32, campaign: &Campaign) {
    let key = DataKey::Campaign(id);
    env.storage().persistent().set(&key, campaign);
    env.storage()
        .persistent()
        .extend_ttl(&key, LEDGER_THRESHOLD, LEDGER_EXTEND);
}

pub fn get_sale(env: &Env, campaign_id: u32, affiliate: &Address) -> Option<Sale> {
    let key = DataKey::Sale(campaign_id, affiliate.clone());
    if env.storage().persistent().has(&key) {
        env.storage()
            .persistent()
            .extend_ttl(&key, LEDGER_THRESHOLD, LEDGER_EXTEND);
    }
    env.storage().persistent().get(&key)
}

pub fn set_sale(env: &Env, campaign_id: u32, affiliate: &Address, sale: &Sale) {
    let key = DataKey::Sale(campaign_id, affiliate.clone());
    env.storage().persistent().set(&key, sale);
    env.storage()
        .persistent()
        .extend_ttl(&key, LEDGER_THRESHOLD, LEDGER_EXTEND);
}
