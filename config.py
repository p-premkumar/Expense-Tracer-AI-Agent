"""
Configuration file for Expense Tracker Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = "8140750596:AAEaSEXVus7m1_3iVhQ7BXDtA4uu-YEzyno"

# Database
DATABASE_PATH = "expenses.db"

# Supported categories
EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Entertainment",
    "Shopping",
    "Utilities",
    "Health",
    "Education",
    "Travel",
    "Work",
    "Other"
]

# Currency
CURRENCY = "₹"

# Text patterns for expense detection
EXPENSE_PATTERNS = {
    "food": ["food", "eat", "lunch", "breakfast", "dinner", "biriyani", "pizza", "burger", "coffee"],
    "transport": ["transport", "travel", "taxi", "bus", "metro", "fuel", "petrol"],
    "entertainment": ["movie", "game", "show", "concert", "play", "entertainment"],
    "shopping": ["shop", "buy", "clothes", "shoe", "gift","shirt"],
    "utilities": ["bill", "electricity", "water", "internet", "phone"],
    "health": ["medicine", "doctor", "hospital", "health"],
    "education": ["course", "book", "education", "training", "tuition"],
    "travel": ["hotel", "flight", "vacation", "trip", "stay"],
    "work": ["office", "work", "project", "meeting"],
}
