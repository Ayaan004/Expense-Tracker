@echo off
title VaultFlow - Professional Expense Tracker
echo Starting VaultFlow...
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred while running the application.
    pause
)
