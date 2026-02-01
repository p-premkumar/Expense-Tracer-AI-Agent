"""
Telegram bot command handlers
"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import ExpenseDatabase
from config import CURRENCY, EXPENSE_CATEGORIES
from datetime import datetime
from excel_exporter import ExcelExporter

db = ExpenseDatabase()
exporter = ExcelExporter()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
👋 Welcome to Expense Tracker AI Agent, {user.first_name}!

I help you track your expenses automatically. Just send me messages like:
• "Spent 150 for biriyani"
• "150 on transport"
• "200 for movie"

I'll extract the amount and category, then store it automatically.

🔍 **What I can do:**
• 📝 Parse text expenses
• 📸 Process receipt photos using OCR
• 📊 Generate weekly/monthly summaries
• 📈 Track expenses by category
• ✏️ Edit or delete expenses

Use /help for available commands.
    """
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    help_text = f"""
*EXPENSE TRACKER BOT - COMPLETE GUIDE*

*BASIC COMMANDS:*
/start - Welcome message
/help - This help message

*VIEW EXPENSES:*
/summary - Last 30 days summary
/weekly - Last 7 days summary
/month - Last 30 days summary
/today - Today's total
/list - Show last 10 expenses
/stats - Detailed statistics

*BUDGET MANAGEMENT:*
/setdaily <amount> - Set daily budget limit
/setweekly <amount> - Set weekly budget limit  
/setmonthly <amount> - Set monthly budget limit
/limits - View current budget status

*REPORTS:*
/week - Weekly report with breakdown
/month - Monthly report with breakdown

*EXPORT DATA:*
/export - Excel export (all expenses)
/export_today - Excel export (today)
/export_weekly - Excel export (last 7 days)
/export_monthly - Excel export (last 30 days)
/export_csv - CSV format export
/pdf - PDF export (coming soon)
/graph - Graph visualization (coming soon)

*MANAGE DATA:*
/categories - Show all categories
/delete - Delete last expense
/list - Show last 10 expenses

*HOW TO ADD EXPENSES:*
Send natural language messages:
• "Spent 150 for biriyani"
• "50 on transport"
• "200 for movie"

*PHOTO RECEIPTS:*
Send a photo of your receipt to auto-extract amount and category

*VOICE MESSAGES:*
Send voice message describing expense - I'll transcribe and record it

*ONLINE PAYMENTS:*
Send payment screenshot with caption:
TXID: xyz123
Account: MyBank

*CATEGORIES:*
{', '.join(EXPENSE_CATEGORIES)}

Use /limits to monitor your budget usage!
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int = 30) -> None:
    """Show expense summary"""
    user_id = update.effective_user.id
    expenses = db.get_summary(user_id, days)
    
    if not expenses:
        await update.message.reply_text("No expenses found for this period.")
        return
    
    summary_text = f"📊 **Expense Summary (Last {days} days)**\n\n"
    total = 0
    
    for category, amount, count in expenses:
        summary_text += f"🏷️ {category}: {CURRENCY}{amount:.2f} ({count} items)\n"
        total += amount
    
    summary_text += f"\n💰 **Total: {CURRENCY}{total:.2f}**"
    
    await update.message.reply_text(summary_text, parse_mode='Markdown')

async def weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show weekly summary"""
    await summary(update, context, days=7)

async def monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show monthly summary"""
    await summary(update, context, days=30)

async def today_total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show today's total"""
    user_id = update.effective_user.id
    total = db.get_total_today(user_id)
    
    message = f"💸 **Today's Spending: {CURRENCY}{total:.2f}**"
    await update.message.reply_text(message, parse_mode='Markdown')

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all categories"""
    categories_text = "📂 **Expense Categories:**\n\n"
    for category in EXPENSE_CATEGORIES:
        categories_text += f"• {category}\n"
    
    await update.message.reply_text(categories_text, parse_mode='Markdown')

async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List last 10 expenses"""
    user_id = update.effective_user.id
    expenses = db.get_expenses(user_id)[:10]
    
    if not expenses:
        await update.message.reply_text("No expenses found.")
        return
    
    list_text = "📝 **Last 10 Expenses:**\n\n"
    for idx, (exp_id, amount, category, description, date) in enumerate(expenses, 1):
        date_obj = datetime.fromisoformat(date)
        date_str = date_obj.strftime("%d-%m-%Y %H:%M")
        list_text += f"{idx}. {category} - {CURRENCY}{amount:.2f} ({date_str})\n"
    
    await update.message.reply_text(list_text, parse_mode='Markdown')

