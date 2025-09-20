"""
Data preparation module for the airdrop simulation system.

This module handles the preparation and assignment of user parameters based on predefined
user archetypes. It converts archetype definitions into numerical arrays and assigns
users to archetypes according to realistic distribution patterns.

Key functions:
- assign_user_parameters(): Assigns behavioral parameters to users based on archetype distribution
- get_archetype_distribution(): Returns the current user archetype distribution

The module adds realistic noise to user parameters to simulate individual variations
while maintaining the core characteristics of each archetype.
"""

import numpy as np
from config import USER_ARCHETYPES, USER_DISTRIBUTION
from typing import Dict, Any

# --- Data Preparation ---
# --- User Archetypes Data ---
user_archetypes_data = []
archetype_names = []
for archetype_name, params in USER_ARCHETYPES.items():
    user_archetypes_data.append([params["base_buy_prob"], params["base_sell_prob"], params["price_sensitivity"], params["market_influence"]])
    archetype_names.append(archetype_name)

user_archetypes_array = np.array(user_archetypes_data, dtype=np.float32)
user_distribution_probs = [USER_DISTRIBUTION[name] for name in archetype_names]

def assign_user_parameters(num_users: int) -> np.ndarray:
    """
    Assigns user parameters based on predefined archetypes with realistic distribution.

    Args:
        num_users (int): The number of users to assign parameters to.

    Returns:
        np.ndarray: An array of user parameters.
    """
    # Use realistic user distribution instead of uniform
    archetypes = np.random.choice(
        len(user_distribution_probs),
        size=num_users,
        p=user_distribution_probs
    )
    user_params = user_archetypes_array[archetypes]

    # Add realistic noise to simulate individual variations
    noise_scale = 0.08  # Reduced noise for more realistic behavior
    noise = np.random.normal(size=user_params.shape, scale=noise_scale)
    user_params = user_params + noise
    user_params = np.clip(user_params, 0.0, 1.0)

    return user_params

def get_archetype_distribution() -> Dict[str, float]:
    """
    Returns the current user archetype distribution.

    Returns:
        Dict[str, float]: Dictionary mapping archetype names to their distribution percentages.
    """
    return USER_DISTRIBUTION.copy()