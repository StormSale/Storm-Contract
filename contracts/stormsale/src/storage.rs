
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

// Helpers
pub fn get_token_address(env: &Env) -> Option<Address> {
    env.storage().instance().get(&DataKey::Token)
}

pub fn get_campaign(env: &Env, id: u32) -> Option<Campaign> {
    env.storage().persistent().get(&DataKey::Campaign(id))
}

pub fn set_campaign(env: &Env, id: u32, campaign: &Campaign) {
    env.storage().persistent().set(&DataKey::Campaign(id), campaign);
}

pub fn get_sale(env: &Env, campaign_id: u32, affiliate: &Address) -> Option<Sale> {
    env.storage().persistent().get(&DataKey::Sale(campaign_id, affiliate.clone()))
}

pub fn set_sale(env: &Env, campaign_id: u32, affiliate: &Address, sale: &Sale) {
    env.storage().persistent().set(&DataKey::Sale(campaign_id, affiliate.clone()), sale);
}
