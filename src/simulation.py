import numpy as np
from typing import Tuple, Dict, Any

from airdrop.src.config import SIMULATION_STEPS, INITIAL_PRICE, INITIAL_TOKENS
from airdrop.src.helpers import dynamic_vesting, calculate_buy_sell_probabilities

# --- Simulation Step ---
def _calculate_trade_volumes(holdings: np.ndarray, buy_probability: np.ndarray, sell_probability: np.ndarray, price: float, total_supply: float) -> Tuple[np.ndarray, np.ndarray]:
    """Calculates the buy and sell amounts based on probabilities and constraints."""
    buy_decisions = np.random.uniform(size=holdings.shape) < buy_probability
    sell_decisions = np.random.uniform(size=holdings.shape) < sell_probability
    buy_amount = np.minimum(buy_decisions * (price * 50.0), total_supply * 0.005)
    sell_amount = sell_decisions * holdings
    return buy_amount, sell_amount

def _apply_price_impact(demand: float, supply: float, price: float, initial_tokens: float) -> float:
    """Applies price impact based on demand, supply, and liquidity."""
    liquidity_pool = 0.05 * initial_tokens  # Constant product AMM-like
    price_impact = (demand - supply) / liquidity_pool
    new_price = price * np.exp(price_impact * 0.1)  # Exponential curve
    new_price += np.random.normal(0, 0.005 * price)  # Volatility scaling
    return np.maximum(new_price, 0.000001)

def simulate_step(step: int, holdings: np.ndarray, buy_probability: np.ndarray, sell_probability: np.ndarray, total_supply: float, price: float, airdrop_per_user: np.ndarray, user_activity: np.ndarray, user_params: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates a single step of the airdrop process.

    Args:
        step (int): The current simulation step.
        holdings (np.ndarray): An array of user holdings.
        buy_probability (np.ndarray): An array of buy probabilities for each user.
        sell_probability (np.ndarray): An array of sell probabilities for each user.
        total_supply (float): The total supply of the token.
        price (float): The current price of the token.
        airdrop_per_user (np.ndarray): An array of airdrop amounts per user.
        user_activity (np.ndarray): An array of user activity levels.
        user_params (np.ndarray): An array of user parameters.
        params (Dict[str, Any]): Dictionary of simulation parameters.

    Returns:
        Dict[str, Any]: A dictionary containing the new holdings, new price, new total supply, and updated user activity.
    """
    vesting = params.get("vesting", "none")
    vesting_periods = params.get("vesting_periods", 1)
    price_threshold = params.get("price_threshold", 0.015)
    activity_threshold = params.get("activity_threshold", 50)
    initial_price = params.get("initial_price", 0.10)
    initial_tokens = params.get("initial_tokens", 1_000_000_000)

    if vesting != "none":
        holdings = dynamic_vesting(holdings, airdrop_per_user, price, {"vesting": vesting, "vesting_periods": vesting_periods, "price_threshold": price_threshold, "activity_threshold": activity_threshold}, step, user_activity)

    buy_amount, sell_amount = _calculate_trade_volumes(holdings, buy_probability, sell_probability, price, total_supply)

    # Add gas fee impact
    gas_fee = 0.001 * price  # Dynamic gas pricing
    effective_buy_price = price + gas_fee
    effective_sell_price = price - gas_fee

    # Modify demand/supply calculations
    demand = np.sum(buy_amount * effective_buy_price * user_activity)
    supply = np.sum(sell_amount * effective_sell_price * holdings * user_activity)

    new_price = _apply_price_impact(demand, supply, price, initial_tokens)

    new_holdings = holdings + buy_amount - sell_amount

    transaction_volume = np.sum(buy_amount + sell_amount)
    burn_rate = 0.05
    new_total_supply = total_supply - transaction_volume * burn_rate

    # Add activity evolution based on market conditions
    activity_change = np.where(
        price > initial_price,
        np.random.normal(0.5, 0.2, size=user_activity.shape),
        np.random.normal(-0.3, 0.2, size=user_activity.shape)
    )
    user_activity = np.clip(user_activity * (1 + activity_change), 5, 200)

    # Whale Detection System
    whale_threshold = 0.01 * initial_tokens
    whales = holdings > whale_threshold
    if np.any(whales):
        # Apply whale-specific behavior modifiers
        user_params[whales, 1] *= 0.8  # Reduce sell probability
        user_params[whales, 3] *= 1.2  # Increase market influence

    return {
        "holdings": new_holdings,
        "price": new_price,
        "total_supply": new_total_supply,
        "user_activity": user_activity
    }

# --- Main Simulation Loop ---
def run_simulation(params: Dict[str, Any]) -> Tuple[List[float], float, List[float]]:
    """
    Runs the airdrop simulation.

    Args:
        airdrop_strategy (Dict[str, Any]): A dictionary defining the airdrop strategy.

    Returns:
        Tuple[List[float], float, List[float]]: A tuple containing the price history, final total supply, and market sentiment history.
    """
    from airdrop.src.data_prep import assign_user_parameters
    from airdrop.src.data_generation import generate_user_data

    num_users = params.get('num_users', 100)
    simulation_steps = params.get('simulation_steps', 100)
    initial_tokens = params.get('initial_tokens', 1_000_000_000)
    initial_price = params.get('initial_price', 0.10)
    market_sentiment = params.get('market_sentiment', 0.0)
    airdrop_strategy = params.get('airdrop_strategy', {"type": "none", "percentage": 0.1, "vesting": "none"})

    user_params = assign_user_parameters(num_users)
    airdrop_distribution, user_activity = generate_user_data(num_users, airdrop_strategy, user_params)

    holdings = np.copy(airdrop_distribution)
    total_supply = float(initial_tokens)
    price = float(initial_price)

    airdrop_per_user = np.copy(airdrop_distribution)

    price_history: List[float] = []
    market_sentiment_history: List[float] = []
    initial_market_sentiment = float(market_sentiment)

    for step in range(simulation_steps):
        buy_probability, sell_probability = calculate_buy_sell_probabilities(user_params, price, initial_price, initial_market_sentiment, airdrop_strategy, holdings, step)
        step_results = simulate_step(step, holdings, buy_probability, sell_probability, total_supply, price, airdrop_per_user, user_activity, user_params, params)
        holdings = step_results["holdings"]
        price = step_results["price"]
        total_supply = step_results["total_supply"]
        user_activity = step_results["user_activity"]

        if step % 1024 == 0:
            price_history.append(price)
            market_sentiment_history.append(initial_market_sentiment)

        # Add price/supply impact on sentiment
        price_change = (price - initial_price) / initial_price
        supply_change = (total_supply - initial_tokens) / initial_tokens

        sentiment_change = (
            0.4 * price_change +
            0.2 * -supply_change +
            np.random.normal(0, 0.01)
        )
        new_market_sentiment = np.clip(initial_market_sentiment + sentiment_change, -1, 1)

        market_sentiment_change = np.random.normal(scale=0.01)
        new_market_sentiment = initial_market_sentiment + market_sentiment_change
        new_market_sentiment = np.clip(new_market_sentiment, -0.5, 0.5)
        initial_market_sentiment = new_market_sentiment

    return price_history, total_supply, market_sentiment_history