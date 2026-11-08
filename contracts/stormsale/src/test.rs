#![cfg(test)]
#![allow(clippy::inconsistent_digit_grouping)]

use super::*;
use soroban_sdk::{
    testutils::{Address as _, Ledger},
    token, Address, Env,
};

fn setup_test_env<'a>() -> (
    Env,
    StormSaleContractClient<'a>,
    Address, // admin
    Address, // token_admin
    Address, // token_address
    token::Client<'a>,
    token::StellarAssetClient<'a>,
) {
    let env = Env::default();
    env.mock_all_auths();

    let contract_id = env.register(StormSaleContract, ());
    let client = StormSaleContractClient::new(&env, &contract_id);

    let admin = Address::generate(&env);
    let token_admin = Address::generate(&env);
    let token_contract = env.register_stellar_asset_contract_v2(token_admin.clone());
    let token_address = token_contract.address();

    let token_client = token::Client::new(&env, &token_address);
    let token_asset_client = token::StellarAssetClient::new(&env, &token_address);

    (
        env,
        client,
        admin,
        token_admin,
        token_address,
        token_client,
        token_asset_client,
    )
}

#[test]
fn test_init_and_role_management() {
    let (env, client, admin, _t_admin, token_address, _tc, _tac) = setup_test_env();

    let advertiser = Address::generate(&env);
    let auditor = Address::generate(&env);

    // Initialize the contract
    client.init(&admin, &token_address);

    // Grant roles
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);
    client.grant_role(&admin, &auditor, &RoleType::Auditor);

    // Verify initializing again fails with AlreadyInitialized error
    let res = client.try_init(&admin, &token_address);
    assert_eq!(res, Err(Ok(Error::AlreadyInitialized)));
}

#[test]
fn test_create_campaign_without_advertiser_role() {
    let (env, client, admin, _t_admin, token_address, _tc, _tac) = setup_test_env();
    let non_advertiser = Address::generate(&env);

    client.init(&admin, &token_address);

    // Attempting to create campaign without Advertiser role should fail
    let res = client.try_create_campaign(&non_advertiser, &1000u32, &604800u32, &100_0000000i128);
    assert_eq!(res, Err(Ok(Error::Unauthorized)));
}

#[test]
fn test_create_campaign_and_escrow_deposit() {
    let (env, client, admin, _t_admin, token_address, token_client, token_asset_client) =
        setup_test_env();

    client.init(&admin, &token_address);

    let advertiser = Address::generate(&env);
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    let budget = 5_000_0000000i128; // 5,000 XLM in stroops
    token_asset_client.mint(&advertiser, &10_000_0000000i128);

    let campaign_id = client.create_campaign(
        &advertiser,
        &1000u32,   // 10% commission rate (1000 bps)
        &604800u32, // 7 days clearing period
        &budget,
    );

    assert_eq!(campaign_id, 1);
    assert_eq!(token_client.balance(&advertiser), 5_000_0000000i128);
    assert_eq!(token_client.balance(&client.address), 5_000_0000000i128);

    let campaign = client.get_campaign(&campaign_id);
    assert_eq!(campaign.id, 1);
    assert_eq!(campaign.advertiser, advertiser);
    assert_eq!(campaign.commission_rate, 1000);
    assert_eq!(campaign.clearing_period, 604800);
    assert_eq!(campaign.budget, budget);
    assert!(campaign.active);
}

#[test]
fn test_top_up_budget() {
    let (env, client, admin, _t_admin, token_address, token_client, token_asset_client) =
        setup_test_env();

    client.init(&admin, &token_address);

    let advertiser = Address::generate(&env);
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    token_asset_client.mint(&advertiser, &10_000_0000000i128);

    let campaign_id = client.create_campaign(&advertiser, &1000u32, &604800u32, &5_000_0000000i128);

    // Top up with 2,000 XLM
    client.top_up_budget(&advertiser, &campaign_id, &2_000_0000000i128);

    assert_eq!(token_client.balance(&advertiser), 3_000_0000000i128);
    assert_eq!(token_client.balance(&client.address), 7_000_0000000i128);

    let campaign = client.get_campaign(&campaign_id);
    assert_eq!(campaign.budget, 7_000_0000000i128);

    // Unauthorized top-up rejection
    let stranger = Address::generate(&env);
    let res = client.try_top_up_budget(&stranger, &campaign_id, &1_000_0000000i128);
    assert_eq!(res, Err(Ok(Error::Unauthorized)));
}

#[test]
fn test_log_sale_and_budget_deduction() {
    let (env, client, admin, _t_admin, token_address, _token_client, token_asset_client) =
        setup_test_env();

    client.init(&admin, &token_address);

    let advertiser = Address::generate(&env);
    let affiliate = Address::generate(&env);
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    token_asset_client.mint(&advertiser, &5_000_0000000i128);
    let campaign_id = client.create_campaign(
        &advertiser,
        &1000u32, // 10%
        &604800u32,
        &5_000_0000000i128,
    );

    // Sale of 1,000 XLM -> 10% commission = 100 XLM (100_0000000 stroops)
    let sale_amount = 1_000_0000000i128;
    client.log_sale(&advertiser, &campaign_id, &affiliate, &sale_amount);

    let campaign = client.get_campaign(&campaign_id);
    assert_eq!(campaign.budget, 4_900_0000000i128); // 5000 - 100

    let sale = client.get_sale(&campaign_id, &affiliate);
    assert_eq!(sale.amount, sale_amount);
    assert_eq!(sale.commission, 100_0000000i128);
    assert!(!sale.claimed);
    assert!(!sale.approved_by_auditor);
}

