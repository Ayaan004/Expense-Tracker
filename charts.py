"""
Embedded Matplotlib Charts for CustomTkinter GUI.
Tailored for sleek modern financial analytics in Dark and Light themes.
"""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
from typing import List, Tuple, Dict, Any, Optional
import tkinter as tk

# Modern color palette
PALETTE = [
    "#6366F1",  # Indigo
    "#EC4899",  # Pink
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#3B82F6",  # Blue
    "#8B5CF6",  # Purple
    "#14B8A6",  # Teal
    "#F43F5E",  # Rose
    "#84CC16",  # Lime
    "#06B6D4",  # Cyan
    "#A855F7",  # Violet
    "#64748B",  # Slate
]

THEME_COLORS = {
    "dark": {
        "bg": "#1E222A",
        "card_bg": "#242933",
        "text": "#E2E8F0",
        "muted_text": "#94A3B8",
        "grid": "#333A48",
        "income": "#10B981",
        "expense": "#F43F5E",
        "accent": "#6366F1"
    },
    "light": {
        "bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "text": "#1E293B",
        "muted_text": "#64748B",
        "grid": "#E2E8F0",
        "income": "#059669",
        "expense": "#E11D48",
        "accent": "#4F46E5"
    }
}


def create_donut_chart(parent: tk.Widget, data: List[Tuple[str, float]], 
                       currency: str = "$", theme: str = "dark") -> FigureCanvasTkAgg:
    """Creates a modern donut chart showing category distribution."""
    colors_cfg = THEME_COLORS.get(theme, THEME_COLORS["dark"])

    fig, ax = plt.subplots(figsize=(4.5, 3.8), dpi=100)
    fig.patch.set_facecolor(colors_cfg["card_bg"])
    ax.set_facecolor(colors_cfg["card_bg"])

    if not data or sum(val for _, val in data) == 0:
        # Empty state
        ax.text(0.5, 0.5, "No expense data yet",
                horizontalalignment='center', verticalalignment='center',
                fontsize=11, color=colors_cfg["muted_text"], transform=ax.transAxes)
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        plt.close(fig)
        return canvas

    # Limit to top 6 categories + 'Other'
    if len(data) > 6:
        top_cats = data[:5]
        other_sum = sum(val for _, val in data[5:])
        top_cats.append(("Other", other_sum))
        data = top_cats

    labels = [cat for cat, _ in data]
    values = [val for _, val in data]
    total_spent = sum(values)

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        autopct='%1.0f%%',
        pctdistance=0.8,
        startangle=140,
        colors=PALETTE[:len(values)],
        wedgeprops=dict(width=0.38, edgecolor=colors_cfg["card_bg"], linewidth=2.5)
    )

    for autotext in autotexts:
        autotext.set_color('#FFFFFF')
        autotext.set_fontsize(9)
        autotext.set_weight('bold')

    # Center label inside donut hole
    ax.text(0, 0.1, "Total", horizontalalignment='center', verticalalignment='center',
            fontsize=10, color=colors_cfg["muted_text"], weight='normal')
    ax.text(0, -0.15, f"{currency}{total_spent:,.0f}", horizontalalignment='center', verticalalignment='center',
            fontsize=12, color=colors_cfg["text"], weight='bold')

    # Modern compact legend at bottom
    legend_labels = [f"{lbl} ({val / total_spent * 100:.0f}%)" for lbl, val in zip(labels, values)]
    legend = ax.legend(wedges, legend_labels, loc="center", bbox_to_anchor=(0.5, -0.12),
                       ncol=2, frameon=False, fontsize=8, labelcolor=colors_cfg["text"])
    
    plt.subplots_adjust(top=0.95, bottom=0.22, left=0.05, right=0.95)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    plt.close(fig)
    return canvas


