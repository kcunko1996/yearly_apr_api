import json
import urllib.request
import urllib.error
from utils.constants import SECONDS_IN_WEEK, WETH_PRICE_URL, WRAPPED_NEAR_PRICE_URL, BOREALIS_PRICE_URL
from utils.contrat_addresses import AURORA_ADRESS, BRL_CHEF_ADDR, NEAR_ADRESS, WETH_ADRESS
from utils.contracts_abi import UNI_ABI, CHEF_ABI


def open_url(request):
    try:
        return urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        return e


def calculate_weekly_apr(web3):
    chefContarct = web3.eth.contract(
        address=BRL_CHEF_ADDR, abi=json.loads(CHEF_ABI))

    contractAuroraPool = web3.eth.contract(
        address=AURORA_ADRESS, abi=json.loads(UNI_ABI))

    contractNear = web3.eth.contract(
        address=NEAR_ADRESS, abi=json.loads(UNI_ABI))

    contractWeth = web3.eth.contract(
        address=WETH_ADRESS, abi=json.loads(UNI_ABI))

    latestBlock = web3.eth.get_block('latest').number

    multiplier = chefContarct.functions.getMultiplier(
        latestBlock, latestBlock+1).call()

    rewardsTokenPerWeek = chefContarct.functions.BRLPerBlock().call() / 1e18 * \
        multiplier * SECONDS_IN_WEEK / 1.1

    wethPriceResponse = open_url(WETH_PRICE_URL)

    wrappedNearPriceResponse = open_url(WRAPPED_NEAR_PRICE_URL)

    borealisPriceResponse = open_url(BOREALIS_PRICE_URL)

    wethPrice = json.load(wethPriceResponse)['weth']['usd']

    borealisPrice = json.load(borealisPriceResponse)['borealis']['usd']

    wrappedNearPrice = json.load(wrappedNearPriceResponse)[
        'wrapped-near']['usd']

    totalAllocPoints = chefContarct.functions.totalAllocPoint().call()

    decimalsAuroraPool = contractAuroraPool.functions.decimals().call()

    decimalsNear = contractNear.functions.decimals().call()

    decimalsWeth = contractWeth.functions.decimals().call()

    reserves = contractAuroraPool.functions.getReserves().call()

    totalSupply = contractAuroraPool.functions.totalSupply().call() / \
        10 ** decimalsAuroraPool

    allocPoints = chefContarct.functions.poolInfo(1).call()[1]

    poolRewardsPerWeek = allocPoints / totalAllocPoints * rewardsTokenPerWeek

    staked = contractAuroraPool.functions.balanceOf(
        BRL_CHEF_ADDR).call() / 10 ** decimalsAuroraPool

    reserve0 = reserves[0] / 10 ** decimalsNear

    reserve1 = reserves[1] / 10 ** decimalsWeth

    tvl = reserve0 * wrappedNearPrice + reserve1 * wethPrice

    price = tvl / totalSupply

    stalked_tvl = price * staked

    usdPerWeek = poolRewardsPerWeek * borealisPrice

    weekly_apr = (usdPerWeek /
                  stalked_tvl * 100)

    return weekly_apr