#[test]
fn test_log_sale_insufficient_budget() {
    let (env, client, admin, _t_admin, token_address, _tc, token_asset_client) = setup_test_env();

    client.init(&admin, &token_address);

    let advertiser = Address::generate(&env);
    let affiliate = Address::generate(&env);
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    token_asset_client.mint(&advertiser, &100_0000000i128);
    let campaign_id = client.create_campaign(
        &advertiser,
        &1000u32, // 10%
        &604800u32,
        &100_0000000i128, // Only 100 XLM budget
    );

    // Sale of 2,000 XLM -> 10% = 200 XLM commission > 100 XLM budget
    let res = client.try_log_sale(&advertiser, &campaign_id, &affiliate, &2_000_0000000i128);
    assert_eq!(res, Err(Ok(Error::InsufficientBudget)));
}

#[test]
fn test_full_audit_and_claim_payout_flow() {
    let (env, client, admin, _t_admin, token_address, token_client, token_asset_client) =
        setup_test_env();

    client.init(&admin, &token_address);

    let advertiser = Address::generate(&env);
    let affiliate = Address::generate(&env);
    let auditor = Address::generate(&env);

    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);
    client.grant_role(&admin, &auditor, &RoleType::Auditor);

    token_asset_client.mint(&advertiser, &1_000_0000000i128);
    let clearing_period = 3600u32; // 1 hour
    let campaign_id = client.create_campaign(
        &advertiser,
        &500u32, // 5%
        &clearing_period,
        &1_000_0000000i128,
    );

    // Log sale: 1,000 XLM -> 5% commission = 50 XLM (50_0000000 stroops)
    client.log_sale(&advertiser, &campaign_id, &affiliate, &1_000_0000000i128);

    // 1. Attempt claim without auditor approval -> SaleNotAudited
    let fail_audit = client.try_claim_payout(&affiliate, &campaign_id);
    assert_eq!(fail_audit, Err(Ok(Error::SaleNotAudited)));

    // 2. Auditor approves sale
    client.audit_sale(&auditor, &campaign_id, &affiliate);
    let audited_sale = client.get_sale(&campaign_id, &affiliate);
    assert!(audited_sale.approved_by_auditor);

    // 3. Attempt claim before clearing period -> ClearingPeriodNotMet
    let fail_clearing = client.try_claim_payout(&affiliate, &campaign_id);
    assert_eq!(fail_clearing, Err(Ok(Error::ClearingPeriodNotMet)));

    // 4. Advance ledger timestamp past clearing period
    env.ledger().with_mut(|li| {
        li.timestamp += clearing_period as u64 + 10;
    });

    // 5. Successful claim
    client.claim_payout(&affiliate, &campaign_id);

    assert_eq!(token_client.balance(&affiliate), 50_0000000i128);
    let claimed_sale = client.get_sale(&campaign_id, &affiliate);
    assert!(claimed_sale.claimed);

    // 6. Double claim rejected -> SaleAlreadyClaimed
    let fail_double = client.try_claim_payout(&affiliate, &campaign_id);
    assert_eq!(fail_double, Err(Ok(Error::SaleAlreadyClaimed)));
}

#[test]
fn test_refund_escrow_flow() {
    let (env, client, admin, _t_admin, token_address, token_client, token_asset_client) =
        setup_test_env();

    client.init(&admin, &token_address);

    let advertiser = Address::generate(&env);
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    let initial_budget = 5_000_0000000i128;
    token_asset_client.mint(&advertiser, &initial_budget);

    let campaign_id = client.create_campaign(&advertiser, &1000u32, &604800u32, &initial_budget);

    assert_eq!(token_client.balance(&advertiser), 0);

    // Stranger cannot refund
    let stranger = Address::generate(&env);
    let fail_stranger = client.try_refund_escrow(&stranger, &campaign_id);
    assert_eq!(fail_stranger, Err(Ok(Error::Unauthorized)));

    // Advertiser refunds escrow
    let refunded = client.refund_escrow(&advertiser, &campaign_id);
    assert_eq!(refunded, initial_budget);

    assert_eq!(token_client.balance(&advertiser), initial_budget);
    assert_eq!(token_client.balance(&client.address), 0);

    let campaign = client.get_campaign(&campaign_id);
    assert_eq!(campaign.budget, 0);
    assert!(!campaign.active);

    // Once inactive, cannot top up or log sales
    let affiliate = Address::generate(&env);
    let fail_sale = client.try_log_sale(&advertiser, &campaign_id, &affiliate, &1_000_0000000i128);
    assert_eq!(fail_sale, Err(Ok(Error::CampaignInactive)));

    let fail_topup = client.try_top_up_budget(&advertiser, &campaign_id, &1_000_0000000i128);
    assert_eq!(fail_topup, Err(Ok(Error::CampaignInactive)));
}
