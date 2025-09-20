"""
Logging module for airdrop simulation.
"""
import logging
import logging.handlers
import sys
from typing import Dict, Any, Optional
import numpy as np
from pathlib import Path


class SimulationLogger:
    """Custom logger for simulation events."""

    def __init__(self, name: str = "airdrop_simulation", log_file: Optional[str] = None, level: int = logging.INFO):
        """
        Initialize the logger.

        Args:
            name (str): Logger name.
            log_file (Optional[str]): Path to log file. If None, logs to console only.
            level (int): Logging level.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB max, 5 backups
            )
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log_simulation_start(self, params: Dict[str, Any]) -> None:
        """Log the start of a simulation."""
        self.logger.info("=" * 50)
        self.logger.info("STARTING AIRDROP SIMULATION")
        self.logger.info("=" * 50)
        self.logger.info(f"Parameters: {params}")
        self.logger.info(f"Strategy: {params.get('airdrop_strategy', {}).get('name', 'Unknown')}")

    def log_simulation_end(self, duration: float, results: Dict[str, Any]) -> None:
        """Log the end of a simulation."""
        self.logger.info("=" * 50)
        self.logger.info("SIMULATION COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Final Price: ${results.get('final_price', 0):.4f}")
        self.logger.info(f"Final Supply: {results.get('final_supply', 0):.0f}")

    def log_step_info(self, step: int, price: float, total_supply: float, market_sentiment: float) -> None:
        """Log information for each simulation step."""
        if step % 100 == 0:  # Log every 100 steps to avoid spam
            self.logger.debug(f"Step {step}: Price=${price:.4f}, Supply={total_supply:.0f}, Sentiment={market_sentiment:.3f}")

    def log_strategy_info(self, strategy_name: str, strategy: Dict[str, Any]) -> None:
        """Log detailed strategy information."""
        self.logger.info(f"Running strategy: {strategy_name}")
        self.logger.info(f"  Type: {strategy.get('type', 'Unknown')}")
        self.logger.info(f"  Percentage: {strategy.get('percentage', 0) * 100:.1f}%")
        self.logger.info(f"  Vesting: {strategy.get('vesting', 'Unknown')}")
        if strategy.get('vesting') != 'none':
            self.logger.info(f"  Vesting periods: {strategy.get('vesting_periods', 'Unknown')}")

    def log_error(self, error: Exception, context: str = "") -> None:
        """Log an error with context."""
        self.logger.error(f"Error in {context}: {str(error)}")
        self.logger.error(f"Error type: {type(error).__name__}")
        if hasattr(error, '__traceback__'):
            self.logger.error("Traceback:", exc_info=True)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def log_array_stats(self, name: str, array: np.ndarray) -> None:
        """Log statistics for a numpy array."""
        if array.size == 0:
            self.logger.debug(f"{name}: Empty array")
            return

        self.logger.debug(f"{name} stats - Mean: {np.mean(array):.4f}, Std: {np.std(array):.4f}, Min: {np.min(array):.4f}, Max: {np.max(array):.4f}")


# Global logger instance
simulation_logger = SimulationLogger()


def get_logger() -> SimulationLogger:
    """Get the global simulation logger."""
    return simulation_logger


def setup_logging(log_file: Optional[str] = "logs/simulation.log", level: str = "INFO") -> SimulationLogger:
    """
    Setup logging configuration.

    Args:
        log_file (Optional[str]): Path to log file.
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        SimulationLogger: Configured logger instance.
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    return SimulationLogger("airdrop_simulation", log_file, level_map.get(level.upper(), logging.INFO))