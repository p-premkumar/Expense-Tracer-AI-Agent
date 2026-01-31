# 🚀 Deployment & Advanced Setup Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Advanced Configuration](#advanced-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites
- Python 3.9+
- pip or conda
- Telegram account
- Git (optional)

### Installation

1. **Clone/Create the project directory:**
```bash
cd "Expense Tracer AI Agent"
```

2. **Create virtual environment (recommended):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Tesseract OCR (optional but recommended):**

**Windows:**
- Download installer: https://github.com/UB-Mannheim/tesseract/wiki
- Run installer and note the installation path
- Update `config.py` with Tesseract path if needed

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

5. **Run diagnostic:**
```bash
python startup.py
```

6. **Start the bot:**
```bash
python main.py
```

---

## Production Deployment

### Using Docker

1. **Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y tesseract-ocr

COPY . .

CMD ["python", "main.py"]
```

2. **Build and run:**
```bash
docker build -t expense-tracker .
docker run -v $(pwd)/expenses.db:/app/expenses.db expense-tracker
```

### Using Systemd (Linux)

1. **Create service file** `/etc/systemd/system/expense-tracker.service`:
```ini
[Unit]
Description=Telegram Expense Tracker Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Expense\ Tracer\ AI\ Agent
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start:**
```bash
sudo systemctl enable expense-tracker
sudo systemctl start expense-tracker
sudo systemctl status expense-tracker
```

### Using Windows Task Scheduler

1. **Create a batch script** `start_bot.bat`:
```batch
@echo off
cd /d "C:\Users\PRAVEEN\OneDrive\Desktop\Expense Tracer AI Agent"
python main.py
pause
```

2. **Create scheduled task:**
- Open Task Scheduler
- Create Basic Task
- Set trigger: At system startup
- Set action: Run script `start_bot.bat`

---

## Cloud Deployment

### Heroku (Free tier ended, but process similar for other platforms)

### AWS EC2

1. **Launch EC2 instance:**
```bash
# Connect to instance
ssh -i your_key.pem ubuntu@your_instance_ip
```

2. **Setup on server:**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python
sudo apt-get install python3.9 python3-pip -y

# Install Tesseract
sudo apt-get install tesseract-ocr -y

# Clone/Upload project
git clone <your-repo-url>
cd "Expense Tracer AI Agent"

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start bot with nohup (runs in background)
nohup python main.py > bot.log 2>&1 &
```

### PythonAnywhere

1. Create account at pythonywhere.com
2. Upload project files
3. Create web app (or scheduled task for bot)
4. Configure to run `main.py`

### Google Cloud Platform

```bash
# Create project
gcloud projects create expense-tracker

# Deploy on Cloud Run
gcloud run deploy expense-tracker \
  --source . \
  --runtime python39 \
  --allow-unauthenticated
```

---

## Advanced Configuration

### Database Optimization

For large datasets, optimize SQLite:

```python
# Add to database.py after creating connection
conn.execute('PRAGMA journal_mode = WAL')
conn.execute('PRAGMA synchronous = NORMAL')
conn.execute('PRAGMA cache_size = -64000')
conn.execute('PRAGMA foreign_keys = ON')
```

### Enable Logging

Edit `main.py`:
```python
import logging

# Add detailed logging
logging.basicConfig(
    filename='bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Add Webhook Support (Instead of Polling)

```python
from telegram.ext import Application
from telegram import Update

# Use webhook instead of polling
application = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)

async def handle_update(update: Update):
    # Process update
    pass

# Instead of polling
# application.run_polling()

# Use webhook
app.run_webhook(
    listen="0.0.0.0",
    port=8000,
    url_path=BOT_TOKEN,
    webhook_url=f"{YOUR_DOMAIN}/{BOT_TOKEN}"
)
```

### Enable Bot Statistics

Add to `bot_commands.py`:
```python
async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics"""
    user_id = update.effective_user.id
    
    # Get stats
    expenses = db.get_expenses(user_id)
    summary = db.get_summary(user_id, 30)
    
    stats = f"""
    📊 Bot Statistics
    Total expenses: {len(expenses)}
    Categories tracked: {len(summary)}
    Average daily: ₹{db.get_total_today(user_id)/30:.2f}
    """
    
    await update.message.reply_text(stats)
```

---

## Troubleshooting

### Bot doesn't start

```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
python startup.py

# Check bot token
# Verify in config.py that token is correct
```

### Bot doesn't respond to messages

```bash
# Check logs
tail -f bot.log

# Verify Telegram API is accessible
ping api.telegram.org

# Check firewall settings
# Ensure outbound HTTPS (443) is allowed
```

### Database errors

```bash
# Reset database
rm expenses.db

# Check permissions
ls -la expenses.db

# Verify database integrity
python -c "import sqlite3; sqlite3.connect('expenses.db').execute('PRAGMA integrity_check')"
```

### OCR not working

```bash
# Check Tesseract installation
tesseract --version

# Add to config.py:
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Test with sample image
python test_parser.py
```

### High CPU/Memory usage

```python
# Reduce polling frequency in main.py
application.run_polling(poll_interval=2.0)

# Enable garbage collection
import gc
gc.enable()
```

### Database too large

```python
# Archive old expenses (older than 1 year)
def archive_old_expenses(self):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM expenses 
        WHERE date < datetime('now', '-1 year')
    ''')
    
    conn.commit()
    conn.close()
```

---

## Monitoring & Maintenance

### Health Check Script

Create `health_check.py`:
```python
import requests
import subprocess

def check_bot():
    try:
        # Check if bot process is running
        result = subprocess.run(['pgrep', '-f', 'main.py'], 
                              capture_output=True)
        return result.returncode == 0
    except:
        return False

if __name__ == "__main__":
    if not check_bot():
        # Restart bot
        subprocess.run(['python', 'main.py'])
        print("Bot restarted")
    else:
        print("Bot is running")
```

### Backup Database

```bash
# Automated daily backup
0 2 * * * cp /path/to/expenses.db /path/to/backup/expenses_$(date +\%Y\%m\%d).db
```

### Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update requirements
pip install -r requirements.txt --upgrade
```

---

## Security Best Practices

1. **Keep bot token secret:**
   - Use environment variables
   - Never commit token to git
   - Use `.env` file with `.gitignore`

2. **Validate user input:**
   - Already implemented in `nlp_processor.py`
   - Add additional validation as needed

3. **Rate limiting:**
   - Telegram handles this automatically
   - Implement custom limits if needed

4. **Database security:**
   - Use strong file permissions
   - Regular backups
   - Consider encryption for sensitive data

5. **Logs security:**
   - Don't log sensitive information
   - Rotate log files regularly
   - Restrict log file access

---

## Performance Tips

1. **Index database:**
```sql
CREATE INDEX idx_user_id ON expenses(user_id);
CREATE INDEX idx_date ON expenses(date);
CREATE INDEX idx_category ON expenses(category);
```

2. **Cache frequently accessed data:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_categories(self, user_id):
    # Cached results
    pass
```

3. **Use connection pooling** for high-traffic scenarios

4. **Compress old data** in database

---

## Support & Resources

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Python-telegram-bot:** https://python-telegram-bot.readthedocs.io
- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **SQLite Documentation:** https://www.sqlite.org/docs.html

---

**Last Updated:** January 2026  
**Version:** 1.0.0