def create_trend_bar_chart(parent: tk.Widget, trend_data: List[Dict[str, Any]], 
                           currency: str = "$", theme: str = "dark") -> FigureCanvasTkAgg:
    """Creates a dual grouped bar chart comparing Monthly Income vs Expenses."""
    colors_cfg = THEME_COLORS.get(theme, THEME_COLORS["dark"])

    fig, ax = plt.subplots(figsize=(5.6, 3.8), dpi=100)
    fig.patch.set_facecolor(colors_cfg["card_bg"])
    ax.set_facecolor(colors_cfg["card_bg"])

    if not trend_data:
        ax.text(0.5, 0.5, "No trend data yet",
                horizontalalignment='center', verticalalignment='center',
                fontsize=11, color=colors_cfg["muted_text"], transform=ax.transAxes)
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        plt.close(fig)
        return canvas

    months = [d["label"] for d in trend_data]
    incomes = [d["income"] for d in trend_data]
    expenses = [d["expense"] for d in trend_data]

    x = range(len(months))
    width = 0.35

    bar1 = ax.bar([i - width/2 for i in x], incomes, width, label='Income', 
                  color=colors_cfg["income"], alpha=0.9, edgecolor='none', zorder=3)
    bar2 = ax.bar([i + width/2 for i in x], expenses, width, label='Expense', 
                  color=colors_cfg["expense"], alpha=0.9, edgecolor='none', zorder=3)

    # Style axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(colors_cfg["grid"])
    ax.spines['bottom'].set_color(colors_cfg["grid"])
    ax.tick_params(colors=colors_cfg["muted_text"], labelsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(months, color=colors_cfg["text"], fontsize=9, weight='bold')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"{currency}{val:,.0f}"))
    ax.grid(axis='y', linestyle='--', alpha=0.35, color=colors_cfg["grid"], zorder=0)

    # Legend
    legend = ax.legend(loc='upper right', frameon=False, fontsize=8, labelcolor=colors_cfg["text"])

    plt.subplots_adjust(top=0.92, bottom=0.18, left=0.15, right=0.95)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    plt.close(fig)
    return canvas


def create_category_bar_chart(parent: tk.Widget, data: List[Tuple[str, float]], 
                              currency: str = "$", theme: str = "dark") -> FigureCanvasTkAgg:
    """Creates a horizontal bar chart of top spending categories."""
    colors_cfg = THEME_COLORS.get(theme, THEME_COLORS["dark"])

    fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=100)
    fig.patch.set_facecolor(colors_cfg["card_bg"])
    ax.set_facecolor(colors_cfg["card_bg"])

    if not data:
        ax.text(0.5, 0.5, "No category data available",
                horizontalalignment='center', verticalalignment='center',
                fontsize=11, color=colors_cfg["muted_text"], transform=ax.transAxes)
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        plt.close(fig)
        return canvas

    # Take top 7
    top_data = data[:7]
    top_data.reverse()  # Top at the top

    cats = [c for c, _ in top_data]
    vals = [v for _, v in top_data]

    y_pos = range(len(cats))
    bars = ax.barh(y_pos, vals, color=PALETTE[:len(cats)], height=0.55, zorder=3)

    # Value annotations on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + (max(vals) * 0.02), bar.get_y() + bar.get_height()/2,
                f"{currency}{width:,.0f}",
                va='center', ha='left', fontsize=8, color=colors_cfg["text"], weight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats, color=colors_cfg["text"], fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(colors_cfg["grid"])
    ax.spines['bottom'].set_color(colors_cfg["grid"])
    ax.tick_params(colors=colors_cfg["muted_text"], labelsize=8)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f"{currency}{val:,.0f}"))
    ax.grid(axis='x', linestyle='--', alpha=0.35, color=colors_cfg["grid"], zorder=0)

    # Give room for text on the right
    ax.set_xlim(0, max(vals) * 1.25 if vals else 100)

    plt.subplots_adjust(top=0.92, bottom=0.15, left=0.32, right=0.92)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    plt.close(fig)
    return canvas
