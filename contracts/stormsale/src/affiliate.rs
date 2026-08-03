use soroban_sdk::{token, Address, Env};
use crate::storage::{get_token_address, RoleType, Sale, get_campaign, set_campaign, get_sale, set_sale};
use crate::errors::Error;
use crate::admin::check_role;

/// Log a sale (Advertiser or Oracle only)
pub fn log_sale(
    env: Env, 
    advertiser: Address, 
    campaign_id: u32, 
    affiliate: Address, 
    amount: i128
) -> Result<(), Error> {
    advertiser.require_auth();
    check_role(&env, &advertiser, RoleType::Advertiser)?;

    let mut campaign = get_campaign(&env, campaign_id).ok_or(Error::CampaignNotFound)?;

    if campaign.advertiser != advertiser {
        return Err(Error::Unauthorized);
    }

    if amount <= 0 {
        return Err(Error::InvalidAmount);
    }

    // Calculate commission (e.g., 500 = 5%)
    let commission = (amount * (campaign.commission_rate as i128)) / 10000;

    if campaign.budget < commission {
        return Err(Error::InsufficientBudget);
    }

    // Deduct the commission from the campaign's escrow budget
    campaign.budget -= commission;
    set_campaign(&env, campaign_id, &campaign);

    // Record the sale
    let timestamp = env.ledger().timestamp();
    let sale = Sale {
        amount,
        commission,
        timestamp,
        claimed: false,
        approved_by_auditor: false, // Wait for auditor
    };

    set_sale(&env, campaign_id, &affiliate, &sale);

    Ok(())
}

/// Auditor approves a sale
pub fn audit_sale(env: Env, auditor: Address, campaign_id: u32, affiliate: Address) -> Result<(), Error> {
    auditor.require_auth();
    check_role(&env, &auditor, RoleType::Auditor)?;

    let mut sale = get_sale(&env, campaign_id, &affiliate).ok_or(Error::SaleNotFound)?;

    sale.approved_by_auditor = true;
    
    set_sale(&env, campaign_id, &affiliate, &sale);

    Ok(())
}

/// Affiliate claims payout
pub fn claim_payout(env: Env, affiliate: Address, campaign_id: u32) -> Result<(), Error> {
    affiliate.require_auth();
    
    let campaign = get_campaign(&env, campaign_id).ok_or(Error::CampaignNotFound)?;
    let mut sale = get_sale(&env, campaign_id, &affiliate).ok_or(Error::SaleNotFound)?;

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

    let token_addr = get_token_address(&env).ok_or(Error::NotInitialized)?;
    let client = token::Client::new(&env, &token_addr);

    // Mark as claimed
    sale.claimed = true;
    set_sale(&env, campaign_id, &affiliate, &sale);

    // Pay the affiliate from the escrow locked in the contract
    client.transfer(&env.current_contract_address(), &affiliate, &sale.commission);

    Ok(())
}
