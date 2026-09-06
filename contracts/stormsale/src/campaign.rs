use crate::admin::check_role;
use crate::errors::Error;
use crate::storage::{get_token_address, set_campaign, Campaign, DataKey, RoleType};
use soroban_sdk::{token, Address, Env};

/// Create a new affiliate campaign (Advertiser only)
pub fn create_campaign(
    env: Env,
    advertiser: Address,
    commission_rate: u32,
    clearing_period: u32,
    budget: i128,
) -> Result<u32, Error> {
    advertiser.require_auth();
    check_role(&env, &advertiser, RoleType::Advertiser)?;

    if budget <= 0 {
        return Err(Error::InvalidAmount);
    }

    let token_addr = get_token_address(&env).ok_or(Error::NotInitialized)?;
    let client = token::Client::new(&env, &token_addr);

    // Transfer the budget from the advertiser to the smart contract escrow
    client.transfer(&advertiser, &env.current_contract_address(), &budget);

    let mut count: u32 = env
        .storage()
        .instance()
        .get(&DataKey::CampaignCount)
        .unwrap_or(0);
    count += 1;

    let campaign = Campaign {
        id: count,
        advertiser: advertiser.clone(),
        commission_rate,
        clearing_period,
        budget,
        active: true,
    };

    set_campaign(&env, count, &campaign);
    env.storage()
        .instance()
        .set(&DataKey::CampaignCount, &count);

    Ok(count)
}

/// Allows advertiser to add more budget to an existing campaign
pub fn top_up_budget(
    env: Env,
    advertiser: Address,
    campaign_id: u32,
    amount: i128,
) -> Result<(), Error> {
    advertiser.require_auth();

    let mut campaign: Campaign = env
        .storage()
        .persistent()
        .get(&DataKey::Campaign(campaign_id))
        .ok_or(Error::CampaignNotFound)?;

    if campaign.advertiser != advertiser {
        return Err(Error::Unauthorized);
    }

    if amount <= 0 {
        return Err(Error::InvalidAmount);
    }

    let token_addr = get_token_address(&env).ok_or(Error::NotInitialized)?;
    let client = token::Client::new(&env, &token_addr);

    // Transfer additional budget from the advertiser to the smart contract escrow
    client.transfer(&advertiser, &env.current_contract_address(), &amount);

    campaign.budget += amount;
    set_campaign(&env, campaign_id, &campaign);

    Ok(())
}
