#![cfg(test)]

use super::*;
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test_init_and_role_management() {
    let env = Env::default();
    env.mock_all_auths();

    let contract_id = env.register(StormSaleContract, ());
    let client = StormSaleContractClient::new(&env, &contract_id);

    let admin = Address::generate(&env);
    let token = Address::generate(&env);
    let advertiser = Address::generate(&env);

    // Initialize the contract
    client.init(&admin, &token);

    // Grant Advertiser role
    client.grant_role(&admin, &advertiser, &RoleType::Advertiser);

    // Verify initializing again fails with AlreadyInitialized error
    let res = client.try_init(&admin, &token);
    assert_eq!(res, Err(Ok(Error::AlreadyInitialized)));
}

#[test]
fn test_create_campaign_without_advertiser_role() {
    let env = Env::default();
    env.mock_all_auths();

    let contract_id = env.register(StormSaleContract, ());
    let client = StormSaleContractClient::new(&env, &contract_id);

    let admin = Address::generate(&env);
    let token = Address::generate(&env);
    let non_advertiser = Address::generate(&env);

    client.init(&admin, &token);

    // Attempting to create campaign without Advertiser role should fail
    let res = client.try_create_campaign(&non_advertiser, &1000u32, &604800u32, &100_0000000i128);
    assert_eq!(res, Err(Ok(Error::Unauthorized)));
}
