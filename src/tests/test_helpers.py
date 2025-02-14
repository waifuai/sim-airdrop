import pytest
import numpy as np
from airdrop.src.helpers import calculate_buy_sell_probabilities, dynamic_vesting
from airdrop.src.config import INITIAL_PRICE

def test_calculate_buy_sell_probabilities():
    num_users = 10
    # Create dummy parameters: all ones for simplicity.
    user_params = np.ones((num_users, 4))
    current_price = INITIAL_PRICE * 1.2
    initial_price = INITIAL_PRICE
    market_sentiment = 0.0
    airdrop_strategy = {"type": "uniform", "airdrop_price": initial_price}
    holdings = np.ones(num_users)
    step = 0

    buy_prob, sell_prob = calculate_buy_sell_probabilities(
        user_params, current_price, initial_price, market_sentiment,
        airdrop_strategy, holdings, step
    )
    # Probabilities must be between 0 and 1.
    assert np.all(buy_prob >= 0.0) and np.all(buy_prob <= 1.0)
    assert np.all(sell_prob >= 0.0) and np.all(sell_prob <= 1.0)

def test_dynamic_vesting_linear():
    num_users = 10
    holdings = np.zeros(num_users)
    airdrop_per_user = np.ones(num_users) * 100
    current_price = INITIAL_PRICE * 1.1
    airdrop_strategy = {"vesting": "linear", "vesting_periods": 2}
    step = 0
    user_activity = np.ones(num_users) * 50

    new_holdings = dynamic_vesting(holdings, airdrop_per_user, current_price, airdrop_strategy, step, user_activity)
    # In linear vesting, if step is at the vesting interval (step 0 qualifies), holdings should increase.
    assert np.all(new_holdings >= holdings)
