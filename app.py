from flask import Flask, jsonify
from web3 import Web3
from utils.helper_functions import calculate_weekly_apr
from utils.constants import MAINNET_URL, NUMBER_OF_WEEKS_IN_YEAR
app = Flask(__name__)


@app.route("/")
def index():
    web3 = Web3(Web3.HTTPProvider(MAINNET_URL))

    weekly_apr = calculate_weekly_apr(web3)

    yearly_apr = format(weekly_apr * NUMBER_OF_WEEKS_IN_YEAR, '.2f')

    response = jsonify([{'yearly_apr': yearly_apr}])

    return response
