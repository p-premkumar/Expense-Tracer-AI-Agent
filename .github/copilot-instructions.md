# AI Agent Instructions: Telegram Expense Tracker Bot

## Project Overview
A Telegram bot that tracks expenses using natural language processing. Users send messages like "Spent 150 for biriyani" and the bot automatically extracts amount, categorizes, and stores in SQLite. Core workflow: **Text/Photo → NLP Parser → Category Detection → Database → Summary Reports**.

## Architecture & Data Flow

### Core Components
1. **main.py** - Telegram bot entry point using `python-telegram-bot` library
   - Initializes handlers for messages (`handle_message`) and photos (`handle_photo`)
   - Routes commands to `bot_commands.py`
   - Manages database and parser instances globally (`db`, `parser`)

2. **nlp_processor.py** - `ExpenseParser` class for extraction
   - `parse_expense(text)` returns `(amount, category, description)` tuple
   - `_extract_amount()` uses regex to find first valid number (0-1000000 range)
   - `_extract_category()` matches keywords from `config.EXPENSE_PATTERNS` dict
   - **Key pattern**: Config-driven category mapping (e.g., "biriyani" → Food)

3. **database.py** - `ExpenseDatabase` class manages SQLite
   - Three tables: `users`, `expenses`, `categories`
   - Key methods: `add_expense()`, `get_summary()`, `get_expenses_by_date()`
   - Stores: `user_id`, `amount`, `category`, `description`, `date`, `source` (text/photo)

4. **bot_commands.py** - 10+ async command handlers
   - Summary logic: `db.get_summary(user_id, days)` groups by category
   - Time-based filtering: `/weekly` (7 days), `/monthly` (30 days), `/today`

### Data Flow
```
User Message → handle_message() → parser.parse_expense() → db.add_expense() 
→ Confirmation Response → /summary queries group by category
```

## Critical Conventions & Patterns

### NLP Parsing Strategy
- **No ML models** - Pure regex + keyword matching from hardcoded patterns in `config.EXPENSE_PATTERNS`
- **Amount extraction**: First number (0-1000000) is the expense amount; ignores dates/IDs
- **Category fallback**: Returns "Other" if no keyword match found
- **Description preservation**: Full user text stored for context

### Database Access
- Always instantiate globally: `db = ExpenseDatabase()` in module scope (see main.py, bot_commands.py)
- All queries use `user_id` filtering for multi-user isolation
- Timestamps auto-generated (`CURRENT_TIMESTAMP`)

### Telegram Handler Pattern
- **Async-first**: All handlers must be `async def`
- **Update/Context pattern**: `async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE)`
- **User tracking**: Always call `db.add_user()` first in handlers to ensure user exists
- **Text validation**: Check `update.message.text` and `.strip()` before parsing
- **Reply method**: `await update.message.reply_text(text, parse_mode='Markdown')`

## Key Files to Understand Each Feature
| Feature | Primary File | Supporting |
|---------|--------------|-----------|
| Text expense parsing | nlp_processor.py | config.py (patterns) |
| Photo/receipt OCR | main.py `handle_photo()` | nlp_processor.py |
| Category detection | config.py (patterns dict) | nlp_processor.py |
| Summaries/reports | bot_commands.py | database.py |
| Multi-user support | database.py (user_id FK) | main.py, bot_commands.py |

## Integration Points & External Dependencies

- **python-telegram-bot** (v21+): `Application`, `CommandHandler`, `MessageHandler`, `Update`, `ContextTypes`
- **SQLite3** (built-in): Connection pool in `database.py`
- **Tesseract OCR** (optional): For receipt image processing in `handle_photo()`
- **dotenv**: Loads environment variables (though BOT_TOKEN hardcoded in config.py)

## Developer Workflows

### Running & Testing
```bash
# Install: pip install -r requirements.txt
# Verify: python startup.py (checks dependencies)
# Run: python main.py (polls Telegram API)
# Test NLP: python test_parser.py
```

### Adding New Features
1. **New command**: Add handler to `bot_commands.py`, register in `main.py` with `CommandHandler("/name", handler)`
2. **New category**: Add to `config.EXPENSE_CATEGORIES` and pattern keywords in `config.EXPENSE_PATTERNS`
3. **Database change**: Extend `ExpenseDatabase.init_db()` and add query method
4. **NLP improvement**: Modify `ExpenseParser` methods; test with `test_parser.py`

### Common Modifications
- **Bot token**: [config.py](config.py) line ~11 (`BOT_TOKEN`)
- **Categories**: [config.py](config.py) `EXPENSE_CATEGORIES` list
- **Keywords**: [config.py](config.py) `EXPENSE_PATTERNS` dict
- **Messages**: Strings in [bot_commands.py](bot_commands.py) (user-facing) and [main.py](main.py) (confirmations)

## Deployment Notes
- Bot runs as long-running process polling Telegram API (`Application.run_polling()`)
- Database persists locally (`expenses.db`) - no cloud sync
- No authentication required; security via Telegram's user_id (requires valid Telegram account to message bot)
- Production: See [DEPLOYMENT.md](DEPLOYMENT.md) for systemd/Docker setup

## Potential Gotchas
- **Global instances**: `db` and `parser` are module-level singletons - be careful with state mutations
- **Timezone naive**: Timestamps use SQLite `CURRENT_TIMESTAMP` (system time, no timezone awareness)
- **Amount extraction order matters**: First regex match wins - "Spent 1500 on Item 2" would extract 1500, not 2
- **No user input validation**: Bot accepts any category; validation only in `is_valid_expense()` method
