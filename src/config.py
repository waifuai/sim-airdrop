import numpy as np
from typing import Dict, Any

# --- Model Parameters ---
INITIAL_TOKENS: int = 1_000_000_000
INITIAL_PRICE: float = 0.10
NUM_USERS: int = 100  # Reduced for CPU
SIMULATION_STEPS: int = 1024 #* 8 * 8 * 64  # Further reduced for CPU
MAX_STRATEGIES: int = 5  # Added parameter to limit strategies

# --- Market Cycles ---
MARKET_CYCLES: Dict[str, Any] = {
    'phase_duration': 256,
    'amplitude': 0.2,
    'frequency': 2*np.pi/SIMULATION_STEPS
}

# --- User Archetypes ---
USER_ARCHETYPES: Dict[str, Dict[str, float]] = {
    "SPECULATOR": {"base_buy_prob": 0.6, "base_sell_prob": 0.9, "price_sensitivity": 0.8, "market_influence": 0.7},
    "HODLER": {"base_buy_prob": 0.2, "base_sell_prob": 0.1, "price_sensitivity": 0.2, "market_influence": 0.3},
    "AIRDROP_HUNTER": {"base_buy_prob": 0.1, "base_sell_prob": 0.95, "price_sensitivity": 0.5, "market_influence": 0.6},
    "ACTIVE_USER": {"base_buy_prob": 0.4, "base_sell_prob": 0.3, "price_sensitivity": 0.4, "market_influence": 0.5},
}