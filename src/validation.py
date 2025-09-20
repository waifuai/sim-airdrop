"""
Validation module for airdrop simulation parameters.
"""
from typing import Dict, Any, List
import numpy as np


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_airdrop_strategy(strategy: Dict[str, Any]) -> None:
    """
    Validates an airdrop strategy configuration.

    Args:
        strategy (Dict[str, Any]): The airdrop strategy to validate.

    Raises:
        ValidationError: If the strategy is invalid.
    """
    required_fields = ['type', 'percentage', 'vesting']
    for field in required_fields:
        if field not in strategy:
            raise ValidationError(f"Missing required field: {field}")

    # Validate strategy type
    valid_types = ['none', 'uniform', 'tiered', 'lottery', 'basic']
    if strategy['type'] not in valid_types:
        raise ValidationError(f"Invalid strategy type: {strategy['type']}. Must be one of {valid_types}")

    # Validate percentage
    if not (0 <= strategy['percentage'] <= 1):
        raise ValidationError(f"Percentage must be between 0 and 1, got {strategy['percentage']}")

    # Validate vesting type
    valid_vesting_types = ['none', 'linear', 'dynamic_price', 'dynamic_activity']
    if strategy['vesting'] not in valid_vesting_types:
        raise ValidationError(f"Invalid vesting type: {strategy['vesting']}. Must be one of {valid_vesting_types}")

    # Type-specific validation
    if strategy['type'] == 'lottery':
        if 'winners_fraction' not in strategy or not (0 < strategy['winners_fraction'] <= 1):
            raise ValidationError("Lottery strategy must have 'winners_fraction' between 0 and 1")

    if strategy['type'] == 'tiered':
        if 'criteria' not in strategy or strategy['criteria'] not in ['holdings', 'activity']:
            raise ValidationError("Tiered strategy must have valid 'criteria' (holdings or activity)")
        if 'thresholds' not in strategy or 'weights' not in strategy:
            raise ValidationError("Tiered strategy must have 'thresholds' and 'weights'")

        thresholds = np.array(strategy['thresholds'])
        weights = np.array(strategy['weights'])
        if len(thresholds) != len(weights):
            raise ValidationError("Thresholds and weights must have the same length")
        if not np.all(weights >= 0):
            raise ValidationError("All weights must be non-negative")

    # Vesting-specific validation
    if strategy['vesting'] != 'none':
        if 'vesting_periods' not in strategy or strategy['vesting_periods'] < 1:
            raise ValidationError("Vesting must have 'vesting_periods' >= 1")

    if strategy['vesting'] == 'dynamic_price':
        if 'price_threshold' not in strategy or strategy['price_threshold'] <= 0:
            raise ValidationError("Dynamic price vesting must have 'price_threshold' > 0")

    if strategy['vesting'] == 'dynamic_activity':
        if 'activity_threshold' not in strategy or strategy['activity_threshold'] <= 0:
            raise ValidationError("Dynamic activity vesting must have 'activity_threshold' > 0")


def validate_simulation_params(params: Dict[str, Any]) -> None:
    """
    Validates simulation parameters.

    Args:
        params (Dict[str, Any]): The simulation parameters to validate.

    Raises:
        ValidationError: If the parameters are invalid.
    """
    required_fields = ['num_users', 'simulation_steps', 'initial_tokens', 'initial_price']
    for field in required_fields:
        if field not in params:
            raise ValidationError(f"Missing required parameter: {field}")

    if params['num_users'] < 1:
        raise ValidationError("Number of users must be at least 1")

    if params['simulation_steps'] < 1:
        raise ValidationError("Simulation steps must be at least 1")

    if params['initial_tokens'] <= 0:
        raise ValidationError("Initial tokens must be positive")

    if params['initial_price'] <= 0:
        raise ValidationError("Initial price must be positive")

    if 'airdrop_strategy' in params:
        validate_airdrop_strategy(params['airdrop_strategy'])


def validate_user_params(user_params: np.ndarray) -> None:
    """
    Validates user parameters array.

    Args:
        user_params (np.ndarray): The user parameters array to validate.

    Raises:
        ValidationError: If the user parameters are invalid.
    """
    if not isinstance(user_params, np.ndarray):
        raise ValidationError("User parameters must be a numpy array")

    if user_params.ndim != 2:
        raise ValidationError("User parameters must be a 2D array")

    if user_params.shape[1] != 4:
        raise ValidationError("User parameters must have 4 columns (base_buy_prob, base_sell_prob, price_sensitivity, market_influence)")

    if np.any(user_params < 0) or np.any(user_params > 1):
        raise ValidationError("All user parameters must be between 0 and 1")


def safe_divide(numerator: np.ndarray, denominator: np.ndarray, default: float = 0.0) -> np.ndarray:
    """
    Safely divides two arrays, handling division by zero.

    Args:
        numerator (np.ndarray): The numerator array.
        denominator (np.ndarray): The denominator array.
        default (float): Default value for division by zero.

    Returns:
        np.ndarray: The result of the division.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.divide(numerator, denominator, out=np.full_like(numerator, default), where=(denominator != 0))
        result = np.nan_to_num(result, nan=default, posinf=default, neginf=default)
    return result


def safe_log(array: np.ndarray, default: float = 0.0) -> np.ndarray:
    """
    Safely computes logarithm, handling non-positive values.

    Args:
        array (np.ndarray): The input array.
        default (float): Default value for non-positive inputs.

    Returns:
        np.ndarray: The logarithm of the array.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.log(np.where(array > 0, array, np.inf))
        result = np.nan_to_num(result, nan=default, posinf=default, neginf=default)
    return result