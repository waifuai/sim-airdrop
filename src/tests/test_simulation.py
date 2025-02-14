import pytest
import numpy as np
from airdrop.src.simulation import simulate_step, run_simulation
from airdrop.src.config import INITIAL_TOKENS, SIMULATION_STEPS, INITIAL_PRICE

def test_simulate_step():
    num_users = 10
    holdings = np.ones(num_users)
    buy_probability = np.ones(num_users) * 0.5
    sell_probability = np.ones(num_users) * 0.5
    total_supply = INITIAL_TOKENS
    price = INITIAL_PRICE
    airdrop_per_user = np.ones(num_users) * 0.1
    step = 0
    user_activity = np.ones(num_users) * 20
    user_params = np.ones((num_users, 4))
    params = {
        "vesting": "none",
        "vesting_periods": 1,
        "price_threshold": 0.015,
        "activity_threshold": 50,
        "initial_price": INITIAL_PRICE,
        "initial_tokens": INITIAL_TOKENS
    }
    
    step_results = simulate_step(
        step, holdings, buy_probability, sell_probability, total_supply, price, airdrop_per_user,
        user_activity, user_params, params
    )
    
    assert step_results["price"] > 0
    # Expect that some tokens are burned so total_supply should be lower.
    assert step_results["total_supply"] < total_supply

def test_run_simulation():
    airdrop_strategy = {"type": "uniform", "percentage": 0.1, "vesting": "none"}
    num_users = 10
    simulation_steps = 100
    initial_tokens = INITIAL_TOKENS
    initial_price = INITIAL_PRICE
    market_sentiment = 0.0
    params = {
        "num_users": num_users,
        "simulation_steps": simulation_steps,
        "initial_tokens": initial_tokens,
        "initial_price": initial_price,
        "market_sentiment": market_sentiment,
        "airdrop_strategy": airdrop_strategy
    }
    
    price_history, final_supply, market_sentiment_history = run_simulation(params)
    # Price history is recorded every 1024 steps (including step 0), so we expect simulation_steps//1024 + 1 entries.
    expected_length = simulation_steps // 1024 + 1
    assert len(price_history) == expected_length
    assert final_supply < initial_tokens
