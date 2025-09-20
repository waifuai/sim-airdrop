import argparse
import time
import pandas as pd
from config import INITIAL_TOKENS, INITIAL_PRICE, NUM_USERS, SIMULATION_STEPS, MAX_STRATEGIES
from strategies import AIRDROP_PARAMETER_GRID, generate_airdrop_strategies
from simulation import run_simulation
from logger import get_logger, setup_logging
from validation import ValidationError
from visualization import generate_comprehensive_report
from typing import List, Dict, Any, Tuple

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Run the airdrop simulation.")
parser.add_argument('--num_users', type=int, default=NUM_USERS, help='Number of users in the simulation')
parser.add_argument('--steps', type=int, default=SIMULATION_STEPS, help='Number of simulation steps')
parser.add_argument('--initial_tokens', type=int, default=INITIAL_TOKENS, help='Initial tokens per user')
parser.add_argument('--initial_price', type=float, default=INITIAL_PRICE, help='Initial token price')
parser.add_argument('--volatility', type=float, default=0.0, help='Price volatility factor')
parser.add_argument('--max_strategies', type=int, default=MAX_STRATEGIES, help='Maximum number of strategies to generate')
args = parser.parse_args()

# --- Main Execution Block ---
logger = setup_logging("logs/simulation.log", "INFO")

try:
    AIRDROP_STRATEGIES = generate_airdrop_strategies(AIRDROP_PARAMETER_GRID, args.max_strategies)
    logger.logger.info(f"Generated {len(AIRDROP_STRATEGIES)} strategies")

    all_results: List[Dict[str, Any]] = []
    start_time: float = time.time()

    for i, airdrop_strategy in enumerate(AIRDROP_STRATEGIES):
        airdrop_name = airdrop_strategy["name"]
        logger.log_strategy_info(airdrop_name, airdrop_strategy)

        try:
            params = {
                'num_users': args.num_users,
                'simulation_steps': args.steps,
                'initial_tokens': args.initial_tokens,
                'initial_price': args.initial_price,
                'market_sentiment': 0.0,
                'airdrop_strategy': airdrop_strategy
            }

            logger.log_simulation_start(params)
            price_history, final_supply, market_sentiment_history = run_simulation(params)

            result: Dict[str, Any] = {
                "airdrop_strategy_name": airdrop_name,
                "final_price": price_history[-1] if price_history else 0.0,
                "price_history": price_history,
                "final_supply": final_supply,
                "market_sentiment_history": market_sentiment_history,
                "strategy_details": str(airdrop_strategy)
            }
            all_results.append(result)

            logger.log_simulation_end(time.time() - start_time, result)
            logger.logger.info(f"Completed strategy {i+1}/{len(AIRDROP_STRATEGIES)}")

        except Exception as e:
            logger.log_error(e, f"Strategy {airdrop_name}")
            logger.logger.error(f"Skipping strategy {airdrop_name} due to error")
            continue

    end_time: float = time.time()
    total_duration = end_time - start_time
    logger.logger.info(f"All simulations completed in {total_duration:.2f} seconds")
    logger.logger.info(f"Successfully ran {len(all_results)} out of {len(AIRDROP_STRATEGIES)} strategies")

except ValidationError as e:
    logger.log_error(e, "Parameter validation")
    print(f"Parameter validation error: {e}")
    exit(1)
except Exception as e:
    logger.log_error(e, "Main execution")
    print(f"Unexpected error: {e}")
    exit(1)

# --- Create DataFrame ---
df = pd.DataFrame(all_results)

# --- Save Results ---
df.to_csv("airdrop_simulation_results.csv", index=False)
logger.logger.info("Results saved to airdrop_simulation_results.csv")

# --- Generate Comprehensive Report ---
try:
    logger.logger.info("Generating visualization report...")
    generate_comprehensive_report(all_results, "results/")
    logger.logger.info("Visualization report generated successfully")
except Exception as e:
    logger.log_error(e, "Visualization generation")
    logger.logger.warning("Could not generate visualization report")

# --- Display Best Strategy ---
if all_results:
    best_strategy_name = df.loc[df['final_price'].idxmax(), 'airdrop_strategy_name']
    print(f"\nBest Strategy (Highest Final Price): {best_strategy_name}")
    print(f"  Final Price: ${df.loc[df['final_price'].idxmax(), 'final_price']:.4f}")
    print(f"  Final Supply: {df.loc[df['final_price'].idxmax(), 'final_supply']:.2f}")
    print(f"  Strategy Details: {df.loc[df['final_price'].idxmax(), 'strategy_details']}")

    logger.logger.info(f"Best performing strategy: {best_strategy_name} with final price ${df['final_price'].max():.4f}")