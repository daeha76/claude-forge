"""
Chart generator module for data research reports.
Provides functions to create various chart types with QJC branding.
"""

import itertools
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def setup_korean_font() -> None:
    """Configure matplotlib to render Korean text correctly."""
    try:
        matplotlib.rcParams["font.family"] = "AppleGothic"
    except Exception:
        matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["axes.unicode_minus"] = False


setup_korean_font()

QJC_PALETTE = [
    "#4F46E5", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#06B6D4", "#F97316",
]


def get_qjc_colors(n: int = 7) -> List[str]:
    """Return n colors cycling through the QJC palette."""
    return [color for _, color in zip(range(n), itertools.cycle(QJC_PALETTE))]


def save_chart(fig: matplotlib.figure.Figure, output_path: str, dpi: int = 300) -> None:
    """Save figure to disk at specified DPI and close it."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def create_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str,
    output_path: str,
    labels: Optional[Dict[str, str]] = None,
) -> str:
    """Create a time-series line chart and save it."""
    try:
        colors = get_qjc_colors(len(y_cols))
        fig, ax = plt.subplots(figsize=(12, 7))

        for col, color in zip(y_cols, colors):
            display_label = (labels or {}).get(col, col)
            ax.plot(df[x_col], df[col], color=color, label=display_label, linewidth=2)

        ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel(x_col, fontsize=12)
        ax.grid(True, alpha=0.3, color="lightgray")
        if len(y_cols) > 1:
            ax.legend(fontsize=10)
        fig.tight_layout()
        save_chart(fig, output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Line chart creation failed: {e}") from e


def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    output_path: str,
    horizontal: bool = False,
) -> str:
    """Create a comparison bar chart and save it."""
    try:
        colors = get_qjc_colors(len(df))
        fig, ax = plt.subplots(figsize=(12, 7))

        if horizontal:
            ax.barh(df[x_col], df[y_col], color=colors)
            ax.set_xlabel(y_col, fontsize=12)
            ax.set_ylabel(x_col, fontsize=12)
        else:
            ax.bar(df[x_col], df[y_col], color=colors)
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)

        ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
        ax.grid(True, alpha=0.3, color="lightgray", axis="y" if not horizontal else "x")
        fig.tight_layout()
        save_chart(fig, output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Bar chart creation failed: {e}") from e


def create_heatmap(
    df: pd.DataFrame,
    title: str,
    output_path: str,
    annot: bool = True,
) -> str:
    """Create a correlation heatmap using seaborn and save it."""
    try:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.heatmap(
            df,
            annot=annot,
            fmt=".2f",
            cmap="YlOrRd",
            linewidths=0.5,
            ax=ax,
            square=True,
        )
        ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
        fig.tight_layout()
        save_chart(fig, output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Heatmap creation failed: {e}") from e


def create_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    output_path: str,
    hue_col: Optional[str] = None,
) -> str:
    """Create a scatter plot with optional color grouping and save it."""
    try:
        fig, ax = plt.subplots(figsize=(12, 7))

        if hue_col is not None:
            groups = df[hue_col].unique()
            colors = get_qjc_colors(len(groups))
            for group, color in zip(groups, colors):
                subset = df[df[hue_col] == group]
                ax.scatter(subset[x_col], subset[y_col], color=color, label=group, alpha=0.7, s=60)
            ax.legend(fontsize=10)
        else:
            ax.scatter(df[x_col], df[y_col], color=QJC_PALETTE[0], alpha=0.7, s=60)

        ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.grid(True, alpha=0.3, color="lightgray")
        fig.tight_layout()
        save_chart(fig, output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Scatter plot creation failed: {e}") from e


def create_multi_line_chart(
    data_dict: Dict[str, Tuple[Union[List, np.ndarray], Union[List, np.ndarray]]],
    title: str,
    output_path: str,
    xlabel: str = "",
    ylabel: str = "",
) -> str:
    """Create a multi-series line chart from a dict of {label: (x_data, y_data)}."""
    try:
        colors = get_qjc_colors(len(data_dict))
        fig, ax = plt.subplots(figsize=(12, 7))

        for (label, (x_data, y_data)), color in zip(data_dict.items(), colors):
            ax.plot(x_data, y_data, color=color, label=label, linewidth=2)

        ax.set_title(title, fontsize=16, fontweight="bold", pad=15)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3, color="lightgray")
        if len(data_dict) > 1:
            ax.legend(fontsize=10)
        fig.tight_layout()
        save_chart(fig, output_path)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Multi-line chart creation failed: {e}") from e


if __name__ == "__main__":
    # Sample data for verification
    dates = pd.date_range("2024-01-01", periods=12, freq="ME")
    sample_df = pd.DataFrame({
        "date": dates,
        "revenue": np.random.randint(100, 500, size=12),
        "cost": np.random.randint(50, 300, size=12),
    })

    line_path = create_line_chart(
        sample_df, "date", ["revenue", "cost"],
        "Monthly Revenue vs Cost", "/tmp/sample_line_chart.png",
        labels={"revenue": "Revenue", "cost": "Cost"},
    )
    print(f"Line chart saved: {line_path}")

    bar_df = pd.DataFrame({
        "category": ["A", "B", "C", "D", "E"],
        "value": [42, 78, 55, 91, 33],
    })
    bar_path = create_bar_chart(
        bar_df, "category", "value",
        "Category Comparison", "/tmp/sample_bar_chart.png",
    )
    print(f"Bar chart saved: {bar_path}")
