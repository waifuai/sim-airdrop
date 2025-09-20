"""
Visualization module for airdrop simulation results.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class SimulationVisualizer:
    """Handles visualization of simulation results."""

    def __init__(self, save_dir: str = "results/plots/"):
        """
        Initialize the visualizer.

        Args:
            save_dir (str): Directory to save plots.
        """
        self.save_dir = save_dir
        import os
        os.makedirs(save_dir, exist_ok=True)

    def plot_price_history(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot price history for all strategies.

        Args:
            results (List[Dict[str, Any]]): Simulation results.
            save_path (Optional[str]): Path to save the plot.

        Returns:
            plt.Figure: The matplotlib figure.
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        for result in results:
            price_history = result.get('price_history', [])
            if price_history:
                steps = range(len(price_history))
                ax.plot(steps, price_history, label=result['airdrop_strategy_name'], alpha=0.7)

        ax.set_xlabel('Simulation Steps')
        ax.set_ylabel('Token Price ($)')
        ax.set_title('Price History Comparison')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.tight_layout()
        return fig

    def plot_final_prices_comparison(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a bar plot comparing final prices of all strategies.

        Args:
            results (List[Dict[str, Any]]): Simulation results.
            save_path (Optional[str]): Path to save the plot.

        Returns:
            plt.Figure: The matplotlib figure.
        """
        df = pd.DataFrame(results)
        df = df.sort_values('final_price', ascending=False)

        fig, ax = plt.subplots(figsize=(14, 8))

        bars = ax.bar(range(len(df)), df['final_price'], color=plt.cm.viridis(np.linspace(0, 1, len(df))))

        ax.set_xlabel('Strategy')
        ax.set_ylabel('Final Price ($)')
        ax.set_title('Final Price Comparison Across Strategies')
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels([name[:20] + '...' if len(name) > 20 else name for name in df['airdrop_strategy_name']], rotation=45, ha='right')

        # Add value labels on bars
        for bar, price in zip(bars, df['final_price']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f'${price:.4f}', ha='center', va='bottom', fontsize=9)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.tight_layout()
        return fig

    def plot_supply_impact(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot the relationship between final supply and final price.

        Args:
            results (List[Dict[str, Any]]): Simulation results.
            save_path (Optional[str]): Path to save the plot.

        Returns:
            plt.Figure: The matplotlib figure.
        """
        df = pd.DataFrame(results)

        fig, ax = plt.subplots(figsize=(10, 8))

        scatter = ax.scatter(df['final_supply'], df['final_price'],
                           c=df['final_price'], cmap='viridis',
                           s=100, alpha=0.7, edgecolors='black')

        # Add strategy labels for outliers
        for _, row in df.iterrows():
            if row['final_price'] > df['final_price'].quantile(0.8) or row['final_price'] < df['final_price'].quantile(0.2):
                ax.annotate(row['airdrop_strategy_name'][:15] + '...',
                           (row['final_supply'], row['final_price']),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax.set_xlabel('Final Supply')
        ax.set_ylabel('Final Price ($)')
        ax.set_title('Supply vs Price Relationship')
        plt.colorbar(scatter, ax=ax, label='Final Price ($)')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.tight_layout()
        return fig

    def create_strategy_comparison_table(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> pd.DataFrame:
        """
        Create a comparison table of all strategies.

        Args:
            results (List[Dict[str, Any]]): Simulation results.
            save_path (Optional[str]): Path to save the table as CSV.

        Returns:
            pd.DataFrame: The comparison table.
        """
        df = pd.DataFrame(results)

        # Extract strategy parameters for comparison
        strategy_details = []
        for result in results:
            strategy_str = result.get('strategy_details', '{}')
            # Simple parsing of strategy string - in production, you'd want more robust parsing
            strategy_details.append(strategy_str)

        df['strategy_summary'] = strategy_details
        df = df[['airdrop_strategy_name', 'final_price', 'final_supply', 'strategy_summary']]
        df = df.sort_values('final_price', ascending=False)

        if save_path:
            df.to_csv(save_path, index=False)

        return df

    def generate_interactive_dashboard(self, results: List[Dict[str, Any]], output_file: str = "results/dashboard.html") -> None:
        """
        Generate an interactive dashboard using Plotly.

        Args:
            results (List[Dict[str, Any]]): Simulation results.
            output_file (str): Path to save the dashboard.
        """
        df = pd.DataFrame(results)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Final Price Comparison', 'Supply vs Price', 'Price History', 'Strategy Performance'),
            specs=[[{'type': 'bar'}, {'type': 'scatter'}],
                   [{'type': 'scatter'}, {'type': 'table'}]]
        )

        # 1. Final Price Bar Chart
        fig.add_trace(
            go.Bar(x=df['airdrop_strategy_name'], y=df['final_price'], name='Final Price',
                   marker_color=df['final_price'], marker_colorscale='Viridis'),
            row=1, col=1
        )

        # 2. Supply vs Price Scatter
        fig.add_trace(
            go.Scatter(x=df['final_supply'], y=df['final_price'],
                      mode='markers', name='Supply vs Price',
                      marker=dict(color=df['final_price'], colorscale='Viridis', showscale=True),
                      text=df['airdrop_strategy_name']),
            row=1, col=2
        )

        # 3. Price History (using first few strategies as example)
        for i, result in enumerate(results[:5]):  # Show first 5 strategies
            price_history = result.get('price_history', [])
            if price_history:
                steps = list(range(len(price_history)))
                fig.add_trace(
                    go.Scatter(x=steps, y=price_history, mode='lines', name=result['airdrop_strategy_name'][:20]),
                    row=2, col=1
                )

        # 4. Strategy Performance Table
        df_table = df[['airdrop_strategy_name', 'final_price', 'final_supply']].copy()
        df_table['final_price'] = df_table['final_price'].round(4)
        df_table['final_supply'] = df_table['final_supply'].round(0)

        fig.add_trace(
            go.Table(
                header=dict(values=['Strategy', 'Final Price ($)', 'Final Supply'],
                           fill_color='paleturquoise', align='left'),
                cells=dict(values=[df_table['airdrop_strategy_name'],
                                  df_table['final_price'],
                                  df_table['final_supply']],
                          fill_color='lavender', align='left')
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(height=800, width=1200, title_text="Airdrop Simulation Dashboard")
        fig.update_xaxes(tickangle=45)

        # Save dashboard
        fig.write_html(output_file)
        print(f"Interactive dashboard saved to {output_file}")

    def plot_strategy_parameters_impact(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> plt.Figure:
        """
        Analyze and plot the impact of different strategy parameters on final price.

        Args:
            results (List[Dict[str, Any]]): Simulation results.
            save_path (Optional[str]): Path to save the plot.

        Returns:
            plt.Figure: The matplotlib figure.
        """
        df = pd.DataFrame(results)

        # Extract parameters from strategy details (simplified parsing)
        df['strategy_type'] = df['strategy_details'].str.extract(r"'type':\s*'([^']*)'")
        df['vesting_type'] = df['strategy_details'].str.extract(r"'vesting':\s*'([^']*)'")
        df['percentage'] = df['strategy_details'].str.extract(r"'percentage':\s*([\d.]+)").astype(float)

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()

        # Strategy type impact
        if 'strategy_type' in df.columns:
            sns.boxplot(data=df, x='strategy_type', y='final_price', ax=axes[0])
            axes[0].set_title('Final Price by Strategy Type')
            axes[0].tick_params(axis='x', rotation=45)

        # Vesting type impact
        if 'vesting_type' in df.columns:
            sns.boxplot(data=df, x='vesting_type', y='final_price', ax=axes[1])
            axes[1].set_title('Final Price by Vesting Type')
            axes[1].tick_params(axis='x', rotation=45)

        # Percentage impact
        if 'percentage' in df.columns:
            axes[2].scatter(df['percentage'], df['final_price'], alpha=0.6)
            axes[2].set_xlabel('Airdrop Percentage')
            axes[2].set_ylabel('Final Price ($)')
            axes[2].set_title('Airdrop Percentage vs Final Price')

        # Hide unused subplot
        axes[3].set_visible(False)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig


def generate_comprehensive_report(results: List[Dict[str, Any]], output_dir: str = "results/") -> None:
    """
    Generate a comprehensive visualization report.

    Args:
        results (List[Dict[str, Any]]): Simulation results.
        output_dir (str): Directory to save all outputs.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    visualizer = SimulationVisualizer(output_dir + "plots/")

    print("Generating comprehensive visualization report...")

    # Generate all plots
    visualizer.plot_price_history(results, f"{output_dir}plots/price_history.png")
    visualizer.plot_final_prices_comparison(results, f"{output_dir}plots/final_prices_comparison.png")
    visualizer.plot_supply_impact(results, f"{output_dir}plots/supply_impact.png")
    visualizer.plot_strategy_parameters_impact(results, f"{output_dir}plots/parameter_impact.png")

    # Generate comparison table
    comparison_table = visualizer.create_strategy_comparison_table(results, f"{output_dir}strategy_comparison.csv")

    # Generate interactive dashboard
    visualizer.generate_interactive_dashboard(results, f"{output_dir}interactive_dashboard.html")

    # Generate summary statistics
    df = pd.DataFrame(results)
    summary_stats = df[['final_price', 'final_supply']].describe()

    with open(f"{output_dir}summary_report.txt", 'w') as f:
        f.write("Airdrop Simulation Summary Report\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Total Strategies Evaluated: {len(results)}\n")
        f.write(f"Best Performing Strategy: {df.loc[df['final_price'].idxmax(), 'airdrop_strategy_name']}\n")
        f.write(f"Best Final Price: ${df['final_price'].max():.4f}\n")
        f.write(f"Worst Performing Strategy: {df.loc[df['final_price'].idxmin(), 'airdrop_strategy_name']}\n")
        f.write(f"Worst Final Price: ${df['final_price'].min():.4f}\n\n")
        f.write("Summary Statistics:\n")
        f.write(summary_stats.to_string())

    print(f"Comprehensive report generated in {output_dir}")
    print(f"- Interactive dashboard: {output_dir}interactive_dashboard.html")
    print(f"- Summary report: {output_dir}summary_report.txt")
    print(f"- Strategy comparison: {output_dir}strategy_comparison.csv")
    print(f"- Plots saved in: {output_dir}plots/")