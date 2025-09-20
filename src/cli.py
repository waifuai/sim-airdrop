#!/usr/bin/env python3
"""
Command Line Interface for Airdrop Simulation Tool.
"""
import click
import time
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from config import INITIAL_TOKENS, INITIAL_PRICE, NUM_USERS, SIMULATION_STEPS, MAX_STRATEGIES
from strategies import AIRDROP_PARAMETER_GRID, generate_airdrop_strategies
from simulation import run_simulation
from logger import setup_logging
from validation import ValidationError
from visualization import generate_comprehensive_report


@click.group()
@click.version_option("1.0.0")
def cli():
    """Airdrop Simulation Tool - Analyze token airdrop strategies and their market impact."""
    pass


@cli.command()
@click.option('--num-users', default=NUM_USERS, type=int, help='Number of users in the simulation')
@click.option('--steps', default=SIMULATION_STEPS, type=int, help='Number of simulation steps')
@click.option('--initial-tokens', default=INITIAL_TOKENS, type=int, help='Initial tokens per user')
@click.option('--initial-price', default=INITIAL_PRICE, type=float, help='Initial token price')
@click.option('--max-strategies', default=MAX_STRATEGIES, type=int, help='Maximum number of strategies to generate')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), help='Logging level')
@click.option('--output-dir', default='results/', type=click.Path(), help='Output directory for results')
@click.option('--config-file', type=click.Path(exists=True), help='JSON configuration file')
def run(num_users: int, steps: int, initial_tokens: int, initial_price: float,
        max_strategies: int, log_level: str, output_dir: str, config_file: Optional[str]):
    """Run the airdrop simulation with specified parameters."""

    # Setup logging
    logger = setup_logging(f"{output_dir}/simulation.log", log_level)

    try:
        # Load config file if provided
        if config_file:
            with open(config_file, 'r') as f:
                config = json.load(f)
                num_users = config.get('num_users', num_users)
                steps = config.get('steps', steps)
                initial_tokens = config.get('initial_tokens', initial_tokens)
                initial_price = config.get('initial_price', initial_price)
                max_strategies = config.get('max_strategies', max_strategies)

        click.echo(f"🚀 Starting Airdrop Simulation")
        click.echo(f"   Users: {num_users}")
        click.echo(f"   Steps: {steps}")
        click.echo(f"   Initial Tokens: {initial_tokens:,}")
        click.echo(f"   Initial Price: ${initial_price}")
        click.echo(f"   Max Strategies: {max_strategies}")
        click.echo(f"   Output Directory: {output_dir}")
        click.echo("")

        # Generate strategies
        with click.progressbar(length=max_strategies, label='Generating strategies') as bar:
            AIRDROP_STRATEGIES = generate_airdrop_strategies(AIRDROP_PARAMETER_GRID, max_strategies)
            bar.update(max_strategies)

        click.echo(f"✅ Generated {len(AIRDROP_STRATEGIES)} strategies")

        # Run simulations
        all_results: List[Dict[str, Any]] = []
        start_time: float = time.time()

        with click.progressbar(AIRDROP_STRATEGIES, label='Running simulations') as bar:
            for airdrop_strategy in bar:
                try:
                    params = {
                        'num_users': num_users,
                        'simulation_steps': steps,
                        'initial_tokens': initial_tokens,
                        'initial_price': initial_price,
                        'market_sentiment': 0.0,
                        'airdrop_strategy': airdrop_strategy
                    }

                    price_history, final_supply, market_sentiment_history = run_simulation(params)

                    result: Dict[str, Any] = {
                        "airdrop_strategy_name": airdrop_strategy["name"],
                        "final_price": price_history[-1] if price_history else 0.0,
                        "price_history": price_history,
                        "final_supply": final_supply,
                        "market_sentiment_history": market_sentiment_history,
                        "strategy_details": str(airdrop_strategy)
                    }
                    all_results.append(result)

                except Exception as e:
                    click.echo(f"❌ Error in strategy {airdrop_strategy['name']}: {str(e)}", err=True)
                    continue

        end_time: float = time.time()
        total_duration = end_time - start_time

        # Save results
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(all_results)
        csv_path = f"{output_dir}/airdrop_simulation_results.csv"
        df.to_csv(csv_path, index=False)

        # Generate visualizations
        click.echo("📊 Generating visualizations...")
        generate_comprehensive_report(all_results, output_dir)

        # Display results
        if all_results:
            best_strategy = df.loc[df['final_price'].idxmax()]
            click.echo(f"\n🏆 Best Strategy: {best_strategy['airdrop_strategy_name']}")
            click.echo(f"   Final Price: ${best_strategy['final_price']:.4f}")
            click.echo(f"   Final Supply: {best_strategy['final_supply']:,.0f}")
            click.echo(f"   Improvement: {((best_strategy['final_price'] - initial_price) / initial_price * 100):.1f}%")

        click.echo(f"\n✅ Simulation completed in {total_duration:.1f} seconds")
        click.echo(f"   Results saved to: {csv_path}")
        click.echo(f"   Interactive dashboard: {output_dir}/interactive_dashboard.html")
        click.echo(f"   Summary report: {output_dir}/summary_report.txt")

    except ValidationError as e:
        click.echo(f"❌ Validation Error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected Error: {e}", err=True)
        exit(1)


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--output-dir', default='results/', type=click.Path(), help='Output directory for visualizations')
def visualize(results_file: str, output_dir: str):
    """Generate visualizations from existing simulation results."""

    try:
        click.echo(f"📊 Generating visualizations from {results_file}")

        # Load results
        df = pd.read_csv(results_file)
        results = df.to_dict('records')

        # Generate visualizations
        generate_comprehensive_report(results, output_dir)

        click.echo(f"✅ Visualizations generated successfully")
        click.echo(f"   Interactive dashboard: {output_dir}/interactive_dashboard.html")
        click.echo(f"   Summary report: {output_dir}/summary_report.txt")
        click.echo(f"   Plots saved in: {output_dir}/plots/")

    except Exception as e:
        click.echo(f"❌ Error generating visualizations: {e}", err=True)
        exit(1)


