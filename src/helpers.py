"""
Helper functions module for the airdrop simulation system.

This module contains utility functions that support the core simulation logic:

- calculate_buy_sell_probabilities(): Calculates user trading probabilities based on various factors
  including price sensitivity, market sentiment, network effects, and market cycles
- dynamic_vesting(): Handles different vesting mechanisms (linear, dynamic_price, dynamic_activity)
  with proper tracking of vested amounts over time

The functions include robust error handling and validation to ensure simulation stability
and realistic behavior modeling.
"""

import numpy as np
from config import INITIAL_PRICE, SIMULATION_STEPS, INITIAL_TOKENS, MARKET_CYCLES
from typing import Tuple, Dict, Any
from validation import validate_user_params, safe_log, safe_divide, ValidationError

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

    Raises:
        ValidationError: If input parameters are invalid.
    """
    try:
        validate_user_params(user_params)

        if current_price <= 0:
            raise ValidationError("Current price must be positive")
        if initial_price <= 0:
            raise ValidationError("Initial price must be positive")
        if not isinstance(holdings, np.ndarray):
            raise ValidationError("Holdings must be a numpy array")

        airdrop_price = airdrop_strategy.get("airdrop_price", initial_price)

        base_buy_prob = user_params[:, 0]
        base_sell_prob = user_params[:, 1]

        if airdrop_strategy.get("type") == "tiered" and airdrop_strategy.get("criteria") == "holdings":
            base_sell_prob = base_sell_prob * 0.5

        price_sensitivity = user_params[:, 2]
        market_influence = user_params[:, 3]

        price_change_factor = safe_divide(current_price - initial_price, initial_price, 0.0)

        exponent_buy = -(base_buy_prob + price_sensitivity * (initial_price - current_price) + market_influence * market_sentiment - price_change_factor * 0.5)
        exponent_buy = np.clip(exponent_buy, -50, 50)
        buy_prob = 1 / (1 + np.exp(exponent_buy))

        exponent_sell = -(base_sell_prob - price_sensitivity * (current_price - airdrop_price) + market_influence * market_sentiment + price_change_factor * 0.3)
        exponent_sell = np.clip(exponent_sell, -50, 50)
        sell_prob = 1 / (1 + np.exp(exponent_sell))

        # Apply holdings multiplier safely
        holdings_multiplier = 1 + safe_log(holdings + 1, 0.0)
        sell_prob = np.where(holdings > 0, sell_prob * holdings_multiplier, sell_prob)
        sell_prob = np.clip(sell_prob, 0.0, 1.0)

        # Add network effect multiplier safely
        total_holdings = np.sum(holdings)
        network_effect = 1 + 0.2 * safe_log(safe_divide(total_holdings, INITIAL_TOKENS, 1.0), 0.0)
        buy_prob *= network_effect
        sell_prob = safe_divide(sell_prob, network_effect, sell_prob)

        # Add market cycle component
        cycle = np.sin(step * MARKET_CYCLES['frequency']) * MARKET_CYCLES['amplitude']
        buy_prob *= 1 + cycle
        sell_prob *= 1 - cycle

        # Ensure probabilities are in valid range
        buy_prob = np.clip(buy_prob, 0.0, 1.0)
        sell_prob = np.clip(sell_prob, 0.0, 1.0)

        return buy_prob, sell_prob

    except Exception as e:
        raise ValidationError(f"Error in calculate_buy_sell_probabilities: {str(e)}")

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

    # Initialize vested_so_far if not present in strategy
    if 'vested_so_far' not in airdrop_strategy:
        airdrop_strategy['vested_so_far'] = np.zeros_like(holdings)

    vested_so_far = airdrop_strategy['vested_so_far']
    vested_amount = np.zeros_like(holdings)

    if vesting_type == "dynamic_price":
        price_threshold = airdrop_strategy.get("price_threshold", 0.015)
        mask = ((step % max(1, SIMULATION_STEPS // vesting_periods)) == 0) & (current_price > price_threshold)
        vested_amount = np.where(mask, airdrop_per_user / vesting_periods, 0.0)

    elif vesting_type == "dynamic_activity":
        activity_threshold = airdrop_strategy.get("activity_threshold", 50)
        mask = ((step % max(1, SIMULATION_STEPS // vesting_periods)) == 0) & (user_activity >= activity_threshold)
        vested_amount = np.where(
            mask,
            (user_activity / activity_threshold) * (airdrop_per_user / vesting_periods),
            0.0
        )

    elif vesting_type == "linear":
        mask = (step % max(1, SIMULATION_STEPS // vesting_periods)) == 0
        vested_amount = np.where(mask, airdrop_per_user / vesting_periods, 0.0)

    # Apply vesting cap to prevent over-vesting
    remaining_vest = airdrop_per_user - vested_so_far
    actual_vest = np.minimum(vested_amount, remaining_vest)
    actual_vest = np.maximum(actual_vest, 0.0)  # Ensure non-negative

    # Update tracking
    vested_so_far += actual_vest
    airdrop_strategy['vested_so_far'] = vested_so_far

    return holdings + actual_vest