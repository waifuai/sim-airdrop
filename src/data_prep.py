import numpy as np
from config import USER_ARCHETYPES
from typing import Dict, Any

# --- Data Preparation ---
# --- User Archetypes Data ---
user_archetypes_data = []
for archetype, params in USER_ARCHETYPES.items():
    user_archetypes_data.append([params["base_buy_prob"], params["base_sell_prob"], params["price_sensitivity"], params["market_influence"]])
user_archetypes_array = np.array(user_archetypes_data, dtype=np.float32)

def assign_user_parameters(num_users: int) -> np.ndarray:
    """
    Assigns user parameters based on predefined archetypes.

    Args:
        num_users (int): The number of users to assign parameters to.

    Returns:
        np.ndarray: An array of user parameters.
    """
    archetype_probs = [0.2, 0.4, 0.1, 0.3]
    archetypes = np.random.choice(len(archetype_probs), size=num_users, p=archetype_probs)
    user_params = user_archetypes_array[archetypes]

    noise_scale = 0.1
    noise = np.random.normal(size=user_params.shape, scale=noise_scale)
    user_params = user_params + noise
    user_params = np.clip(user_params, 0.0, 1.0)
    return user_params