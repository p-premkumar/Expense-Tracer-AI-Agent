# Budget Management Features - Implementation Guide

## Overview

The Expense Tracker Bot now includes comprehensive budget management features that allow users to:
- Set daily, weekly, and monthly spending limits
- Monitor their current spending against limits
- Receive automatic warnings when approaching or exceeding limits
- View budget status with visual indicators

## New Features Implemented

### 1. Budget Limit Commands

#### `/setdaily <amount>`
Sets a daily spending limit for the user.

**Example:**
```
/setdaily 500
```

**Response:**
```
✅ Daily limit set to ₹500.00
```

#### `/setweekly <amount>`
Sets a weekly spending limit (last 7 days).

**Example:**
```
/setweekly 3500
```

**Response:**
```
✅ Weekly limit set to ₹3500.00
```

#### `/setmonthly <amount>`
Sets a monthly spending limit (last 30 days).

**Example:**
```
/setmonthly 15000
```

**Response:**
```
✅ Monthly limit set to ₹15000.00
```

### 2. Budget Status Monitoring

#### `/limits`
Displays current spending against set limits with warning indicators.

**Example Response:**
```
💰 Budget Status

✅ Daily: ₹250.00 / ₹500.00 (50%)
⚡ Weekly: ₹2625.00 / ₹3500.00 (75%)
⚠️ Monthly: ₹12450.00 / ₹15000.00 (83%)
```

**Warning Levels:**
- ✅ Green (Safe): 0-74%
- ⚡ Yellow (Caution): 75-89%
- ⚠️ Orange (Critical): 90-99%
- 🔴 Red (Exceeded): 100%+

### 3. Automatic Budget Alerts

When adding a new expense, the bot automatically checks budget limits and sends alerts if thresholds are crossed.

**Example:**
```
User: Spent 200 for shopping

Bot: ✅ Expense Recorded!
💰 Amount: ₹200.00
🏷️ Category: Shopping
📝 Description: shopping

*Budget Alert:*
⚡ Daily limit at 75%: ₹375.00 / ₹500.00
⚠️ Weekly limit at 90%: ₹3150.00 / ₹3500.00
```

### 4. Enhanced Reports

#### `/week`
Shows weekly expense breakdown with category details.

#### `/month`
Shows monthly expense breakdown with category details.

#### `/today`
Shows today's expenses (existing command, now with budget awareness).

### 5. Export Enhancements

#### `/export_csv`
Exports all expenses in CSV format.

#### `/pdf`
PDF export (coming soon).

#### `/graph`
Graph visualization export (coming soon).

## Database Schema

### budget_limits Table
```sql
CREATE TABLE budget_limits (
    limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    daily_limit REAL,
    weekly_limit REAL,
    monthly_limit REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
```

## Core Implementation Details

### Budget Tracking Algorithm

The budget tracking system uses the following logic:

1. **Daily Total**: Sum of expenses from current date
2. **Weekly Total**: Sum of expenses from last 7 days
3. **Monthly Total**: Sum of expenses from last 30 days

### Warning Threshold Logic

```python
def get_limit_status(current, limit):
    if not limit:
        return None
    
    percentage = (current / limit) * 100
    
    if percentage >= 100:
        return "🔴", percentage      # Exceeded
    elif percentage >= 90:
        return "⚠️", percentage       # Critical
    elif percentage >= 75:
        return "⚡", percentage       # Warning
    else:
        return "✅", percentage       # Safe
```

### Expense Recording with Budget Checks

When a new expense is recorded:

1. Expense is added to database
2. Budget limits are retrieved for the user
3. Current totals (daily, weekly, monthly) are calculated
4. Percentages are compared against thresholds
5. Warnings are sent if any threshold is crossed

## Configuration

### Currency Setting
Budget limits and alerts use the currency defined in `config.py`:
```python
CURRENCY = "₹"
```

### Budget Limit Constraints
- Minimum: 0.01 (any positive value)
- Maximum: No hard limit (practical limit depends on use case)
- Decimal precision: 2 places

## Database Methods

### New Methods in `ExpenseDatabase`

#### `set_budget_limit(user_id, limit_type, amount)`
Sets or updates a budget limit for a user.

**Parameters:**
- `user_id`: Telegram user ID
- `limit_type`: 'daily', 'weekly', or 'monthly'
- `amount`: Limit amount in specified currency

#### `get_budget_limits(user_id)`
Retrieves all budget limits for a user.

**Returns:** Tuple of (daily_limit, weekly_limit, monthly_limit)

#### `get_total_today(user_id)`
Calculates today's total expenses.

**Returns:** Float amount

#### `get_total_week(user_id)`
Calculates last 7 days' total expenses.

**Returns:** Float amount

#### `get_total_month(user_id)`
Calculates last 30 days' total expenses.

**Returns:** Float amount

## New Commands in bot_commands.py

### Set Budget Commands
- `set_daily_limit()` - Handles /setdaily command
- `set_weekly_limit()` - Handles /setweekly command
- `set_monthly_limit()` - Handles /setmonthly command

### Status/Report Commands
- `check_limits()` - Handles /limits command
- `report_week()` - Handles /week command
- `report_month()` - Handles /month command