async def delete_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete last expense"""
    user_id = update.effective_user.id
    expenses = db.get_expenses(user_id)
    
    if not expenses:
        await update.message.reply_text("No expenses to delete.")
        return
    
    exp_id = expenses[0][0]
    db.delete_expense(exp_id, user_id)
    
    await update.message.reply_text("✅ Last expense deleted!")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed statistics"""
    user_id = update.effective_user.id
    expenses_30 = db.get_summary(user_id, 30)
    expenses_7 = db.get_summary(user_id, 7)
    
    stats_text = "📈 **Detailed Statistics**\n\n"
    
    # Last 7 days
    stats_text += "**Last 7 Days:**\n"
    total_7 = 0
    if expenses_7:
        for category, amount, count in expenses_7:
            stats_text += f"  {category}: {CURRENCY}{amount:.2f}\n"
            total_7 += amount
        stats_text += f"  **Total: {CURRENCY}{total_7:.2f}**\n\n"
    else:
        stats_text += "  No expenses\n\n"
    
    # Last 30 days
    stats_text += "**Last 30 Days:**\n"
    total_30 = 0
    if expenses_30:
        for category, amount, count in expenses_30:
            stats_text += f"  {category}: {CURRENCY}{amount:.2f}\n"
            total_30 += amount
        stats_text += f"  **Total: {CURRENCY}{total_30:.2f}**\n"
    else:
        stats_text += "  No expenses\n"
    
    # Daily average
    if expenses_30:
        daily_avg = total_30 / 30
        stats_text += f"\n💡 **Daily Average: {CURRENCY}{daily_avg:.2f}**"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')
async def export_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export all expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating Excel file with all your expenses...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_all_expenses(user_id)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **All Expenses Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\nSheets included:\n• All Expenses\n• Summary\n• Monthly Breakdown",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Excel file exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating Excel file: {str(e)}")

async def export_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export monthly expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating monthly expense report...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_monthly_expenses(user_id)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **Monthly Expense Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\nPeriod: Last 30 days\n\nSheets included:\n• Summary by Category\n• Detailed Transactions",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Monthly report exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")

async def export_weekly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export weekly expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating weekly expense report...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_custom_period(user_id, days=7)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **Weekly Expense Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\nPeriod: Last 7 days",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Weekly report exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")

async def export_today_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export today's expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating today's expense report...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_custom_period(user_id, days=1)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **Today's Expense Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Today's report exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")

# ===== BUDGET LIMIT COMMANDS =====

async def set_daily_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set daily budget limit"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /setdaily <amount>\nExample: `/setdaily 500`", parse_mode='Markdown')
        return
    
    try:
        amount = float(context.args[0])
        db.set_budget_limit(user_id, 'daily', amount)
        await update.message.reply_text(f"✅ Daily limit set to {CURRENCY}{amount:.2f}")
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a number.")

async def set_weekly_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set weekly budget limit"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /setweekly <amount>\nExample: `/setweekly 3500`", parse_mode='Markdown')
        return
    
    try:
        amount = float(context.args[0])
        db.set_budget_limit(user_id, 'weekly', amount)
        await update.message.reply_text(f"✅ Weekly limit set to {CURRENCY}{amount:.2f}")
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a number.")

async def set_monthly_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set monthly budget limit"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /setmonthly <amount>\nExample: `/setmonthly 15000`", parse_mode='Markdown')
        return
    
    try:
        amount = float(context.args[0])
        db.set_budget_limit(user_id, 'monthly', amount)
        await update.message.reply_text(f"✅ Monthly limit set to {CURRENCY}{amount:.2f}")
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a number.")

