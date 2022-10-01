from brownie import TestCampaign, accounts
def main():
    account = accounts.load('main')
    TestCampaign.deploy({'from': account}, publish_source=True)