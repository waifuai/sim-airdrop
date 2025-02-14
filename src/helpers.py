import numpy as np
from config import INITIAL_PRICE, SIMULATION_STEPS, INITIAL_TOKENS, MARKET_CYCLES
from typing import Tuple, Dict, Any

# --- Helper Functions ---
def calculate_buy_sell_probabilities(user_params: np.ndarray, current_price: float, initial_price: float, market_sentiment: float, airdrop_strategy: Dict[str, Any], holdings: np.ndarray, step: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates the buy and sell probabilities for each user.

    Args:
        user_params (np.ndarray): An array of user parameters.
        current_price (float): The current price of the token.
        initial_price (float): The initial price of the token.
        market_sentiment (float): The current market sentiment.
        airdrop_strategy (Dict[str, Any]): A dictionary defining the airdrop strategy.
        holdings (np.ndarray): An array of user holdings.
        step (int): The current simulation step.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple containing the buy and sell probabilities.
    """
    airdrop_price = airdrop_strategy.get("airdrop_price", initial_price)

    base_buy_prob = user_params[:, 0]
    base_sell_prob = user_params[:, 1]

    if airdrop_strategy["type"] == "tiered" and airdrop_strategy["criteria"] == "holdings":
        base_sell_prob = base_sell_prob * 0.5

    price_sensitivity = user_params[:, 2]
    market_influence = user_params[:, 3]

    price_change_factor = (current_price - initial_price) / initial_price

    exponent_buy = -(base_buy_prob + price_sensitivity * (initial_price - current_price) + market_influence * market_sentiment - price_change_factor * 0.5)
    exponent_buy = np.clip(exponent_buy, -50, 50)
    buy_prob = 1 / (1 + np.exp(exponent_buy))

    exponent_sell = -(base_sell_prob - price_sensitivity * (current_price - airdrop_price) + market_influence * market_sentiment + price_change_factor * 0.3)
    exponent_sell = np.clip(exponent_sell, -50, 50)
    sell_prob = 1 / (1 + np.exp(exponent_sell))

    sell_prob = np.where(holdings > 0, sell_prob * (1 + np.log(holdings + 1)), sell_prob)

    # Add network effect multiplier
    network_effect = 1 + 0.2 * np.log1p(np.sum(holdings) / INITIAL_TOKENS)
    buy_prob *= network_effect
    sell_prob /= network_effect

    # Add market cycle component
    cycle = np.sin(step * MARKET_CYCLES['frequency']) * MARKET_CYCLES['amplitude']
    buy_prob *= 1 + cycle
    sell_prob *= 1 - cycle


    return buy_prob, sell_prob

def dynamic_vesting(holdings: np.ndarray, airdrop_per_user: np.ndarray, current_price: float, airdrop_strategy: Dict[str, Any], step: int, user_activity: np.ndarray) -> np.ndarray:
    """
    Applies dynamic vesting to user holdings.

    Args:
        holdings (np.ndarray): An array of user holdings.
        airdrop_per_user (np.ndarray): An array of airdrop amounts per user.
        current_price (float): The current price of the token.
        airdrop_strategy (Dict[str, Any]): A dictionary defining the airdrop strategy.
        step (int): The current simulation step.
        user_activity (np.ndarray): An array of user activity levels.

    Returns:
        np.ndarray: An array of updated user holdings.
    """
    vesting_type = airdrop_strategy["vesting"]
    vesting_periods = airdrop_strategy.get("vesting_periods", 1)

    dynamic_price_mask = vesting_type == "dynamic_price"
    dynamic_activity_mask = vesting_type == "dynamic_activity"
    linear_vesting_mask = vesting_type == "linear"

    vested_amount = np.zeros_like(holdings)
    vested_so_far_global = dynamic_vesting.vested_so_far if hasattr(dynamic_vesting, 'vested_so_far') else np.zeros_like(holdings)
    vested_so_far = airdrop_strategy.get('vested_so_far', vested_so_far_global)


    if dynamic_price_mask:
        price_threshold = airdrop_strategy["price_threshold"]
        mask = ((step % (SIMULATION_STEPS // vesting_periods)) == 0) & (current_price > price_threshold)
        vested_amount = np.where(mask, airdrop_per_user / vesting_periods, 0.0)

    elif dynamic_activity_mask:
        activity_threshold = airdrop_strategy["activity_threshold"]
        mask = ((step % (SIMULATION_STEPS // vesting_periods)) == 0) & (user_activity >= activity_threshold)
        vested_amount = np.where(
            mask,
            (user_activity / activity_threshold) * (airdrop_per_user / vesting_periods),
            0.0
        )

    elif linear_vesting_mask:
         mask = (step % (SIMULATION_STEPS // vesting_periods)) == 0
         vested_amount = np.where(mask, airdrop_per_user / vesting_periods, 0.0)

    # Apply vesting cap
    remaining_vest = airdrop_per_user - vested_so_far
    actual_vest = np.minimum(vested_amount, remaining_vest)

    vested_so_far += actual_vest
    dynamic_vesting.vested_so_far = vested_so_far

    airdrop_strategy['vested_so_far'] = vested_so_far
    return holdings + actual_vest