@cli.command()
@click.option('--num-strategies', default=5, type=int, help='Number of strategies to generate')
@click.option('--output-file', default='strategy_examples.json', type=click.Path(), help='Output file for strategies')
def generate_strategies(num_strategies: int, output_file: str):
    """Generate and display example strategies."""

    try:
        click.echo(f"🔧 Generating {num_strategies} example strategies")

        strategies = generate_airdrop_strategies(AIRDROP_PARAMETER_GRID, num_strategies)

        # Display strategies
        for i, strategy in enumerate(strategies, 1):
            click.echo(f"\n{i}. {strategy['name']}:")
            click.echo(f"   Type: {strategy.get('type', 'N/A')}")
            click.echo(f"   Percentage: {strategy.get('percentage', 0) * 100:.1f}%")
            click.echo(f"   Vesting: {strategy.get('vesting', 'N/A')}")

            if strategy.get('vesting') != 'none':
                click.echo(f"   Vesting Periods: {strategy.get('vesting_periods', 'N/A')}")

            if strategy.get('criteria'):
                click.echo(f"   Criteria: {strategy.get('criteria', 'N/A')}")

        # Save to file
        with open(output_file, 'w') as f:
            json.dump(strategies, f, indent=2)

        click.echo(f"\n✅ Strategies saved to {output_file}")

    except Exception as e:
        click.echo(f"❌ Error generating strategies: {e}", err=True)
        exit(1)


@cli.command()
@click.argument('config_file', type=click.Path())
def validate_config(config_file: str):
    """Validate a configuration file."""

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        click.echo(f"✅ Configuration file {config_file} is valid")
        click.echo("\nConfiguration:")
        click.echo(json.dumps(config, indent=2))

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON in {config_file}: {e}", err=True)
        exit(1)
    except FileNotFoundError:
        click.echo(f"❌ Configuration file {config_file} not found", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Error validating config: {e}", err=True)
        exit(1)


@cli.command()
@click.option('--config-template', default='config_template.json', type=click.Path(), help='Output file for config template')
def create_config_template(config_template: str):
    """Create a configuration template file."""

    template = {
        "num_users": 100,
        "steps": 1024,
        "initial_tokens": 1000000000,
        "initial_price": 0.10,
        "max_strategies": 5,
        "log_level": "INFO",
        "description": "Airdrop simulation configuration",
        "notes": [
            "num_users: Number of users in the simulation (default: 100)",
            "steps: Number of simulation steps (default: 1024)",
            "initial_tokens: Total token supply (default: 1,000,000,000)",
            "initial_price: Starting price per token in USD (default: 0.10)",
            "max_strategies: Maximum number of strategies to generate (default: 5)",
            "log_level: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)"
        ]
    }

    try:
        with open(config_template, 'w') as f:
            json.dump(template, f, indent=2)

        click.echo(f"✅ Configuration template created: {config_template}")
        click.echo("\nEdit this file to customize your simulation parameters.")

    except Exception as e:
        click.echo(f"❌ Error creating config template: {e}", err=True)
        exit(1)


if __name__ == '__main__':
    cli()