def get_limit_status(current, limit):
    """Get budget warning status"""
    if not limit:
        return None
    
    percentage = (current / limit) * 100
    
    if percentage >= 100:
        return "🔴", percentage
    elif percentage >= 90:
        return "⚠️", percentage
    elif percentage >= 75:
        return "⚡", percentage
    else:
        return "✅", percentage

async def check_limits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check budget status"""
    user_id = update.effective_user.id
    
    daily_limit, weekly_limit, monthly_limit = db.get_budget_limits(user_id)
    
    if not any([daily_limit, weekly_limit, monthly_limit]):
        await update.message.reply_text(
            "❌ No limits set.\n\nSet limits using:\n"
            "/setdaily <amount>\n"
            "/setweekly <amount>\n"
            "/setmonthly <amount>",
            parse_mode='Markdown'
        )
        return
    
    today_total = db.get_total_today(user_id)
    week_total = db.get_total_week(user_id)
    month_total = db.get_total_month(user_id)
    
    limits_text = "💰 **Budget Status**\n\n"
    
    if daily_limit:
        status, percentage = get_limit_status(today_total, daily_limit)
        limits_text += f"{status} **Daily:** {CURRENCY}{today_total:.2f} / {CURRENCY}{daily_limit:.2f} ({percentage:.0f}%)\n"
    
    if weekly_limit:
        status, percentage = get_limit_status(week_total, weekly_limit)
        limits_text += f"{status} **Weekly:** {CURRENCY}{week_total:.2f} / {CURRENCY}{weekly_limit:.2f} ({percentage:.0f}%)\n"
    
    if monthly_limit:
        status, percentage = get_limit_status(month_total, monthly_limit)
        limits_text += f"{status} **Monthly:** {CURRENCY}{month_total:.2f} / {CURRENCY}{monthly_limit:.2f} ({percentage:.0f}%)\n"
    
    await update.message.reply_text(limits_text, parse_mode='Markdown')

async def report_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show weekly report"""
    user_id = update.effective_user.id
    expenses = db.get_summary(user_id, 7)
    
    if not expenses:
        await update.message.reply_text("No expenses found for this week.")
        return
    
    report_text = "📊 **Weekly Report (Last 7 Days)**\n\n"
    total = 0
    
    for category, amount, count in expenses:
        report_text += f"🏷️ {category}: {CURRENCY}{amount:.2f} ({count} items)\n"
        total += amount
    
    report_text += f"\n💰 **Total: {CURRENCY}{total:.2f}**"
    
    await update.message.reply_text(report_text, parse_mode='Markdown')

async def report_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show monthly report"""
    user_id = update.effective_user.id
    expenses = db.get_summary(user_id, 30)
    
    if not expenses:
        await update.message.reply_text("No expenses found for this month.")
        return
    
    report_text = "📊 **Monthly Report (Last 30 Days)**\n\n"
    total = 0
    
    for category, amount, count in expenses:
        report_text += f"🏷️ {category}: {CURRENCY}{amount:.2f} ({count} items)\n"
        total += amount
    
    report_text += f"\n💰 **Total: {CURRENCY}{total:.2f}**"
    
    await update.message.reply_text(report_text, parse_mode='Markdown')

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export all expenses as CSV"""
    user_id = update.effective_user.id
    expenses = db.get_expenses(user_id)
    
    if not expenses:
        await update.message.reply_text("No expenses to export.")
        return
    
    # Create CSV content
    csv_content = "Date,Category,Amount,Description\n"
    for exp_id, amount, category, description, date in expenses:
        csv_content += f'"{date}","{category}","{amount}","{description}"\n'
    
    # Save to file
    filename = f"expenses_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w') as f:
        f.write(csv_content)
    
    # Send file
    with open(filename, 'rb') as csv_file:
        await update.message.reply_document(
            document=csv_file,
            caption="📊 Expenses CSV Export",
            filename=filename
        )
    
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)
    
    await update.message.reply_text("✅ CSV exported successfully!")

async def export_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Placeholder for PDF export"""
    await update.message.reply_text("📄 PDF export coming soon! Use /export_monthly for Excel format.")

async def export_graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Placeholder for graph export"""
    await update.message.reply_text("📈 Graph export coming soon! Use /stats to see text-based statistics.")
