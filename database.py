"""
Database layer for the Professional Expense Tracker.
Uses SQLite for robust, zero-configuration local persistence.
"""

import sqlite3
import csv
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional, Tuple


class DatabaseManager:
    DEFAULT_CATEGORIES = [
        ("Food & Dining", "expense"),
        ("Groceries", "expense"),
        ("Shopping", "expense"),
        ("Housing & Rent", "expense"),
        ("Utilities & Bills", "expense"),
        ("Transportation", "expense"),
        ("Healthcare & Fitness", "expense"),
        ("Entertainment", "expense"),
        ("Education", "expense"),
        ("Travel", "expense"),
        ("Salary", "income"),
        ("Freelance & Side Gig", "income"),
        ("Investments & Dividends", "income"),
        ("Other Income", "income"),
        ("Miscellaneous", "expense")
    ]

    PAYMENT_METHODS = ["Credit Card", "Debit Card", "Bank Transfer", "Cash", "Digital Wallet", "Crypto"]

    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
                    category TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    date TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    category TEXT PRIMARY KEY,
                    monthly_limit REAL NOT NULL
                )
            """)

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Default settings if not exist
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', '$')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'dark')")

            # Check if transactions table is empty; if so, populate default budgets
            cursor.execute("SELECT COUNT(*) FROM budgets")
            if cursor.fetchone()[0] == 0:
                default_budgets = [
                    ("Food & Dining", 400.0),
                    ("Groceries", 500.0),
                    ("Shopping", 250.0),
                    ("Housing & Rent", 1200.0),
                    ("Utilities & Bills", 200.0),
                    ("Transportation", 200.0),
                    ("Entertainment", 150.0),
                    ("Healthcare & Fitness", 150.0),
                ]
                cursor.executemany("INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)", default_budgets)

            conn.commit()

    # --- Transaction CRUD ---

    def add_transaction(self, title: str, amount: float, trans_type: str, category: str,
                        payment_method: str, date: str, notes: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (title, amount, type, category, payment_method, date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title.strip(), round(float(amount), 2), trans_type.lower(), category, payment_method, date, notes.strip()))
            conn.commit()
            return cursor.lastrowid

    def update_transaction(self, trans_id: int, title: str, amount: float, trans_type: str,
                           category: str, payment_method: str, date: str, notes: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions
                SET title = ?, amount = ?, type = ?, category = ?, payment_method = ?, date = ?, notes = ?
                WHERE id = ?
            """, (title.strip(), round(float(amount), 2), trans_type.lower(), category, payment_method, date, notes.strip(), trans_id))
            conn.commit()

    def delete_transaction(self, trans_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
            conn.commit()

    def get_transaction(self, trans_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_transactions(self, search: str = "", category: str = "All",
                         trans_type: str = "All", start_date: Optional[str] = None,
                         end_date: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
        query = "SELECT * FROM transactions WHERE 1=1"
        params: List[Any] = []

        if search:
            query += " AND (title LIKE ? OR notes LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if trans_type and trans_type != "All":
            query += " AND type = ?"
            params.append(trans_type.lower())

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # --- Summary Metrics & Analytics ---

    def get_summary_metrics(self) -> Dict[str, float]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE type = 'income'")
            total_income = cursor.fetchone()[0]

            cursor.execute("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE type = 'expense'")
            total_expense = cursor.fetchone()[0]

            # Current month stats
            current_month = datetime.now().strftime("%Y-%m")
            cursor.execute("""
                SELECT IFNULL(SUM(amount), 0) FROM transactions 
                WHERE type = 'income' AND date LIKE ?
            """, (f"{current_month}%",))
            monthly_income = cursor.fetchone()[0]

            cursor.execute("""
                SELECT IFNULL(SUM(amount), 0) FROM transactions 
                WHERE type = 'expense' AND date LIKE ?
            """, (f"{current_month}%",))
            monthly_expense = cursor.fetchone()[0]

            total_balance = total_income - total_expense
            savings_rate = ((monthly_income - monthly_expense) / monthly_income * 100) if monthly_income > 0 else 0.0

            return {
                "total_balance": total_balance,
                "total_income": total_income,
                "total_expense": total_expense,
                "monthly_income": monthly_income,
                "monthly_expense": monthly_expense,
                "savings_rate": max(-100.0, min(100.0, savings_rate))
            }

    def get_category_breakdown(self, trans_type: str = "expense", month: Optional[str] = None) -> List[Tuple[str, float]]:
        query = """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = ?
        """
        params = [trans_type.lower()]

        if month:
            query += " AND date LIKE ?"
            params.append(f"{month}%")

        query += " GROUP BY category ORDER BY total DESC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [(row["category"], float(row["total"])) for row in cursor.fetchall()]

    def get_monthly_trend(self, months_back: int = 6) -> List[Dict[str, Any]]:
        """Returns monthly income & expense totals for the last N months."""
        today = datetime.now()
        results = []
        for i in range(months_back - 1, -1, -1):
            target_date = today - timedelta(days=i * 30)
            month_str = target_date.strftime("%Y-%m")
            month_label = target_date.strftime("%b %y")

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT IFNULL(SUM(amount), 0) FROM transactions
                    WHERE type = 'income' AND date LIKE ?
                """, (f"{month_str}%",))
                inc = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT IFNULL(SUM(amount), 0) FROM transactions
                    WHERE type = 'expense' AND date LIKE ?
                """, (f"{month_str}%",))
                exp = cursor.fetchone()[0]

                results.append({
                    "month": month_str,
                    "label": month_label,
                    "income": float(inc),
                    "expense": float(exp),
                    "net": float(inc - exp)
                })

        return results

    # --- Budgets ---

    def get_budgets(self) -> List[Dict[str, Any]]:
        current_month = datetime.now().strftime("%Y-%m")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.category, b.monthly_limit,
                       IFNULL(SUM(t.amount), 0) as spent
                FROM budgets b
                LEFT JOIN transactions t ON b.category = t.category 
                    AND t.type = 'expense' 
                    AND t.date LIKE ?
                GROUP BY b.category, b.monthly_limit
                ORDER BY b.monthly_limit DESC
            """, (f"{current_month}%",))
            
            rows = []
            for row in cursor.fetchall():
                limit = float(row["monthly_limit"])
                spent = float(row["spent"])
                percentage = (spent / limit * 100) if limit > 0 else 0
                rows.append({
                    "category": row["category"],
                    "limit": limit,
                    "spent": spent,
                    "remaining": max(0.0, limit - spent),
                    "percentage": percentage
                })
            return rows

    def set_budget(self, category: str, limit: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO budgets (category, monthly_limit)
                VALUES (?, ?)
                ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
            """, (category, round(float(limit), 2)))
            conn.commit()

    def delete_budget(self, category: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets WHERE category = ?", (category,))
            conn.commit()

    # --- Settings ---

    def get_setting(self, key: str, default: str = "") -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            conn.commit()

    # --- Import / Export ---

    def export_to_csv(self, file_path: str) -> int:
        transactions = self.get_transactions(limit=10000)
        if not transactions:
            return 0

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "title", "amount", "type", "category", "payment_method", "notes"])
            writer.writeheader()
            for tx in transactions:
                writer.writerow({
                    "id": tx["id"],
                    "date": tx["date"],
                    "title": tx["title"],
                    "amount": tx["amount"],
                    "type": tx["type"],
                    "category": tx["category"],
                    "payment_method": tx["payment_method"],
                    "notes": tx.get("notes", "")
                })
        return len(transactions)

    def import_from_csv(self, file_path: str) -> int:
        count = 0
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    title = row.get("title", "").strip()
                    amount = float(row.get("amount", 0))
                    trans_type = row.get("type", "expense").strip().lower()
                    category = row.get("category", "Miscellaneous").strip()
                    payment_method = row.get("payment_method", "Cash").strip()
                    date = row.get("date", datetime.now().strftime("%Y-%m-%d")).strip()
                    notes = row.get("notes", "").strip()

                    if title and amount > 0:
                        self.add_transaction(title, amount, trans_type, category, payment_method, date, notes)
                        count += 1
                except Exception:
                    continue
        return count

    # --- Demo Data Generator ---

    def populate_demo_data(self):
        """Generates realistic demo transactions for the last 90 days for instant dashboard presentation."""
        now = datetime.now()
        
        sample_transactions = [
            # Incomes
            ("Monthly Salary", 4500.0, "income", "Salary", "Bank Transfer"),
            ("Freelance UI Design", 950.0, "income", "Freelance & Side Gig", "Bank Transfer"),
            ("Stock Dividends", 140.0, "income", "Investments & Dividends", "Bank Transfer"),
            ("Bonus Payout", 600.0, "income", "Salary", "Bank Transfer"),
            # Recurring Expenses
            ("Apartment Rent", 1200.0, "expense", "Housing & Rent", "Bank Transfer"),
            ("High-speed Fiber Internet", 65.0, "expense", "Utilities & Bills", "Credit Card"),
            ("Electricity & Water", 110.0, "expense", "Utilities & Bills", "Credit Card"),
            ("Gym Membership", 55.0, "expense", "Healthcare & Fitness", "Credit Card"),
            ("Health Insurance", 180.0, "expense", "Healthcare & Fitness", "Bank Transfer"),
            # Variable Expenses
            ("Whole Foods Groceries", 145.20, "expense", "Groceries", "Credit Card"),
            ("Trader Joe's Run", 88.50, "expense", "Groceries", "Debit Card"),
            ("Dinner with Colleagues", 74.00, "expense", "Food & Dining", "Credit Card"),
            ("Artisan Espresso & Bakery", 12.50, "expense", "Food & Dining", "Digital Wallet"),
            ("Uber Ride to Downtown", 24.30, "expense", "Transportation", "Digital Wallet"),
            ("Metro Pass Recharge", 45.00, "expense", "Transportation", "Debit Card"),
            ("Gasoline Refill", 58.00, "expense", "Transportation", "Credit Card"),
            ("Amazon Gadgets Order", 119.99, "expense", "Shopping", "Credit Card"),
            ("New Running Shoes", 130.00, "expense", "Shopping", "Credit Card"),
            ("Netflix & Spotify Subscription", 27.98, "expense", "Entertainment", "Credit Card"),
            ("Movie Night IMAX", 38.50, "expense", "Entertainment", "Credit Card"),
            ("Weekend Getaway Hotel", 280.00, "expense", "Travel", "Credit Card"),
            ("Flight Tickets", 320.00, "expense", "Travel", "Credit Card"),
            ("Python Machine Learning Book", 42.00, "expense", "Education", "Debit Card"),
        ]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Spread across 3 months
            for month_offset in [0, 1, 2]:
                for item in sample_transactions:
                    # Random day in that month
                    day = random.randint(1, 27)
                    dt = (now - timedelta(days=month_offset * 30 + (28 - day)))
                    date_str = dt.strftime("%Y-%m-%d")
                    # add small jitter to amounts
                    amount = item[1]
                    if item[2] == "expense" and item[3] not in ["Housing & Rent", "Utilities & Bills"]:
                        amount = round(amount * random.uniform(0.85, 1.25), 2)

                    cursor.execute("""
                        INSERT INTO transactions (title, amount, type, category, payment_method, date, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (item[0], amount, item[2], item[3], item[4], date_str, "Sample demo transaction"))
            conn.commit()

    def clear_all_transactions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
            conn.commit()
