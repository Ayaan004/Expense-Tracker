# 💎 VaultFlow • Professional Expense Tracker

A modern, high-performance financial intelligence and expense management desktop GUI built with **Python**, **CustomTkinter**, **Matplotlib**, and **SQLite**.

---

## ✨ Features

- **Executive Financial Dashboard**:
  - Real-time KPI metric cards: **Net Balance**, **Monthly Inflow**, **Monthly Outflow**, and **Savings Rate %**.
  - Dynamic **6-Month Income vs. Expense Trend Chart** (grouped bars).
  - Categorical **Expense Distribution Donut Chart** with centered ledger metrics.
  - Quick glance at recent transactions with one-click navigation.

- **Complete Transaction Ledger & History**:
  - Live search across description, notes, and tags.
  - Multi-criteria filtering by **Type** (*All, Expense, Income*) and **Category**.
  - Interactive table with color-coded transaction badges (+/- indicators).
  - In-place record editing (modal dialog) and safe deletion confirmation.

- **Seamless Transaction Entry**:
  - Smart segmented toggle for **Expense** vs **Income** (auto-adjusts categories).
  - Automatic date assignment (defaults to today `YYYY-MM-DD`).
  - Dropdown payment methods (*Credit Card, Debit Card, Bank Transfer, Cash, Digital Wallet, Crypto*).
  - Optional memo / invoice / receipt note field.

- **Monthly Budget Planner & Alerts**:
  - Category-level spending limits with progress indicators.
  - Real-time status badges: **Normal** (Green), **Warning >80%** (Amber), and **OVER BUDGET >100%** (Red).
  - Overall monthly budget health gauge.

- **Financial Intelligence & Analytics**:
  - Horizontal bar ranking for top spending categories.
  - Average expense ticket size, highest single purchase, and transaction volume counters.

- **Data Portability & Customization**:
  - **Dark / Light Theme Switcher** with real-time UI palette and chart re-rendering.
  - Currency symbol configuration (`$`, `€`, `£`, `₹`, `¥`, `₩`, etc.).
  - **CSV Export & Import**: Export to Excel/Google Sheets or load ledger backups.
  - Built-in **Demo Data Generator**: Populates 90 days of realistic financial transactions with one click.
  - Zero-maintenance local **SQLite** persistence (`expenses.db`).

---

## 🚀 Getting Started

### 1. Requirements
Ensure Python 3.10+ is installed. Dependencies can be installed via:

```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Run via python:
```bash
python main.py
```
Or simply double-click **`run.bat`** on Windows!

---

## 📁 Project Architecture

| File | Description |
|---|---|
| [`main.py`](file:///c:/Users/ayaan/Desktop/development/PYTHON/Expense%20Tracker/main.py) | Application entry point launcher |
| [`app.py`](file:///c:/Users/ayaan/Desktop/development/PYTHON/Expense%20Tracker/app.py) | Full CustomTkinter GUI implementation with 6 interactive views |
| [`database.py`](file:///c:/Users/ayaan/Desktop/development/PYTHON/Expense%20Tracker/database.py) | SQLite data layer, transaction CRUD, budget queries, demo data |
| [`charts.py`](file:///c:/Users/ayaan/Desktop/development/PYTHON/Expense%20Tracker/charts.py) | Matplotlib embedded canvas charts tailored for Dark & Light themes |
| [`run.bat`](file:///c:/Users/ayaan/Desktop/development/PYTHON/Expense%20Tracker/run.bat) | Windows 1-click batch launcher |
| [`requirements.txt`](file:///c:/Users/ayaan/Desktop/development/PYTHON/Expense%20Tracker/requirements.txt) | Python dependencies specification |
