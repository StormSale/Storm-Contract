#![no_std]

mod storage_types;
mod test;

use soroban_sdk::{
    contract, contractimpl, contracterror, Address, Env, Vec, token,
};
use storage_types::{DataKey, RoleType, Campaign, Sale};

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum Error {
    AlreadyInitialized = 1,
    NotInitialized = 2,
    Unauthorized = 3,
    InvalidAmount = 4,
    CampaignNotFound = 5,
    SaleNotFound = 6,
    SaleAlreadyClaimed = 7,
    ClearingPeriodNotMet = 8,
    SaleNotAudited = 9,
}

#[contract]
pub struct StormSaleContract;

#[contractimpl]
impl StormSaleContract {
    /// Initialize the contract with an admin and the XLM token address
    pub fn init(env: Env, admin: Address, token: Address) -> Result<(), Error> {
        if env.storage().instance().has(&DataKey::Admin) {
            return Err(Error::AlreadyInitialized);
        }
        
        // The admin authorizes the initialization
        admin.require_auth();

        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::Token, &token);
        env.storage().instance().set(&DataKey::CampaignCount, &0u32);

        // Grant Admin role to the creator
        Self::grant_role_internal(&env, admin, RoleType::Admin);
        
        Ok(())
    }

    /// Grant a role to an address (Admin only)
    pub fn grant_role(env: Env, admin: Address, target: Address, role: RoleType) -> Result<(), Error> {
        admin.require_auth();
        Self::check_role(&env, &admin, RoleType::Admin)?;

        Self::grant_role_internal(&env, target, role);
        Ok(())
    }

    /// Internal function to set a role
    fn grant_role_internal(env: &Env, target: Address, role: RoleType) {
        env.storage().instance().set(&DataKey::Role(target), &role);
    }

    /// Internal function to verify a role
    fn check_role(env: &Env, account: &Address, required_role: RoleType) -> Result<(), Error> {
        let role = env.storage().instance().get(&DataKey::Role(account.clone()))
            .unwrap_or(RoleType::Affiliate); // Default if none
            
        if role != required_role && role != RoleType::Admin {
            return Err(Error::Unauthorized);
        }
        Ok(())
    }

    /// Create a new affiliate campaign (Advertiser only)
    pub fn create_campaign(
        env: Env, 
        advertiser: Address, 
        commission_rate: u32, 
        clearing_period: u32
    ) -> Result<u32, Error> {
        advertiser.require_auth();
        Self::check_role(&env, &advertiser, RoleType::Advertiser)?;

        let mut count: u32 = env.storage().instance().get(&DataKey::CampaignCount).unwrap_or(0);
        count += 1;

        let campaign = Campaign {
            id: count,
            advertiser: advertiser.clone(),
            commission_rate,
            clearing_period,
            active: true,
        };

        env.storage().persistent().set(&DataKey::Campaign(count), &campaign);
        env.storage().instance().set(&DataKey::CampaignCount, &count);

        Ok(count)
    }

    /// Log a sale (Advertiser only). 
    /// Advertiser must transfer `amount` of XLM to the contract.
    pub fn log_sale(
        env: Env, 
        advertiser: Address, 
        campaign_id: u32, 
        affiliate: Address, 
        amount: i128
    ) -> Result<(), Error> {
        advertiser.require_auth();
        Self::check_role(&env, &advertiser, RoleType::Advertiser)?;

        let campaign: Campaign = env.storage().persistent().get(&DataKey::Campaign(campaign_id))
            .ok_or(Error::CampaignNotFound)?;

        if campaign.advertiser != advertiser {
            return Err(Error::Unauthorized);
        }

        if amount <= 0 {
            return Err(Error::InvalidAmount);
        }

        let token_addr: Address = env.storage().instance().get(&DataKey::Token)
            .ok_or(Error::NotInitialized)?;
        
        let client = token::Client::new(&env, &token_addr);

        // Calculate commission
        let commission = (amount * (campaign.commission_rate as i128)) / 10000;

        // Transfer funds from advertiser to the contract
        client.transfer(&advertiser, &env.current_contract_address(), &amount);

        // Record the sale
        let timestamp = env.ledger().timestamp();
        let sale = Sale {
            amount,
            commission,
            timestamp,
            claimed: false,
            approved_by_auditor: false, // Wait for auditor
        };

        env.storage().persistent().set(&DataKey::Sale(campaign_id, affiliate.clone()), &sale);

        Ok(())
    }

    /// Auditor approves a sale
    pub fn audit_sale(env: Env, auditor: Address, campaign_id: u32, affiliate: Address) -> Result<(), Error> {
        auditor.require_auth();
        Self::check_role(&env, &auditor, RoleType::Auditor)?;

        let mut sale: Sale = env.storage().persistent().get(&DataKey::Sale(campaign_id, affiliate.clone()))
            .ok_or(Error::SaleNotFound)?;

        sale.approved_by_auditor = true;
        
        env.storage().persistent().set(&DataKey::Sale(campaign_id, affiliate), &sale);

        Ok(())
    }

    /// Affiliate claims payout
    pub fn claim_payout(env: Env, affiliate: Address, campaign_id: u32) -> Result<(), Error> {
        affiliate.require_auth();
        
        let campaign: Campaign = env.storage().persistent().get(&DataKey::Campaign(campaign_id))
            .ok_or(Error::CampaignNotFound)?;

        let mut sale: Sale = env.storage().persistent().get(&DataKey::Sale(campaign_id, affiliate.clone()))
            .ok_or(Error::SaleNotFound)?;

        if sale.claimed {
            return Err(Error::SaleAlreadyClaimed);
        }

        if !sale.approved_by_auditor {
            return Err(Error::SaleNotAudited);
        }

        let current_time = env.ledger().timestamp();
        if current_time < sale.timestamp + (campaign.clearing_period as u64) {
            return Err(Error::ClearingPeriodNotMet);
        }

        let token_addr: Address = env.storage().instance().get(&DataKey::Token)
            .ok_or(Error::NotInitialized)?;
        
        let client = token::Client::new(&env, &token_addr);

        // Mark as claimed
        sale.claimed = true;
        env.storage().persistent().set(&DataKey::Sale(campaign_id, affiliate.clone()), &sale);

        // Pay the affiliate
        client.transfer(&env.current_contract_address(), &affiliate, &sale.commission);

        // The remaining balance belongs to the advertiser or admin depending on business logic. 
        // For StormSale, we'll return the remainder (amount - commission) to the advertiser.
        let remainder = sale.amount - sale.commission;
        client.transfer(&env.current_contract_address(), &campaign.advertiser, &remainder);

        Ok(())
    }

    /// Get campaign metadata
    pub fn get_campaign(env: Env, campaign_id: u32) -> Result<Campaign, Error> {
        env.storage().persistent().get(&DataKey::Campaign(campaign_id))
            .ok_or(Error::CampaignNotFound)
    }

    /// Get sale metadata
    pub fn get_sale(env: Env, campaign_id: u32, affiliate: Address) -> Result<Sale, Error> {
        env.storage().persistent().get(&DataKey::Sale(campaign_id, affiliate))
            .ok_or(Error::SaleNotFound)
    }
}
