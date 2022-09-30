from brownie import TestCampaign, accounts
def main():
    account = accounts.load('main')
    # TestCampaign.deploy({'from': account}, publish_source=True)
    token = TestCampaign1.at("0xC3BB19A39b6F3d7303f99d36439bfB3545c277A0")
    TestCampaign1.publish_source(token)