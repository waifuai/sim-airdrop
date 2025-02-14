import itertools
import random
from typing import Dict, Any, List

# --- Airdrop Strategies Parameter Grid ---
AIRDROP_PARAMETER_GRID: Dict[str, Any] = {
    "type": ["lottery", "basic", "tiered"],
    "percentage": [0.05, 0.1],
    "vesting": ["dynamic_activity", "dynamic_price", "linear", "none"],
    "vesting_periods": [1, 3, 6, 12, 24],
    "criteria": ["holdings", "activity", "none"],
    "thresholds": {
        "holdings": [[0.01, 0.1, 0.5, 1.0], [0.05, 0.2, 0.6, 1.2], [0.1, 0.3, 0.7, 1.5]],
        "activity": [[10, 30, 50, 100], [20, 40, 70, 120], [30, 60, 90, 150]]
    },
    "weights": [[0.1, 0.2, 0.3, 0.4], [0.2, 0.3, 0.3, 0.2], [0.4, 0.3, 0.2, 0.1]],
    "winners_fraction": [0.01, 0.02, 0.05, 0.1],
    "price_threshold": [0.015, 0.02, 0.025, 0.03],
    "activity_threshold": [30, 50, 70, 90]
}

# --- Function to Generate Airdrop Strategies ---
def generate_airdrop_strategies(param_grid: Dict[str, Any], max_strategies: int) -> List[Dict[str, Any]]:
    """
    Generates a list of airdrop strategies based on the given parameter grid.

    Args:
        param_grid (Dict[str, Any]): A dictionary defining the parameter grid for the airdrop strategies.
        max_strategies (int): The maximum number of strategies to generate.

    Returns:
        List[Dict[str, Any]]: A list of airdrop strategies.
    """
    keys = list(param_grid.keys())
    strategies = []

    tiered_combinations = []
    non_tiered_keys = [k for k in keys if k not in ("thresholds", "weights")]

    if "type" in param_grid and "tiered" in param_grid["type"]:
        tiered_indices = [i for i, val in enumerate(param_grid["type"]) if val == "tiered"]

        for type_index in tiered_indices:
            temp_grid = {k: param_grid[k] for k in non_tiered_keys}
            temp_grid["type"] = ["tiered"]
            temp_grid["criteria"] = [c for c in param_grid["criteria"] if c != "none"]

            for combo in itertools.product(*[temp_grid[k] for k in temp_grid]):
                strategy = dict(zip(temp_grid.keys(), combo))
                criteria_value = strategy["criteria"]
                threshold_options = param_grid["thresholds"][criteria_value]
                weight_options = param_grid["weights"]

                for threshold, weight in itertools.product(threshold_options, weight_options):
                    new_strategy = strategy.copy()
                    new_strategy["thresholds"] = threshold
                    new_strategy["weights"] = weight
                    new_strategy["criteria"] = criteria_value
                    tiered_combinations.append(new_strategy)

    other_combinations = []
    non_tiered_keys = [k for k in keys if k not in ("thresholds", "weights")]
    temp_grid = {k: param_grid[k] for k in non_tiered_keys}

    for combo in itertools.product(*[temp_grid[k] for k in non_tiered_keys]):
        strategy = dict(zip(non_tiered_keys, combo))
        if strategy["type"] != "tiered":
            strategy.pop("criteria", None)
            other_combinations.append(strategy)

    all_combinations = tiered_combinations + other_combinations
    random.shuffle(all_combinations)

    for strategy in all_combinations:
        if len(strategies) >= max_strategies:
            break

        # Validate parameter combinations
        if strategy['type'] == 'lottery' and 'winners_fraction' not in strategy:
            continue
        if strategy['vesting'] == 'dynamic_price' and 'price_threshold' not in strategy:
            continue
        if strategy['vesting'] == 'dynamic_activity' and 'activity_threshold' not in strategy:
            continue
        if strategy['vesting'] != 'none' and 'vesting_periods' not in strategy:
            continue


        strategies.append(strategy)

    for i, strategy in enumerate(strategies):
        strategy["name"] = f"Strategy_{i+1}"

    return strategies