import pytest
import numpy as np
from airdrop.src.config import INITIAL_TOKENS
from airdrop.src.data_generation import generate_user_data

def test_generate_user_data_uniform():
    num_users = 100
    airdrop_strategy = {"type": "uniform", "percentage": 0.1}
    # Dummy user parameters (shape: num_users x 4)
    user_params = np.ones((num_users, 4))
    distribution, activity = generate_user_data(num_users, airdrop_strategy, user_params)
    
    assert distribution.shape[0] == num_users
    assert activity.shape[0] == num_users
    # For a uniform strategy, all users are eligible so distribution > 0
    assert np.allclose(np.sum(distribution), INITIAL_TOKENS * 0.1)

def test_generate_user_data_none():
    num_users = 50
    airdrop_strategy = {"type": "none", "percentage": 0.1}
    user_params = np.ones((num_users, 4))
    distribution, activity = generate_user_data(num_users, airdrop_strategy, user_params)
    
    # When type is "none", no one should get tokens
    assert np.allclose(distribution, 0.0)
