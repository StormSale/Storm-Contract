use soroban_sdk::contracterror;

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
    InsufficientBudget = 10,
}
