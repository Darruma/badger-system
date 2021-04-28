from brownie import *

AddressZero = "0x0000000000000000000000000000000000000000"
MaxUint256 = str(int(2 ** 256 - 1))
EmptyBytes32 = "0x0000000000000000000000000000000000000000000000000000000000000000"

DEFAULT_ADMIN_ROLE = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)

TOKEN_LOCKER_ROLE = web3.keccak(text="TOKEN_LOCKER_ROLE").hex()
ROOT_UPDATER_ROLE = web3.keccak(text="ROOT_UPDATER_ROLE").hex()
GUARDIAN_ROLE = web3.keccak(text="GUARDIAN_ROLE").hex()
APPROVED_STAKER_ROLE = web3.keccak(text="APPROVED_STAKER_ROLE").hex()
PAUSER_ROLE = web3.keccak(text="PAUSER_ROLE").hex()
UNPAUSER_ROLE = web3.keccak(text="UNPAUSER_ROLE").hex()
DISTRIBUTOR_ROLE = web3.keccak(text="DISTRIBUTOR_ROLE").hex()
ROOT_PROPOSER_ROLE = web3.keccak(text="ROOT_PROPOSER_ROLE").hex()
ROOT_VALIDATOR_ROLE = web3.keccak(text="ROOT_VALIDATOR_ROLE").hex()
APPROVED_ACCOUNT_ROLE = web3.keccak(text="APPROVED_ACCOUNT_ROLE").hex()