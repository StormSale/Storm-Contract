use crate::errors::Error;
use crate::storage::{DataKey, RoleType};
use soroban_sdk::{Address, Env};

/// Internal function to set a role
pub fn grant_role_internal(env: &Env, target: Address, role: RoleType) {
    env.storage().instance().set(&DataKey::Role(target), &role);
}

/// Internal function to verify a role
pub fn check_role(env: &Env, account: &Address, required_role: RoleType) -> Result<(), Error> {
    let role = env
        .storage()
        .instance()
        .get(&DataKey::Role(account.clone()))
        .unwrap_or(RoleType::Affiliate); // Default if none

    if role != required_role && role != RoleType::Admin {
        return Err(Error::Unauthorized);
    }
    Ok(())
}

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
    grant_role_internal(&env, admin, RoleType::Admin);

    Ok(())
}

pub fn grant_role(env: Env, admin: Address, target: Address, role: RoleType) -> Result<(), Error> {
    admin.require_auth();
    check_role(&env, &admin, RoleType::Admin)?;

    grant_role_internal(&env, target, role);
    Ok(())
}
