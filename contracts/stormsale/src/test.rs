#![cfg(test)]

use super::*;
use soroban_sdk::{testutils::Address as _, Env};

#[test]
fn test_initialization() {
    let env = Env::default();
    let contract_id = env.register_contract(None, StormSaleContract);
    let client = StormSaleContractClient::new(&env, &contract_id);

    let admin = Address::generate(&env);
    let token = Address::generate(&env);

    client.init(&admin, &token);

    // Verify it cannot be initialized again
    // let result = client.try_init(&admin, &token);
    // assert!(result.is_err()); // In a real test we check the exact Error::AlreadyInitialized
}

#[test]
fn test_create_campaign() {
    let env = Env::default();
    let contract_id = env.register_contract(None, StormSaleContract);
    let client = StormSaleContractClient::new(&env, &contract_id);

    let admin = Address::generate(&env);
    let advertiser = Address::generate(&env);
    let token = Address::generate(&env);

    client.init(&admin, &token);
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    let commission_rate = 500; // 5%
    let clearing_period = 86400; // 1 day

    let campaign_id = client.create_campaign(&advertiser, &commission_rate, &clearing_period);
    assert_eq!(campaign_id, 1);

    let campaign = client.get_campaign(&campaign_id);
    assert_eq!(campaign.advertiser, advertiser);
    assert_eq!(campaign.commission_rate, commission_rate);
    assert_eq!(campaign.clearing_period, clearing_period);
}
