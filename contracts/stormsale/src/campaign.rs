use crate::admin::check_role;
use crate::errors::Error;
use crate::storage::{
    self, get_campaign, get_token_address, set_campaign, AudienceType, Campaign, DataKey, RoleType,
};
use soroban_sdk::{symbol_short, token, Address, Env};

/// Create a new affiliate campaign (Advertiser only, default B2C)
pub fn create_campaign(
    env: Env,
    advertiser: Address,
    commission_rate: u32,
    clearing_period: u32,
    budget: i128,
) -> Result<u32, Error> {
    create_targeted_campaign(
        env,
        advertiser,
        commission_rate,
        clearing_period,
        budget,
        AudienceType::B2C,
    )
}

/// Create a new targeted affiliate campaign (Advertiser only, explicit B2B or B2C)
pub fn create_targeted_campaign(
    env: Env,
    advertiser: Address,
    commission_rate: u32,
    clearing_period: u32,
    budget: i128,
    audience: AudienceType,
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
        audience,
    };

    set_campaign(&env, count, &campaign);
    env.storage()
        .instance()
        .set(&DataKey::CampaignCount, &count);

    let audience_sym = match audience {
        AudienceType::B2C => symbol_short!("b2c"),
        AudienceType::B2B => symbol_short!("b2b"),
    };

    env.events().publish(
        (
            symbol_short!("camp"),
            symbol_short!("created"),
            audience_sym,
        ),
        (count, advertiser, budget),
    );

    Ok(count)
}

/// Authorize or revoke a B2B team operator to log sales on behalf of an advertiser
pub fn set_campaign_operator(
    env: Env,
    advertiser: Address,
    campaign_id: u32,
    operator: Address,
    approved: bool,
) -> Result<(), Error> {
    advertiser.require_auth();

    let campaign = get_campaign(&env, campaign_id).ok_or(Error::CampaignNotFound)?;
    if campaign.advertiser != advertiser {
        return Err(Error::Unauthorized);
    }

    storage::set_campaign_operator(&env, campaign_id, &operator, approved);

    env.events().publish(
        (symbol_short!("operator"), symbol_short!("set")),
        (campaign_id, operator, approved),
    );

    Ok(())
}

/// Allows advertiser to add more budget to an existing campaign
pub fn top_up_budget(
    env: Env,
    advertiser: Address,
    campaign_id: u32,
    amount: i128,
) -> Result<(), Error> {
    advertiser.require_auth();

    let mut campaign = get_campaign(&env, campaign_id).ok_or(Error::CampaignNotFound)?;

    if campaign.advertiser != advertiser {
        return Err(Error::Unauthorized);
    }

    if !campaign.active {
        return Err(Error::CampaignInactive);
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

    env.events().publish(
        (symbol_short!("camp"), symbol_short!("topup")),
        (campaign_id, amount, campaign.budget),
    );

    Ok(())
}

/// Allows advertiser to cancel/close campaign and refund remaining escrow budget
pub fn refund_escrow(env: Env, advertiser: Address, campaign_id: u32) -> Result<i128, Error> {
    advertiser.require_auth();

    let mut campaign = get_campaign(&env, campaign_id).ok_or(Error::CampaignNotFound)?;

    if campaign.advertiser != advertiser {
        return Err(Error::Unauthorized);
    }

    let refundable = campaign.budget;
    if refundable <= 0 {
        return Err(Error::InvalidAmount);
    }

    let token_addr = get_token_address(&env).ok_or(Error::NotInitialized)?;
    let client = token::Client::new(&env, &token_addr);

    campaign.budget = 0;
    campaign.active = false;
    set_campaign(&env, campaign_id, &campaign);

    client.transfer(&env.current_contract_address(), &advertiser, &refundable);

    env.events().publish(
        (symbol_short!("camp"), symbol_short!("refund")),
        (campaign_id, advertiser, refundable),
    );

    Ok(refundable)
}
