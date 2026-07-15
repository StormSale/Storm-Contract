#![no_std]
use soroban_sdk::{contracttype, Address};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum DataKey {
    /// The admin of the StormSale platform
    Admin,
    /// Store a specific role status for an address (Address, RoleType)
    Role(Address),
    /// XLM Token address (SAC)
    Token,
    /// Global counter for Campaigns
    CampaignCount,
    /// Campaign metadata by ID
    Campaign(u32),
    /// Tracks sales: Campaign ID, Affiliate Address -> Sale Struct
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
