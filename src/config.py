"""
Configuration file for the airdrop simulation system.

This module contains all the configurable parameters and constants used throughout the simulation,
including model parameters, market parameters, user archetypes with their behavioral characteristics,
network effects parameters, and logging configuration.

The configuration is organized into sections:
- Model Parameters: Basic simulation settings like token count, price, user count
- Market Parameters: Market dynamics including liquidity, gas fees, burn rates
- Market Cycles: Parameters defining market phase durations and volatility
- User Archetypes: Different user types with their trading probabilities and behaviors
- User Distribution: How users are distributed across different archetypes
- Network Effects: Parameters affecting user behavior based on network size
- Vesting Parameters: Configuration for token vesting mechanisms
- Logging Configuration: Settings for logging output and formatting
"""

import numpy as np
from typing import Dict, Any

# --- Model Parameters ---
INITIAL_TOKENS: int = 1_000_000_000
INITIAL_PRICE: float = 0.10
NUM_USERS: int = 500  # Increased for more realistic simulation
SIMULATION_STEPS: int = 1024  # One market cycle
MAX_STRATEGIES: int = 10  # Increased for better strategy comparison

# --- Market Parameters ---
MARKET_MAKER_LIQUIDITY: float = 0.05  # Percentage of total supply as liquidity
GAS_PRICE_IMPACT: float = 0.001  # Gas fee as percentage of price
BURN_RATE: float = 0.05  # Percentage of transaction volume burned
WHALE_THRESHOLD: float = 0.01  # Percentage of total supply for whale detection

# --- Market Cycles ---
MARKET_CYCLES: Dict[str, Any] = {
    'phase_duration': 256,  # Steps per market phase
    'amplitude': 0.15,      # Reduced for more realistic volatility
    'frequency': 2*np.pi/SIMULATION_STEPS
}

# --- User Archetypes ---
USER_ARCHETYPES: Dict[str, Dict[str, float]] = {
    "SPECULATOR": {
        "base_buy_prob": 0.65,
        "base_sell_prob": 0.85,
        "price_sensitivity": 0.9,
        "market_influence": 0.8,
        "description": "High frequency traders"
    },
    "HODLER": {
        "base_buy_prob": 0.25,
        "base_sell_prob": 0.05,
        "price_sensitivity": 0.1,
        "market_influence": 0.2,
        "description": "Long-term holders"
    },
    "AIRDROP_HUNTER": {
        "base_buy_prob": 0.15,
        "base_sell_prob": 0.95,
        "price_sensitivity": 0.7,
        "market_influence": 0.9,
        "description": "Quick profit seekers"
    },
    "ACTIVE_USER": {
        "base_buy_prob": 0.45,
        "base_sell_prob": 0.25,
        "price_sensitivity": 0.4,
        "market_influence": 0.4,
        "description": "Balanced active users"
    },
    "INVESTOR": {
        "base_buy_prob": 0.35,
        "base_sell_prob": 0.15,
        "price_sensitivity": 0.3,
        "market_influence": 0.3,
        "description": "Value investors"
    }
}

# --- User Distribution ---
USER_DISTRIBUTION: Dict[str, float] = {
    "SPECULATOR": 0.15,
    "HODLER": 0.40,
    "AIRDROP_HUNTER": 0.10,
    "ACTIVE_USER": 0.25,
    "INVESTOR": 0.10
}

# --- Network Effects ---
NETWORK_EFFECT_MULTIPLIER: float = 0.2
MIN_NETWORK_SIZE: int = 100
MAX_NETWORK_SIZE: int = 10000

# --- Vesting Parameters ---
DEFAULT_VESTING_PERIODS: int = 12
PRICE_THRESHOLD_RANGE: tuple = (0.01, 0.20)  # Min and max price thresholds
ACTIVITY_THRESHOLD_RANGE: tuple = (10, 100)  # Min and max activity thresholds

# --- Logging Configuration ---
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'