# 🚀 Quick Start Guide - Expense Tracker AI Agent

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Optional - Install Tesseract for OCR
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Step 3: Run Diagnostic Check
```bash
python startup.py
```

This will verify all dependencies and configurations are correct.

## Step 4: Start the Bot
```bash
python main.py
```

You should see:
```
🤖 Expense Tracker Bot is running!
Press Ctrl+C to stop.
```

## Step 5: Open Telegram
Search for a bot using the provided token or scan this QR code:
- Or search: @BotFather > create new bot > get token

## Step 6: Test with Commands
Try these in Telegram:

### Start the bot
```
/start
```

### Add an expense (just send a message)
```
Spent 150 for biriyani
```

### View summary
```
/summary
```

### View help
```
/help
```

## 📝 Common Commands

| Command | What it does |
|---------|-------------|
| `/start` | Welcome & instructions |
| `/help` | List all commands |
| `/summary` | Last 30 days summary |
| `/weekly` | Last 7 days summary |
| `/monthly` | Last 30 days summary |
| `/today` | Today's spending |
| `/categories` | Show all categories |
| `/list` | Last 10 expenses |
| `/stats` | Detailed statistics |
| `/delete` | Delete last expense |

## 💡 Tips

1. **Add expenses naturally** - The bot understands various formats:
   - "Spent 150 for biriyani"
   - "150 on food"
   - "Transport - 50"
   - "200 for movie"

2. **Upload receipts** - Send a photo of your receipt and OCR will extract the amount

3. **Check statistics** - Use `/stats` to understand your spending patterns

4. **View history** - Use `/list` to see your last 10 expenses

## 🆘 Troubleshooting

### Bot not starting?
1. Check Python version: `python --version` (should be 3.9+)
2. Verify dependencies: `python startup.py`
3. Check bot token in `config.py`

### Amount not detected?
Try clearer phrasing:
- ✅ "Spent 150 for food"
- ❌ "approx 150-200 for food"

### OCR not working?
- Tesseract might not be installed
- Try uploading a clearer receipt image
- Use manual entry as fallback

### Database errors?
- Delete `expenses.db` to reset
- Bot will create new database automatically
- All data will be lost - backup if needed!

## 📁 File Structure

```
Expense Tracer AI Agent/
├── main.py              # ← Run this to start bot
├── config.py            # Bot configuration
├── database.py          # Data management
├── nlp_processor.py     # Text parsing & OCR
├── bot_commands.py      # Command handlers
├── analytics.py         # Advanced features
├── startup.py           # Diagnostic check
├── requirements.txt     # Python packages
├── .env                 # Environment variables
├── expenses.db          # Database (auto-created)
└── README.md           # Full documentation
```

## 🎯 Next Steps

1. Start the bot: `python main.py`
2. Open Telegram and find your bot
3. Send `/start` to begin
4. Start adding expenses!
5. Check `/summary` to see your spending

## ❓ Need Help?

- Check [README.md](README.md) for full documentation
- Review bot commands: `/help`
- Run diagnostic: `python startup.py`
- Check logs in console for error messages

---

**Happy expense tracking! 💰**