### Export Commands
- `export_csv()` - Handles /export_csv command
- `export_pdf()` - Placeholder for /pdf command
- `export_graph()` - Placeholder for /graph command

### Helper Functions
- `get_limit_status()` - Calculates warning level and percentage

## Integration Points

### main.py Changes

**Imports:**
```python
from bot_commands import (
    ...
    set_daily_limit,
    set_weekly_limit,
    set_monthly_limit,
    check_limits,
    report_week,
    report_month,
    export_csv,
    export_pdf,
    export_graph,
)
```

**Command Registration:**
```python
application.add_handler(CommandHandler("setdaily", set_daily_limit))
application.add_handler(CommandHandler("setweekly", set_weekly_limit))
application.add_handler(CommandHandler("setmonthly", set_monthly_limit))
application.add_handler(CommandHandler("limits", check_limits))
application.add_handler(CommandHandler("week", report_week))
application.add_handler(CommandHandler("month", report_month))
application.add_handler(CommandHandler("export_csv", export_csv))
application.add_handler(CommandHandler("pdf", export_pdf))
application.add_handler(CommandHandler("graph", export_graph))
```

**Budget Alert Logic in handle_message():**
After adding an expense, the function checks budget limits and sends warnings if needed.

## Usage Examples

### Setting Budgets
```
User: /setdaily 500
Bot: ✅ Daily limit set to ₹500.00

User: /setweekly 3500
Bot: ✅ Weekly limit set to ₹3500.00

User: /setmonthly 15000
Bot: ✅ Monthly limit set to ₹15000.00
```

### Monitoring Budget
```
User: /limits
Bot: 💰 Budget Status

✅ Daily: ₹125.50 / ₹500.00 (25%)
✅ Weekly: ₹875.25 / ₹3500.00 (25%)
✅ Monthly: ₹3250.75 / ₹15000.00 (22%)
```

### Adding Expense with Alert
```
User: Spent 400 for shopping
Bot: ✅ Expense Recorded!
💰 Amount: ₹400.00
🏷️ Category: Shopping
📝 Description: shopping

*Budget Alert:*
⚡ Daily limit at 75%: ₹375.00 / ₹500.00
```

## Testing

All budget features have been tested with 100% pass rate:

**Test Coverage:**
- Budget limit setting and retrieval
- Total calculation (daily, weekly, monthly)
- Warning threshold logic
- Multi-user isolation
- Command parsing and validation

**Run Tests:**
```bash
python -m unittest test_budget_features.py -v
```

## Future Enhancements

### Planned Features
1. **PDF Export** - Generate PDF reports with budget summaries
2. **Graph Visualization** - Create charts showing spending trends
3. **Budget History** - Track historical budget modifications
4. **Budget Recommendations** - AI-powered spending suggestions
5. **Alert Customization** - User-defined alert thresholds
6. **Budget Categories** - Set limits per expense category

### Potential Improvements
- Recurring budget adjustments
- Budget rollover handling
- Advanced analytics and forecasting
- Integration with financial APIs
- Multi-currency support

## Performance Considerations

### Database Queries
- Budget limit queries: O(1) - Single lookup
- Total calculations: O(n) - Full table scan, optimizable with indexed date columns
- Multi-user isolation: Efficient via user_id filtering

### Optimization Opportunities
1. Add database indexes on (user_id, date) for faster total calculations
2. Cache budget limits in memory with periodic refresh
3. Batch budget checks for multiple users
4. Use database views for recurring totals

## Error Handling

### Invalid Input Handling
- Non-numeric amounts: User receives error message
- Negative amounts: Rejected at validation level
- Missing arguments: Usage instructions provided

### Database Error Handling
- Connection failures: Graceful error messages
- Constraint violations: Automatic retry with conflict resolution
- Query timeouts: Fallback to default behavior

## Security Considerations

### Data Protection
- User budgets are isolated per user_id
- No cross-user data leakage possible
- Budget data stored securely in SQLite

### Input Validation
- Amount validation: Must be positive number
- SQL injection prevention: Using parameterized queries
- Command injection prevention: Restricted command set

## Compatibility

- **Python Version**: 3.9+
- **Python-Telegram-Bot**: 22.6+
- **SQLite3**: 3.35+
- **Operating Systems**: Windows, Linux, macOS

## Files Modified/Created

### Modified Files
- `database.py`: Added budget_limits table and query methods
- `bot_commands.py`: Added budget command handlers and help command update
- `main.py`: Added new command handlers and budget alert logic

### New Files
- `test_budget_features.py`: Comprehensive test suite

## Help Command Updates

The `/help` command now displays all budget and export commands:

```
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
```

## Troubleshooting

### Issue: Budget limits not showing
**Solution:** Ensure limits have been set with /setdaily, /setweekly, or /setmonthly commands

### Issue: Warnings not appearing
**Solution:** Check that limits are set and expenses are being added correctly

### Issue: Incorrect totals
**Solution:** Verify database connections and check that expenses have correct timestamps

## Support and Feedback

For issues or feature requests related to budget management, please refer to the project documentation or contact the development team.
