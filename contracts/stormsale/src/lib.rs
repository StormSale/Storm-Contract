#![no_std]

mod admin;
mod affiliate;
mod campaign;
mod errors;
mod storage;

#[cfg(test)]
mod test;

use errors::Error;
use soroban_sdk::{contract, contractimpl, Address, Env};
use storage::{Campaign, RoleType, Sale};

#[contract]
pub struct StormSaleContract;

#[contractimpl]
impl StormSaleContract {
    /// Initialize the contract with an admin and the XLM token address
    pub fn init(env: Env, admin: Address, token: Address) -> Result<(), Error> {
        admin::init(env, admin, token)
    }

    /// Grant a role to an address (Admin only)
    pub fn grant_role(
        env: Env,
        admin: Address,
        target: Address,
        role: RoleType,
    ) -> Result<(), Error> {
        admin::grant_role(env, admin, target, role)
    }

    /// Create a new affiliate campaign (Advertiser only)
    pub fn create_campaign(
        env: Env,
        advertiser: Address,
        commission_rate: u32,
        clearing_period: u32,
        budget: i128,
    ) -> Result<u32, Error> {
        campaign::create_campaign(env, advertiser, commission_rate, clearing_period, budget)
    }

    /// Top up the budget of an existing campaign (Advertiser only)
    pub fn top_up_budget(
        env: Env,
        advertiser: Address,
        campaign_id: u32,
        amount: i128,
    ) -> Result<(), Error> {
        campaign::top_up_budget(env, advertiser, campaign_id, amount)
    }

    /// Log a sale (Advertiser only)
    pub fn log_sale(
        env: Env,
        advertiser: Address,
        campaign_id: u32,
        affiliate: Address,
        amount: i128,
    ) -> Result<(), Error> {
        affiliate::log_sale(env, advertiser, campaign_id, affiliate, amount)
    }

    /// Auditor approves a sale
    pub fn audit_sale(
        env: Env,
        auditor: Address,
        campaign_id: u32,
        affiliate: Address,
    ) -> Result<(), Error> {
        affiliate::audit_sale(env, auditor, campaign_id, affiliate)
    }

    /// Affiliate claims payout
    pub fn claim_payout(env: Env, affiliate: Address, campaign_id: u32) -> Result<(), Error> {
        affiliate::claim_payout(env, affiliate, campaign_id)
    }

    /// Get campaign metadata
    pub fn get_campaign(env: Env, campaign_id: u32) -> Result<Campaign, Error> {
        storage::get_campaign(&env, campaign_id).ok_or(Error::CampaignNotFound)
    }

    /// Get sale metadata
    pub fn get_sale(env: Env, campaign_id: u32, affiliate: Address) -> Result<Sale, Error> {
        storage::get_sale(&env, campaign_id, &affiliate).ok_or(Error::SaleNotFound)
    }
}
