"""
VaultFlow - Professional Expense Tracker & Financial Intelligence GUI
Built with CustomTkinter, SQLite, and Matplotlib.
"""

import sys
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

from database import DatabaseManager
from charts import create_donut_chart, create_trend_bar_chart, create_category_bar_chart

# Configure CustomTkinter defaults
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else "Helvetica"


class ExpenseTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Database initialization
        self.db = DatabaseManager()

        # Window settings
        self.title("VaultFlow • Professional Expense Tracker")
        self.geometry("1240x800")
        self.minsize(1080, 700)

        # State variables
        self.current_theme = self.db.get_setting("theme", "dark")
        ctk.set_appearance_mode(self.current_theme.capitalize())
        self.currency = self.db.get_setting("currency", "$")
        self.current_view = "dashboard"
        self.selected_transaction_id = None

        # Build Main UI Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # If database is completely empty, populate demo data so the app looks stunning immediately
        if not self.db.get_transactions(limit=1):
            self.db.populate_demo_data()

        # Show initial view
        self.show_view("dashboard")

    # =========================================================================
    # SIDEBAR NAVIGATION
    # =========================================================================
    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # Brand / Logo
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(25, 20), sticky="ew")

        brand_label = ctk.CTkLabel(
            logo_frame,
            text="💎 VaultFlow",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold")
        )
        brand_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="Expense & Wealth Intelligence",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=("gray50", "gray60")
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("transactions", "💳  Transactions"),
            ("add", "➕  Add Record"),
            ("budgets", "🎯  Budgets & Limits"),
            ("analytics", "📈  Analytics"),
            ("settings", "⚙️  Settings & Data"),
        ]

        for idx, (view_name, text) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                height=42,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                text_color=("gray20", "gray85"),
                hover_color=("gray85", "#2A2F3D"),
                command=lambda v=view_name: self.show_view(v)
            )
            btn.grid(row=idx, column=0, padx=15, pady=4, sticky="ew")
            self.nav_buttons[view_name] = btn

        # Bottom Utilities Frame (Theme & Quick Info)
        bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color=("gray92", "#1C2029"), corner_radius=12)
        bottom_frame.grid(row=9, column=0, padx=15, pady=20, sticky="sew")

        # Theme Switcher
        theme_title = ctk.CTkLabel(
            bottom_frame,
            text="Appearance Mode",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
        )
        theme_title.pack(anchor="w", padx=12, pady=(10, 4))

        self.theme_segmented = ctk.CTkSegmentedButton(
            bottom_frame,
            values=["Dark", "Light"],
            command=self._on_theme_toggle,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11)
        )
        self.theme_segmented.set(self.current_theme.capitalize())
        self.theme_segmented.pack(fill="x", padx=12, pady=(0, 10))

        # Currency Indicator
        curr_label = ctk.CTkLabel(
            bottom_frame,
            text=f"Active Currency: {self.currency}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=("gray40", "gray60")
        )
        curr_label.pack(anchor="w", padx=12, pady=(0, 8))

    def _build_content_area(self):
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

    def show_view(self, view_name: str):
        self.current_view = view_name

        # Update sidebar button highlights
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(
                    fg_color=("#3B82F6", "#3B82F6"),
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray20", "gray85")
                )

        # Clear existing view content
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Render corresponding view
        if view_name == "dashboard":
            self._render_dashboard()
        elif view_name == "transactions":
            self._render_transactions()
        elif view_name == "add":
            self._render_add_transaction()
        elif view_name == "budgets":
            self._render_budgets()
        elif view_name == "analytics":
            self._render_analytics()
        elif view_name == "settings":
            self._render_settings()

    def _on_theme_toggle(self, value: str):
        theme_val = value.lower()
        self.current_theme = theme_val
        ctk.set_appearance_mode(value)
        self.db.set_setting("theme", theme_val)
        # Refresh current view so charts update their background colors
        self.show_view(self.current_view)

    # =========================================================================
    # VIEW 1: DASHBOARD
    # =========================================================================
    def _render_dashboard(self):
        container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Header with Greeting & Quick Add Button
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Executive Dashboard",
            font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold")
        )
        title_lbl.pack(side="left")

        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        demo_btn = ctk.CTkButton(
            actions_frame,
            text="⚡ Reset / Load Demo Data",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=("gray80", "#2E3440"),
            hover_color=("gray70", "#3E4451"),
            text_color=("gray10", "gray90"),
            height=34,
            command=self._load_demo_data_prompt
        )
        demo_btn.pack(side="left", padx=(0, 10))

        quick_add_btn = ctk.CTkButton(
            actions_frame,
            text="+ Add Transaction",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=34,
            command=lambda: self.show_view("add")
        )
        quick_add_btn.pack(side="left")

        # Key Metrics (KPIs)
        metrics = self.db.get_summary_metrics()

        cards_data = [
            ("Net Balance", f"{self.currency}{metrics['total_balance']:,.2f}", 
             "#10B981" if metrics['total_balance'] >= 0 else "#EF4444", "All-time accumulated wealth"),
            ("Monthly Income", f"{self.currency}{metrics['monthly_income']:,.2f}", 
             "#3B82F6", "Current month inflows"),
            ("Monthly Expenses", f"{self.currency}{metrics['monthly_expense']:,.2f}", 
             "#F43F5E", "Current month outflows"),
            ("Savings Rate", f"{metrics['savings_rate']:.1f}%", 
             "#8B5CF6", "Target: ≥ 20.0% of income")
        ]

        for i, (card_title, card_val, accent_color, subtext) in enumerate(cards_data):
            card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
            card.grid(row=1, column=i, padx=8, pady=(0, 20), sticky="nsew")

            # Accent color bar on top
            accent_bar = ctk.CTkFrame(card, height=4, fg_color=accent_color, corner_radius=2)
            accent_bar.pack(fill="x", padx=12, pady=(10, 8))

            c_title = ctk.CTkLabel(
                card,
                text=card_title,
                font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                text_color=("gray50", "gray60")
            )
            c_title.pack(anchor="w", padx=16)

            c_val = ctk.CTkLabel(
                card,
                text=card_val,
                font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
                text_color=accent_color
            )
            c_val.pack(anchor="w", padx=16, pady=(4, 2))

            c_sub = ctk.CTkLabel(
                card,
                text=subtext,
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=("gray60", "gray50")
            )
            c_sub.pack(anchor="w", padx=16, pady=(0, 14))

        # Middle Section: 2 Charts Side-by-Side
        charts_row = ctk.CTkFrame(container, fg_color="transparent")
        charts_row.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(0, 20))
        charts_row.grid_columnconfigure((0, 1), weight=1)

        # Left Chart: Trend Bar Chart
        left_chart_frame = ctk.CTkFrame(charts_row, fg_color=("white", "#1F242E"), corner_radius=12)
        left_chart_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        trend_title = ctk.CTkLabel(
            left_chart_frame,
            text="Income vs Expenses (6-Month Trend)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        )
        trend_title.pack(anchor="w", padx=16, pady=(14, 8))

        trend_data = self.db.get_monthly_trend(months_back=6)
        chart_theme = "light" if self.current_theme == "light" else "dark"
        trend_canvas = create_trend_bar_chart(left_chart_frame, trend_data, currency=self.currency, theme=chart_theme)
        trend_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Right Chart: Category Donut Chart
        right_chart_frame = ctk.CTkFrame(charts_row, fg_color=("white", "#1F242E"), corner_radius=12)
        right_chart_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        donut_title = ctk.CTkLabel(
            right_chart_frame,
            text="Expense Distribution by Category",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        )
        donut_title.pack(anchor="w", padx=16, pady=(14, 8))

        cat_breakdown = self.db.get_category_breakdown(trans_type="expense")
        donut_canvas = create_donut_chart(right_chart_frame, cat_breakdown, currency=self.currency, theme=chart_theme)
        donut_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Bottom Section: Recent Transactions
        recent_frame = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
        recent_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(0, 20))

        recent_header = ctk.CTkFrame(recent_frame, fg_color="transparent")
        recent_header.pack(fill="x", padx=16, pady=(14, 10))

        recent_lbl = ctk.CTkLabel(
            recent_header,
            text="Recent Activity",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
        )
        recent_lbl.pack(side="left")

        view_all_btn = ctk.CTkButton(
            recent_header,
            text="View All Transactions →",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=("#2563EB", "#60A5FA"),
            hover=False,
            command=lambda: self.show_view("transactions")
        )
        view_all_btn.pack(side="right")

        recent_txs = self.db.get_transactions(limit=6)
        if not recent_txs:
            empty_lbl = ctk.CTkLabel(
                recent_frame,
                text="No transactions recorded yet. Click '+ Add Transaction' to start!",
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                text_color=("gray50", "gray60")
            )
            empty_lbl.pack(pady=30)
        else:
            for tx in recent_txs:
                self._create_transaction_row(recent_frame, tx, is_compact=True)

    def _create_transaction_row(self, parent: ctk.CTkFrame, tx: dict, is_compact: bool = False):
        row = ctk.CTkFrame(parent, fg_color=("gray95", "#262C38"), corner_radius=8, height=44)
        row.pack(fill="x", padx=16, pady=4)
        row.pack_propagate(False)

        # Date
        date_lbl = ctk.CTkLabel(
            row,
            text=tx["date"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=("gray50", "gray55"),
            width=90
        )
        date_lbl.pack(side="left", padx=(12, 10))

        # Title
        title_lbl = ctk.CTkLabel(
            row,
            text=tx["title"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True, padx=5)

        # Category Badge
        cat_badge = ctk.CTkLabel(
            row,
            text=f" {tx['category']} ",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            fg_color=("gray85", "#323B4B"),
            corner_radius=4,
            text_color=("gray20", "gray80")
        )
        cat_badge.pack(side="left", padx=10)

        # Payment Method
        if not is_compact:
            method_lbl = ctk.CTkLabel(
                row,
                text=tx["payment_method"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=("gray50", "gray60"),
                width=110
            )
            method_lbl.pack(side="left", padx=10)

        # Amount
        is_income = tx["type"] == "income"
        prefix = "+" if is_income else "-"
        amt_color = "#10B981" if is_income else "#F43F5E"
        amt_lbl = ctk.CTkLabel(
            row,
            text=f"{prefix}{self.currency}{tx['amount']:,.2f}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=amt_color,
            width=110,
            anchor="e"
        )
        amt_lbl.pack(side="right", padx=(10, 16))

    # =========================================================================
    # VIEW 2: TRANSACTIONS (CRUD & Table)
    # =========================================================================
    def _render_transactions(self):
        # Header
        top_bar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 15))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text="Transaction History",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        )
        title_lbl.pack(side="left")

        actions_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        actions_frame.pack(side="right")

        export_btn = ctk.CTkButton(
            actions_frame,
            text="📥 Export CSV",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=("gray80", "#2E3440"),
            hover_color=("gray70", "#3E4451"),
            text_color=("gray10", "gray90"),
            height=34,
            command=self._export_csv_action
        )
        export_btn.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            actions_frame,
            text="+ Add New",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=34,
            command=lambda: self.show_view("add")
        )
        add_btn.pack(side="left")

        # Filter and Search Row
        filters_frame = ctk.CTkFrame(self.main_content, fg_color=("white", "#1F242E"), corner_radius=10)
        filters_frame.pack(fill="x", pady=(0, 15), ipady=6)

        # Search box
        self.search_entry = ctk.CTkEntry(
            filters_frame,
            placeholder_text="🔍 Search title or notes...",
            width=260,
            height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12)
        )
        self.search_entry.pack(side="left", padx=(12, 10), pady=6)
        self.search_entry.bind("<KeyRelease>", lambda event: self._filter_transactions())

        # Type filter
        type_lbl = ctk.CTkLabel(filters_frame, text="Type:", font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        type_lbl.pack(side="left", padx=(8, 4))

        self.type_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["All", "Expense", "Income"],
            width=110,
            height=34,
            command=lambda _: self._filter_transactions()
        )
        self.type_filter.pack(side="left", padx=(0, 10))

        # Category filter
        cat_lbl = ctk.CTkLabel(filters_frame, text="Category:", font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        cat_lbl.pack(side="left", padx=(8, 4))

        categories = ["All"] + [c[0] for c in DatabaseManager.DEFAULT_CATEGORIES]
        self.cat_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=categories,
            width=170,
            height=34,
            command=lambda _: self._filter_transactions()
        )
        self.cat_filter.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            filters_frame,
            text="Reset Filters",
            width=90,
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color=("gray70", "gray50"),
            text_color=("gray20", "gray80"),
            command=self._reset_filters
        )
        clear_btn.pack(side="left", padx=6)

        # Table Header
        tbl_header = ctk.CTkFrame(self.main_content, fg_color=("gray90", "#1C2029"), corner_radius=6, height=36)
        tbl_header.pack(fill="x", pady=(0, 6))
        tbl_header.pack_propagate(False)

        ctk.CTkLabel(tbl_header, text="DATE", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                     text_color=("gray50", "gray60"), width=95, anchor="w").pack(side="left", padx=(16, 5))
        ctk.CTkLabel(tbl_header, text="DESCRIPTION", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                     text_color=("gray50", "gray60"), anchor="w").pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(tbl_header, text="CATEGORY", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                     text_color=("gray50", "gray60"), width=150, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(tbl_header, text="METHOD", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                     text_color=("gray50", "gray60"), width=120, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(tbl_header, text="AMOUNT", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                     text_color=("gray50", "gray60"), width=110, anchor="e").pack(side="left", padx=5)
        ctk.CTkLabel(tbl_header, text="ACTIONS", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                     text_color=("gray50", "gray60"), width=90, anchor="center").pack(side="right", padx=(5, 16))

        # Scrollable Transactions List
        self.tx_table_frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        self.tx_table_frame.pack(fill="both", expand=True)

        self._filter_transactions()

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.type_filter.set("All")
        self.cat_filter.set("All")
        self._filter_transactions()

    def _filter_transactions(self):
        for widget in self.tx_table_frame.winfo_children():
            widget.destroy()

        search_text = self.search_entry.get().strip()
        type_val = self.type_filter.get()
        cat_val = self.cat_filter.get()

        txs = self.db.get_transactions(
            search=search_text,
            category=cat_val,
            trans_type=type_val,
            limit=250
        )

        if not txs:
            empty_box = ctk.CTkLabel(
                self.tx_table_frame,
                text="No transactions match your current search and filter criteria.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                text_color=("gray50", "gray60")
            )
            empty_box.pack(pady=40)
            return

        for tx in txs:
            row = ctk.CTkFrame(self.tx_table_frame, fg_color=("white", "#232834"), corner_radius=6, height=44)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)

            # Date
            ctk.CTkLabel(row, text=tx["date"], font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                         text_color=("gray40", "gray60"), width=95, anchor="w").pack(side="left", padx=(16, 5))

            # Title
            title_text = tx["title"]
            if tx.get("notes"):
                title_text += f" ({tx['notes']})"
            ctk.CTkLabel(row, text=title_text, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                         anchor="w").pack(side="left", fill="x", expand=True, padx=5)

            # Category
            cat_badge = ctk.CTkLabel(
                row,
                text=f" {tx['category']} ",
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                fg_color=("gray90", "#2E3748"),
                corner_radius=4,
                width=150,
                anchor="w"
            )
            cat_badge.pack(side="left", padx=5)

            # Method
            ctk.CTkLabel(row, text=tx["payment_method"], font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                         text_color=("gray40", "gray60"), width=120, anchor="w").pack(side="left", padx=5)

            # Amount
            is_income = tx["type"] == "income"
            prefix = "+" if is_income else "-"
            amt_color = "#10B981" if is_income else "#F43F5E"
            ctk.CTkLabel(row, text=f"{prefix}{self.currency}{tx['amount']:,.2f}",
                         font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                         text_color=amt_color, width=110, anchor="e").pack(side="left", padx=5)

            # Actions (Edit / Delete)
            actions_box = ctk.CTkFrame(row, fg_color="transparent", width=90)
            actions_box.pack(side="right", padx=(5, 14))

            del_btn = ctk.CTkButton(
                actions_box,
                text="🗑️",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("#FEE2E2", "#7F1D1D"),
                text_color="#EF4444",
                command=lambda tid=tx["id"]: self._delete_transaction_action(tid)
            )
            del_btn.pack(side="right", padx=2)

            edit_btn = ctk.CTkButton(
                actions_box,
                text="✏️",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("gray85", "#323B4B"),
                command=lambda t=tx: self._open_edit_modal(t)
            )
            edit_btn.pack(side="right", padx=2)

    def _delete_transaction_action(self, trans_id: int):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction record?"):
            self.db.delete_transaction(trans_id)
            self._filter_transactions()

    def _open_edit_modal(self, tx: dict):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Edit Transaction #{tx['id']}")
        modal.geometry("480x560")
        modal.transient(self)
        modal.grab_set()

        form_frame = ctk.CTkFrame(modal, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(form_frame, text=f"Update Record #{tx['id']}", font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")).pack(anchor="w", pady=(0, 15))

        # Title
        ctk.CTkLabel(form_frame, text="Description / Payee", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w")
        title_entry = ctk.CTkEntry(form_frame, height=36)
        title_entry.insert(0, tx["title"])
        title_entry.pack(fill="x", pady=(4, 12))

        # Amount & Type
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 12))
        row2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row2, text="Amount", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(row2, text="Type", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(row=0, column=1, sticky="w", padx=(10, 0))

        amt_entry = ctk.CTkEntry(row2, height=36)
        amt_entry.insert(0, str(tx["amount"]))
        amt_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        type_seg = ctk.CTkSegmentedButton(row2, values=["Expense", "Income"], height=36)
        type_seg.set(tx["type"].capitalize())
        type_seg.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 0))

        # Category
        ctk.CTkLabel(form_frame, text="Category", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w")
        cat_menu = ctk.CTkOptionMenu(form_frame, values=[c[0] for c in DatabaseManager.DEFAULT_CATEGORIES], height=36)
        cat_menu.set(tx["category"])
        cat_menu.pack(fill="x", pady=(4, 12))

        # Method
        ctk.CTkLabel(form_frame, text="Payment Method", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w")
        method_menu = ctk.CTkOptionMenu(form_frame, values=DatabaseManager.PAYMENT_METHODS, height=36)
        method_menu.set(tx["payment_method"])
        method_menu.pack(fill="x", pady=(4, 12))

        # Date
        ctk.CTkLabel(form_frame, text="Date (YYYY-MM-DD)", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w")
        date_entry = ctk.CTkEntry(form_frame, height=36)
        date_entry.insert(0, tx["date"])
        date_entry.pack(fill="x", pady=(4, 12))

        # Notes
        ctk.CTkLabel(form_frame, text="Notes (Optional)", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w")
        notes_entry = ctk.CTkEntry(form_frame, height=36)
        notes_entry.insert(0, tx.get("notes", ""))
        notes_entry.pack(fill="x", pady=(4, 20))

        def save_changes():
            title = title_entry.get().strip()
            amount_str = amt_entry.get().strip()
            date_val = date_entry.get().strip()

            if not title:
                messagebox.showerror("Validation Error", "Title cannot be empty.", parent=modal)
                return

            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid positive numeric amount.", parent=modal)
                return

            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.", parent=modal)
                return

            self.db.update_transaction(
                trans_id=tx["id"],
                title=title,
                amount=amount,
                trans_type=type_seg.get().lower(),
                category=cat_menu.get(),
                payment_method=method_menu.get(),
                date=date_val,
                notes=notes_entry.get().strip()
            )
            modal.destroy()
            self._filter_transactions()

        save_btn = ctk.CTkButton(
            form_frame,
            text="Save Changes",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=38,
            command=save_changes
        )
        save_btn.pack(fill="x")

    # =========================================================================
    # VIEW 3: ADD TRANSACTION
    # =========================================================================
    def _render_add_transaction(self):
        container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True)

        card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=14, width=640)
        card.pack(padx=20, pady=10, ipady=15)

        title_lbl = ctk.CTkLabel(
            card,
            text="Add New Transaction",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold")
        )
        title_lbl.pack(anchor="w", padx=30, pady=(20, 4))

        subtitle_lbl = ctk.CTkLabel(
            card,
            text="Record an incoming revenue or outgoing expenditure with precision.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=("gray50", "gray60")
        )
        subtitle_lbl.pack(anchor="w", padx=30, pady=(0, 20))

        # Form Container
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=30)

        # Type Toggle (Expense vs Income)
        ctk.CTkLabel(form, text="Transaction Type", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).pack(anchor="w", pady=(0, 6))
        self.add_type_seg = ctk.CTkSegmentedButton(
            form,
            values=["Expense", "Income"],
            height=38,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            selected_color="#F43F5E",
            command=self._on_add_type_change
        )
        self.add_type_seg.set("Expense")
        self.add_type_seg.pack(fill="x", pady=(0, 16))

        # Description / Payee
        ctk.CTkLabel(form, text="Description / Title", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).pack(anchor="w", pady=(0, 6))
        self.add_title_entry = ctk.CTkEntry(
            form,
            placeholder_text="e.g., Grocery Shopping, Monthly Salary, Coffee with Client",
            height=40,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13)
        )
        self.add_title_entry.pack(fill="x", pady=(0, 16))

        # Two-column row: Amount & Date
        grid_row = ctk.CTkFrame(form, fg_color="transparent")
        grid_row.pack(fill="x", pady=(0, 16))
        grid_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid_row, text=f"Amount ({self.currency})", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(grid_row, text="Date (YYYY-MM-DD)", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).grid(row=0, column=1, sticky="w", padx=(15, 0), pady=(0, 6))

        self.add_amount_entry = ctk.CTkEntry(
            grid_row,
            placeholder_text="0.00",
            height=40,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        )
        self.add_amount_entry.grid(row=1, column=0, sticky="ew")

        self.add_date_entry = ctk.CTkEntry(
            grid_row,
            height=40,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13)
        )
        self.add_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.add_date_entry.grid(row=1, column=1, sticky="ew", padx=(15, 0))

        # Category & Payment Method
        grid_row2 = ctk.CTkFrame(form, fg_color="transparent")
        grid_row2.pack(fill="x", pady=(0, 16))
        grid_row2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(grid_row2, text="Category", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(grid_row2, text="Payment Method", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).grid(row=0, column=1, sticky="w", padx=(15, 0), pady=(0, 6))

        self.add_cat_menu = ctk.CTkOptionMenu(
            grid_row2,
            values=[c[0] for c in DatabaseManager.DEFAULT_CATEGORIES if c[1] == "expense"],
            height=40,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13)
        )
        self.add_cat_menu.grid(row=1, column=0, sticky="ew")

        self.add_method_menu = ctk.CTkOptionMenu(
            grid_row2,
            values=DatabaseManager.PAYMENT_METHODS,
            height=40,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13)
        )
        self.add_method_menu.grid(row=1, column=1, sticky="ew", padx=(15, 0))

        # Notes
        ctk.CTkLabel(form, text="Notes / Tags (Optional)", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).pack(anchor="w", pady=(0, 6))
        self.add_notes_entry = ctk.CTkEntry(
            form,
            placeholder_text="Add optional remarks, receipt reference or invoice number...",
            height=40,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13)
        )
        self.add_notes_entry.pack(fill="x", pady=(0, 24))

        # Submit Buttons
        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 10))

        submit_btn = ctk.CTkButton(
            btn_row,
            text="✓ Save Transaction",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=44,
            command=self._submit_add_transaction
        )
        submit_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        reset_btn = ctk.CTkButton(
            btn_row,
            text="Clear Form",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=("gray85", "#2E3748"),
            hover_color=("gray75", "#3A455A"),
            text_color=("gray10", "gray90"),
            height=44,
            width=110,
            command=self._reset_add_form
        )
        reset_btn.pack(side="right")

    def _on_add_type_change(self, value: str):
        is_income = value.lower() == "income"
        if is_income:
            self.add_type_seg.configure(selected_color="#10B981")
            cats = [c[0] for c in DatabaseManager.DEFAULT_CATEGORIES if c[1] == "income"]
        else:
            self.add_type_seg.configure(selected_color="#F43F5E")
            cats = [c[0] for c in DatabaseManager.DEFAULT_CATEGORIES if c[1] == "expense"]

        self.add_cat_menu.configure(values=cats)
        if cats:
            self.add_cat_menu.set(cats[0])

    def _reset_add_form(self):
        self.add_title_entry.delete(0, "end")
        self.add_amount_entry.delete(0, "end")
        self.add_notes_entry.delete(0, "end")
        self.add_date_entry.delete(0, "end")
        self.add_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def _submit_add_transaction(self):
        title = self.add_title_entry.get().strip()
        amount_str = self.add_amount_entry.get().strip()
        trans_type = self.add_type_seg.get().lower()
        category = self.add_cat_menu.get()
        method = self.add_method_menu.get()
        date_val = self.add_date_entry.get().strip()
        notes = self.add_notes_entry.get().strip()

        if not title:
            messagebox.showerror("Missing Information", "Please enter a transaction title or description.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive number for the amount.")
            return

        try:
            datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be valid and formatted as YYYY-MM-DD.")
            return

        self.db.add_transaction(
            title=title,
            amount=amount,
            trans_type=trans_type,
            category=category,
            payment_method=method,
            date=date_val,
            notes=notes
        )

        messagebox.showinfo("Success", f"Recorded {trans_type.capitalize()}: {self.currency}{amount:,.2f} for '{title}'")
        self._reset_add_form()
        self.show_view("dashboard")

    # =========================================================================
    # VIEW 4: BUDGETS & LIMITS
    # =========================================================================
    def _render_budgets(self):
        container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True)

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Monthly Budget Planner & Tracking",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        )
        title_lbl.pack(side="left")

        add_budget_btn = ctk.CTkButton(
            header_frame,
            text="+ Set Category Budget",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=34,
            command=self._open_budget_modal
        )
        add_budget_btn.pack(side="right")

        budgets = self.db.get_budgets()

        # Overall summary card
        total_budget = sum(b["limit"] for b in budgets)
        total_spent = sum(b["spent"] for b in budgets)
        overall_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0

        summary_card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
        summary_card.pack(fill="x", pady=(0, 20), ipady=10)

        s_top = ctk.CTkFrame(summary_card, fg_color="transparent")
        s_top.pack(fill="x", padx=20, pady=(10, 8))

        ctk.CTkLabel(s_top, text="Current Month Overall Budget Health", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")).pack(side="left")
        ctk.CTkLabel(s_top, text=f"Total: {self.currency}{total_spent:,.2f} / {self.currency}{total_budget:,.2f} ({overall_pct:.1f}%)",
                     font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                     text_color="#F43F5E" if overall_pct > 100 else "#10B981").pack(side="right")

        # Global Progress Bar
        bar_color = "#EF4444" if overall_pct > 100 else ("#F59E0B" if overall_pct > 80 else "#10B981")
        overall_bar = ctk.CTkProgressBar(summary_card, height=12, corner_radius=6, progress_color=bar_color)
        overall_bar.set(min(1.0, overall_pct / 100))
        overall_bar.pack(fill="x", padx=20, pady=(0, 10))

        # Individual Category Budget Cards
        if not budgets:
            empty_lbl = ctk.CTkLabel(
                container,
                text="No category budgets configured yet. Click '+ Set Category Budget' above to establish limits.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=13),
                text_color=("gray50", "gray60")
            )
            empty_lbl.pack(pady=40)
            return

        # Grid of category budget cards (2 columns)
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        for i, b in enumerate(budgets):
            col = i % 2
            row = i // 2

            b_card = ctk.CTkFrame(grid_frame, fg_color=("white", "#1F242E"), corner_radius=12)
            b_card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            top_row = ctk.CTkFrame(b_card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(14, 6))

            ctk.CTkLabel(top_row, text=b["category"], font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")).pack(side="left")

            pct = b["percentage"]
            badge_color = "#EF4444" if pct > 100 else ("#F59E0B" if pct > 80 else "#10B981")
            status_text = "OVER BUDGET" if pct > 100 else f"{pct:.0f}%"
            badge = ctk.CTkLabel(
                top_row,
                text=f" {status_text} ",
                font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
                text_color="white",
                fg_color=badge_color,
                corner_radius=4
            )
            badge.pack(side="right")

            # Spent vs Limit details
            details_row = ctk.CTkFrame(b_card, fg_color="transparent")
            details_row.pack(fill="x", padx=16, pady=(0, 8))

            spent_lbl = ctk.CTkLabel(
                details_row,
                text=f"Spent: {self.currency}{b['spent']:,.2f}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                text_color=badge_color
            )
            spent_lbl.pack(side="left")

            limit_lbl = ctk.CTkLabel(
                details_row,
                text=f"Limit: {self.currency}{b['limit']:,.2f}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=("gray50", "gray60")
            )
            limit_lbl.pack(side="right")

            # Progress Bar
            pbar = ctk.CTkProgressBar(b_card, height=8, corner_radius=4, progress_color=badge_color)
            pbar.set(min(1.0, pct / 100))
            pbar.pack(fill="x", padx=16, pady=(0, 12))

            # Bottom controls: Edit / Delete
            bottom_ctrl = ctk.CTkFrame(b_card, fg_color="transparent")
            bottom_ctrl.pack(fill="x", padx=16, pady=(0, 12))

            remaining_lbl = ctk.CTkLabel(
                bottom_ctrl,
                text=f"Remaining: {self.currency}{b['remaining']:,.2f}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=("gray50", "gray60")
            )
            remaining_lbl.pack(side="left")

            edit_btn = ctk.CTkButton(
                bottom_ctrl,
                text="Edit Limit",
                width=75,
                height=26,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color=("gray90", "#2E3748"),
                text_color=("gray10", "gray90"),
                command=lambda cat=b["category"], lim=b["limit"]: self._open_budget_modal(cat, lim)
            )
            edit_btn.pack(side="right")

    def _open_budget_modal(self, category: str = "", current_limit: float = 0.0):
        modal = ctk.CTkToplevel(self)
        modal.title("Configure Category Budget")
        modal.geometry("400x320")
        modal.transient(self)
        modal.grab_set()

        form = ctk.CTkFrame(modal, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=25)

        title_text = "Edit Category Budget" if category else "Set New Budget"
        ctk.CTkLabel(form, text=title_text, font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(form, text="Expense Category", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w", pady=(0, 4))
        expense_cats = [c[0] for c in DatabaseManager.DEFAULT_CATEGORIES if c[1] == "expense"]
        cat_opt = ctk.CTkOptionMenu(form, values=expense_cats, height=36)
        if category:
            cat_opt.set(category)
        cat_opt.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(form, text=f"Monthly Spending Limit ({self.currency})", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w", pady=(0, 4))
        limit_entry = ctk.CTkEntry(form, height=36)
        if current_limit > 0:
            limit_entry.insert(0, str(current_limit))
        limit_entry.pack(fill="x", pady=(0, 20))

        def save_budget():
            try:
                val = float(limit_entry.get().strip())
                if val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number for the monthly limit.", parent=modal)
                return

            self.db.set_budget(cat_opt.get(), val)
            modal.destroy()
            self._render_budgets()

        save_btn = ctk.CTkButton(
            form,
            text="Save Budget Limit",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=38,
            command=save_budget
        )
        save_btn.pack(fill="x")

    # =========================================================================
    # VIEW 5: ANALYTICS & INSIGHTS
    # =========================================================================
    def _render_analytics(self):
        container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True)

        title_lbl = ctk.CTkLabel(
            container,
            text="Financial Intelligence & Analytics",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        )
        title_lbl.pack(anchor="w", pady=(0, 20))

        # Top section: Top Spending Categories Ranking Chart
        chart_theme = "light" if self.current_theme == "light" else "dark"
        chart_card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
        chart_card.pack(fill="x", pady=(0, 20))

        c_title = ctk.CTkLabel(
            chart_card,
            text="Top Spending Categories (All-Time Outflows)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        )
        c_title.pack(anchor="w", padx=16, pady=(14, 8))

        cat_data = self.db.get_category_breakdown(trans_type="expense")
        cat_chart = create_category_bar_chart(chart_card, cat_data, currency=self.currency, theme=chart_theme)
        cat_chart.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Analytics Statistics Cards
        stats_frame = ctk.CTkFrame(container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        txs = self.db.get_transactions(limit=1000)
        expense_txs = [t for t in txs if t["type"] == "expense"]
        total_exp = sum(t["amount"] for t in expense_txs)
        avg_exp = (total_exp / len(expense_txs)) if expense_txs else 0.0
        max_exp = max((t["amount"] for t in expense_txs), default=0.0)

        # Total transactions
        stat_cards = [
            ("Average Expense Ticket", f"{self.currency}{avg_exp:,.2f}", "#3B82F6"),
            ("Highest Single Expense", f"{self.currency}{max_exp:,.2f}", "#F43F5E"),
            ("Total Transactions Logged", f"{len(txs):,}", "#10B981")
        ]

        for idx, (label, val, clr) in enumerate(stat_cards):
            c = ctk.CTkFrame(stats_frame, fg_color=("white", "#1F242E"), corner_radius=12)
            c.grid(row=0, column=idx, padx=8, pady=0, sticky="nsew")

            ctk.CTkLabel(c, text=label, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                         text_color=("gray50", "gray60")).pack(anchor="w", padx=16, pady=(14, 4))
            ctk.CTkLabel(c, text=val, font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
                         text_color=clr).pack(anchor="w", padx=16, pady=(0, 14))

    # =========================================================================
    # VIEW 6: SETTINGS & DATA
    # =========================================================================
    def _render_settings(self):
        container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True)

        title_lbl = ctk.CTkLabel(
            container,
            text="Settings & Data Management",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        )
        title_lbl.pack(anchor="w", pady=(0, 20))

        # Currency Preferences Card
        curr_card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
        curr_card.pack(fill="x", pady=(0, 20), ipady=10)

        ctk.CTkLabel(curr_card, text="Currency Configuration", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")).pack(anchor="w", padx=20, pady=(12, 4))
        ctk.CTkLabel(curr_card, text="Choose your primary currency symbol displayed across all views and reports.",
                     font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=("gray50", "gray60")).pack(anchor="w", padx=20, pady=(0, 12))

        curr_row = ctk.CTkFrame(curr_card, fg_color="transparent")
        curr_row.pack(fill="x", padx=20)

        currencies = ["$", "€", "£", "₹", "¥", "₩", "A$", "C$", "Fr.", "AED"]
        self.curr_menu = ctk.CTkOptionMenu(
            curr_row,
            values=currencies,
            width=140,
            height=36,
            command=self._on_currency_change
        )
        self.curr_menu.set(self.currency)
        self.curr_menu.pack(side="left")

        # Data Backup & Export / Import Card
        data_card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
        data_card.pack(fill="x", pady=(0, 20), ipady=10)

        ctk.CTkLabel(data_card, text="Data Portability & Backup", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")).pack(anchor="w", padx=20, pady=(12, 4))
        ctk.CTkLabel(data_card, text="Export your financial ledger to CSV for Excel/Google Sheets, or import existing records.",
                     font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=("gray50", "gray60")).pack(anchor="w", padx=20, pady=(0, 15))

        btn_box = ctk.CTkFrame(data_card, fg_color="transparent")
        btn_box.pack(fill="x", padx=20)

        export_btn = ctk.CTkButton(
            btn_box,
            text="📥 Export to CSV...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=36,
            command=self._export_csv_action
        )
        export_btn.pack(side="left", padx=(0, 12))

        import_btn = ctk.CTkButton(
            btn_box,
            text="📤 Import from CSV...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=("gray85", "#2E3748"),
            hover_color=("gray75", "#3A455A"),
            text_color=("gray10", "gray90"),
            height=36,
            command=self._import_csv_action
        )
        import_btn.pack(side="left")

        # Database Management Card
        db_card = ctk.CTkFrame(container, fg_color=("white", "#1F242E"), corner_radius=12)
        db_card.pack(fill="x", pady=(0, 20), ipady=10)

        ctk.CTkLabel(db_card, text="Database Maintenance & Demo Data", font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")).pack(anchor="w", padx=20, pady=(12, 4))
        ctk.CTkLabel(db_card, text="Generate synthetic high-fidelity sample transactions or reset ledger data.",
                     font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=("gray50", "gray60")).pack(anchor="w", padx=20, pady=(0, 15))

        db_btn_box = ctk.CTkFrame(db_card, fg_color="transparent")
        db_btn_box.pack(fill="x", padx=20)

        demo_btn = ctk.CTkButton(
            db_btn_box,
            text="⚡ Load Sample Demo Data (3 Months)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            command=self._load_demo_data_prompt
        )
        demo_btn.pack(side="left", padx=(0, 12))

        clear_btn = ctk.CTkButton(
            db_btn_box,
            text="⚠️ Wipe All Transactions",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            height=36,
            command=self._clear_all_prompt
        )
        clear_btn.pack(side="left")

    def _on_currency_change(self, value: str):
        self.currency = value
        self.db.set_setting("currency", value)
        messagebox.showinfo("Currency Updated", f"Active currency symbol changed to '{value}'.")
        self.show_view("dashboard")

    def _export_csv_action(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")],
            initialfile=f"expense_tracker_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if file_path:
            count = self.db.export_to_csv(file_path)
            messagebox.showinfo("Export Complete", f"Successfully exported {count} transactions to:\n{file_path}")

    def _import_csv_action(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if file_path:
            count = self.db.import_from_csv(file_path)
            messagebox.showinfo("Import Complete", f"Successfully imported {count} transactions from:\n{file_path}")
            self.show_view("dashboard")

    def _load_demo_data_prompt(self):
        if messagebox.askyesno("Load Demo Data", "This will generate realistic income and expense transactions for the past 90 days. Would you like to proceed?"):
            self.db.populate_demo_data()
            messagebox.showinfo("Demo Data Loaded", "Sample financial data loaded successfully!")
            self.show_view("dashboard")

    def _clear_all_prompt(self):
        if messagebox.askyesno("Confirm Wipe", "Are you sure you want to delete ALL transaction records? This action cannot be undone."):
            self.db.clear_all_transactions()
            messagebox.showinfo("Database Cleared", "All transaction history has been deleted.")
            self.show_view("dashboard")


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
