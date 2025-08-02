from mcp.server.fastmcp import FastMCP
from pydantic import Field
import typing
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
from collections import defaultdict
import hashlib
import json
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set. Please configure it in .env file or deployment environment.")

# Create FastMCP instance

PORT = os.environ.get("PORT",8000)
mcp = FastMCP("expense-tracker",host='0.0.0.0',port=PORT)

# User authentication helpers
current_user_id = None
current_username = None

def get_mongo_client():
    """Get MongoDB client connection"""
    return MongoClient(MONGO_URI)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def require_auth():
    """Check if user is authenticated"""
    global current_user_id
    if not current_user_id:
        raise Exception("Please log in first using the 'login' or 'register' tool.")
    return current_user_id

@mcp.tool(
    name='register',
    description="Register a new user with username and password"
)
def register(username: str, password: str) -> str:
    client = get_mongo_client()
    db = client.expenses
    if db.users.find_one({'username': username}):
        client.close()
        return "Username already exists. Please choose another."
    hashed = hash_password(password)
    result = db.users.insert_one({'username': username, 'password': hashed})
    client.close()
    return f"User '{username}' registered successfully. Please log in."

@mcp.tool(
    name='login',
    description="Log in with username and password"
)
def login(username: str, password: str) -> str:
    global current_user_id, current_username
    client = get_mongo_client()
    db = client.expenses
    user = db.users.find_one({'username': username})
    client.close()
    if not user or user['password'] != hash_password(password):
        return "Invalid username or password."
    current_user_id = str(user['_id'])
    current_username = username
    return f"Logged in as {username}."

@mcp.tool(
    name='logout',
    description="Log out the current user"
)
def logout() -> str:
    global current_user_id, current_username
    current_user_id = None
    current_username = None
    return "Logged out."

@mcp.tool(
    name='add_expense',
    description="Add a new expense for the logged-in user"
)
def add_expense(
    category: str = Field(description="Expense category (e.g., Food, Transport, Entertainment)"),
    amount: float = Field(description="Amount spent"),
    date: str = Field(description="Date in YYYY-MM-DD format"),
    description: str = Field(description="Description of the expense")
) -> str:
    """Add a new expense to the database"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Parse date
        expense_date = datetime.strptime(date, '%Y-%m-%d')
        
        # Insert expense
        expense_data = {
            'user_id': user_id,
            'category': category,
            'amount': amount,
            'date': expense_date,
            'description': description
        }
        
        result = db.expenses.insert_one(expense_data)
        client.close()
        
        return f"Expense added for {current_username} with ID: {str(result.inserted_id)}"
    except Exception as e:
        return f"Error adding expense: {str(e)}"

@mcp.tool(
    name='get_my_expenses',
    description="Get all expenses for the logged-in user"
)
def get_my_expenses() -> str:
    """Get all expenses sorted by date (newest first)"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        expenses = list(db.expenses.find({'user_id': user_id}).sort("date", -1))
        client.close()
        
        if not expenses:
            return "No expenses found."
        
        result = []
        for expense in expenses:
            result.append({
                'id': str(expense['_id']),
                'category': expense['category'],
                'amount': expense['amount'],
                'date': expense['date'].strftime('%Y-%m-%d'),
                'description': expense['description']
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving expenses: {str(e)}"

@mcp.tool(
    name='get_my_expense_by_id',
    description="Get a specific expense by ID for the logged-in user"
)
def get_my_expense_by_id(expense_id: str = Field(description="The MongoDB ObjectId of the expense")) -> str:
    """Get a specific expense by ID"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        expense = db.expenses.find_one({'_id': ObjectId(expense_id), 'user_id': user_id})
        client.close()
        
        if not expense:
            return f"No expense found with ID: {expense_id} for this user."
        
        result = {
            'id': str(expense['_id']),
            'category': expense['category'],
            'amount': expense['amount'],
            'date': expense['date'].strftime('%Y-%m-%d'),
            'description': expense['description']
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving expense: {str(e)}"

@mcp.tool(
    name='update_my_expense',
    description="Update an expense by ID for the logged-in user"
)
def update_my_expense(
    expense_id: str = Field(description="The MongoDB ObjectId of the expense to update"),
    category: Optional[str] = Field(None, description="New category (optional)"),
    amount: Optional[float] = Field(None, description="New amount (optional)"),
    date: Optional[str] = Field(None, description="New date in YYYY-MM-DD format (optional)"),
    description: Optional[str] = Field(None, description="New description (optional)")
) -> str:
    """Update an existing expense"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Build update data
        update_data = {}
        if category is not None:
            update_data['category'] = category
        if amount is not None:
            update_data['amount'] = amount
        if date is not None:
            update_data['date'] = datetime.strptime(date, '%Y-%m-%d')
        if description is not None:
            update_data['description'] = description
        
        if not update_data:
            return "No update data provided."
        
        result = db.expenses.update_one(
            {'_id': ObjectId(expense_id), 'user_id': user_id},
            {'$set': update_data}
        )
        client.close()
        
        if result.matched_count == 0:
            return f"No expense found with ID: {expense_id} for this user."
        
        return f"Expense updated. Modified {result.modified_count} document(s)."
    except Exception as e:
        return f"Error updating expense: {str(e)}"

@mcp.tool(
    name='delete_my_expense',
    description="Delete an expense by ID for the logged-in user"
)
def delete_my_expense(expense_id: str = Field(description="The MongoDB ObjectId of the expense to delete")) -> str:
    """Delete an expense by ID"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        result = db.expenses.delete_one({'_id': ObjectId(expense_id), 'user_id': user_id})
        client.close()
        
        if result.deleted_count == 0:
            return f"No expense found with ID: {expense_id} for this user."
        
        return "Expense deleted."
    except Exception as e:
        return f"Error deleting expense: {str(e)}"

@mcp.tool(
    name='get_my_expenses_by_category',
    description="Get expenses by category for the logged-in user"
)
def get_my_expenses_by_category(category: str = Field(description="Category to filter by")) -> str:
    """Get expenses filtered by category"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        expenses = list(db.expenses.find({'user_id': user_id, 'category': category}).sort("date", -1))
        client.close()
        
        if not expenses:
            return f"No expenses found for category: {category}."
        
        result = []
        total_amount = 0
        for expense in expenses:
            result.append({
                'id': str(expense['_id']),
                'category': expense['category'],
                'amount': expense['amount'],
                'date': expense['date'].strftime('%Y-%m-%d'),
                'description': expense['description']
            })
            total_amount += expense['amount']
        
        return json.dumps({
            'category': category,
            'total_expenses': len(result),
            'total_amount': total_amount,
            'expenses': result
        }, indent=2)
    except Exception as e:
        return f"Error retrieving expenses by category: {str(e)}"

@mcp.tool(
    name='get_my_monthly_report',
    description="Get monthly expense report for the logged-in user"
)
def get_my_monthly_report(year: int = Field(description="Year (e.g., 2024)"), month: int = Field(description="Month (1-12)")) -> str:
    """Get monthly expense report"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Create date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        expenses = list(db.expenses.find({
            'user_id': user_id,
            'date': {'$gte': start_date, '$lt': end_date}
        }).sort("date", -1))
        client.close()
        
        if not expenses:
            return f"No expenses found for {year}-{month:02d}."
        
        # Calculate totals by category
        category_totals = {}
        total_amount = 0
        
        result = []
        for expense in expenses:
            result.append({
                'id': str(expense['_id']),
                'category': expense['category'],
                'amount': expense['amount'],
                'date': expense['date'].strftime('%Y-%m-%d'),
                'description': expense['description']
            })
            
            category = expense['category']
            category_totals[category] = category_totals.get(category, 0) + expense['amount']
            total_amount += expense['amount']
        
        return json.dumps({
            'period': f"{year}-{month:02d}",
            'total_expenses': len(result),
            'total_amount': total_amount,
            'category_breakdown': category_totals,
            'expenses': result
        }, indent=2)
    except Exception as e:
        return f"Error generating monthly report: {str(e)}"

@mcp.tool(
    name='get_my_expense_summary',
    description="Get a summary of all expenses with totals by category for the logged-in user"
)
def get_my_expense_summary() -> str:
    """Get expense summary with category totals"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Aggregate expenses by category
        pipeline = [
            {'$match': {'user_id': user_id}},
            {
                '$group': {
                    '_id': '$category',
                    'total_amount': {'$sum': '$amount'},
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'total_amount': -1}
            }
        ]
        
        category_summary = list(db.expenses.aggregate(pipeline))
        
        # Get overall totals
        total_expenses = db.expenses.count_documents({'user_id': user_id})
        total_amount = sum(cat['total_amount'] for cat in category_summary)
        
        client.close()
        
        result = {
            'total_expenses': total_expenses,
            'total_amount': total_amount,
            'category_breakdown': [
                {
                    'category': cat['_id'],
                    'total_amount': cat['total_amount'],
                    'count': cat['count'],
                    'percentage': round((cat['total_amount'] / total_amount * 100), 2) if total_amount > 0 else 0
                }
                for cat in category_summary
            ]
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error generating expense summary: {str(e)}"

@mcp.tool(
    name='quick_add_expense',
    description="Quickly add an expense with today's date using natural language like 'lunch $15' or 'gas 45.50'"
)
def quick_add_expense(expense_text: str = Field(description="Natural language expense like 'coffee $5.50' or 'uber ride 25'")) -> str:
    """Add expense using natural language - automatically uses today's date"""
    user_id = require_auth()
    try:
        # Parse amount from text
        amount_match = re.search(r'\$?(\d+\.?\d*)', expense_text)
        if not amount_match:
            return "Could not find amount in the text. Please include a number like '$15' or '25.50'"
        
        amount = float(amount_match.group(1))
        
        # Remove amount from text to get description
        description = re.sub(r'\$?\d+\.?\d*', '', expense_text).strip()
        if not description:
            description = f"Expense for ${amount}"
        
        # Smart category detection based on keywords
        description_lower = description.lower()
        if any(word in description_lower for word in ['coffee', 'lunch', 'dinner', 'food', 'restaurant', 'eat', 'pizza', 'burger']):
            category = 'Food'
        elif any(word in description_lower for word in ['uber', 'taxi', 'gas', 'fuel', 'parking', 'bus', 'train', 'transport']):
            category = 'Transport'
        elif any(word in description_lower for word in ['movie', 'cinema', 'game', 'entertainment', 'concert', 'show']):
            category = 'Entertainment'
        elif any(word in description_lower for word in ['grocery', 'supermarket', 'shopping', 'store', 'market']):
            category = 'Groceries'
        elif any(word in description_lower for word in ['bill', 'electric', 'water', 'internet', 'phone', 'utility']):
            category = 'Bills'
        elif any(word in description_lower for word in ['medicine', 'doctor', 'hospital', 'pharmacy', 'health']):
            category = 'Health'
        else:
            category = 'Other'
        
        # Use today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        return add_expense(category, amount, today, description)
    except Exception as e:
        return f"Error parsing expense: {str(e)}"

@mcp.tool(
    name='get_my_today_expenses',
    description="Get all expenses for today for the logged-in user"
)
def get_my_today_expenses() -> str:
    """Get today's expenses with total"""
    user_id = require_auth()
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        client = get_mongo_client()
        db = client.expenses
        
        expenses = list(db.expenses.find({
            'user_id': user_id,
            'date': {'$gte': today, '$lt': tomorrow}
        }).sort("date", -1))
        client.close()
        
        if not expenses:
            return "No expenses recorded for today."
        
        result = []
        total_amount = 0
        for expense in expenses:
            result.append({
                'id': str(expense['_id']),
                'category': expense['category'],
                'amount': expense['amount'],
                'time': expense['date'].strftime('%H:%M'),
                'description': expense['description']
            })
            total_amount += expense['amount']
        
        return json.dumps({
            'date': today.strftime('%Y-%m-%d'),
            'total_expenses': len(result),
            'total_amount': total_amount,
            'expenses': result
        }, indent=2)
    except Exception as e:
        return f"Error retrieving today's expenses: {str(e)}"

@mcp.tool(
    name='get_my_week_summary',
    description="Get expenses summary for the current week for the logged-in user"
)
def get_my_week_summary() -> str:
    """Get current week's expense summary"""
    user_id = require_auth()
    try:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        client = get_mongo_client()
        db = client.expenses
        
        expenses = list(db.expenses.find({
            'user_id': user_id,
            'date': {'$gte': week_start, '$lt': week_end}
        }))
        client.close()
        
        if not expenses:
            return f"No expenses found for this week ({week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')})"
        
        # Group by day and category
        daily_totals = defaultdict(float)
        category_totals = defaultdict(float)
        total_amount = 0
        
        for expense in expenses:
            day = expense['date'].strftime('%A')
            daily_totals[day] += expense['amount']
            category_totals[expense['category']] += expense['amount']
            total_amount += expense['amount']
        
        return json.dumps({
            'week_period': f"{week_start.strftime('%Y-%m-%d')} to {(week_end - timedelta(days=1)).strftime('%Y-%m-%d')}",
            'total_amount': total_amount,
            'daily_breakdown': dict(daily_totals),
            'category_breakdown': dict(category_totals),
            'average_per_day': round(total_amount / 7, 2)
        }, indent=2)
    except Exception as e:
        return f"Error generating week summary: {str(e)}"

@mcp.tool(
    name='find_my_expenses',
    description="Search expenses by description, category, or amount range for the logged-in user"
)
def find_my_expenses(
    search_term: typing.Optional[str] = Field(None, description="Search in description or category"),
    min_amount: typing.Optional[float] = Field(None, description="Minimum amount"),
    max_amount: typing.Optional[float] = Field(None, description="Maximum amount"),
    days_back: typing.Optional[int] = Field(None, description="Search within last N days")
) -> str:
    """Search expenses with flexible criteria"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Build search query
        query = {'user_id': user_id}
        
        if search_term:
            query['$or'] = [
                {'description': {'$regex': search_term, '$options': 'i'}},
                {'category': {'$regex': search_term, '$options': 'i'}}
            ]
        
        if min_amount is not None or max_amount is not None:
            amount_filter = {}
            if min_amount is not None:
                amount_filter['$gte'] = min_amount
            if max_amount is not None:
                amount_filter['$lte'] = max_amount
            query['amount'] = amount_filter
        
        if days_back is not None:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            query['date'] = {'$gte': cutoff_date}
        
        expenses = list(db.expenses.find(query).sort("date", -1))
        client.close()
        
        if not expenses:
            return "No expenses found matching your criteria."
        
        result = []
        total_amount = 0
        for expense in expenses:
            result.append({
                'id': str(expense['_id']),
                'category': expense['category'],
                'amount': expense['amount'],
                'date': expense['date'].strftime('%Y-%m-%d'),
                'description': expense['description']
            })
            total_amount += expense['amount']
        
        return json.dumps({
            'search_criteria': {
                'search_term': search_term,
                'min_amount': min_amount,
                'max_amount': max_amount,
                'days_back': days_back
            },
            'total_found': len(result),
            'total_amount': total_amount,
            'expenses': result
        }, indent=2)
    except Exception as e:
        return f"Error searching expenses: {str(e)}"

@mcp.tool(
    name='get_my_spending_trends',
    description="Analyze spending patterns and trends over time for the logged-in user"
)
def get_my_spending_trends() -> str:
    """Get spending trends and patterns analysis"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Get last 30 days of data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        expenses = list(db.expenses.find({
            'user_id': user_id,
            'date': {'$gte': thirty_days_ago}
        }))
        
        if not expenses:
            return "Not enough data for trend analysis (need at least 30 days of expenses)"
        
        # Analyze by week
        weekly_spending = defaultdict(float)
        category_trends = defaultdict(list)
        daily_spending = defaultdict(float)
        
        for expense in expenses:
            week = expense['date'].strftime('%Y-W%U')
            day = expense['date'].strftime('%Y-%m-%d')
            
            weekly_spending[week] += expense['amount']
            daily_spending[day] += expense['amount']
            category_trends[expense['category']].append(expense['amount'])
        
        # Calculate averages and trends
        weekly_amounts = list(weekly_spending.values())
        daily_amounts = list(daily_spending.values())
        
        avg_weekly = sum(weekly_amounts) / len(weekly_amounts) if weekly_amounts else 0
        avg_daily = sum(daily_amounts) / len(daily_amounts) if daily_amounts else 0
        
        # Top spending categories
        category_totals = {}
        for category, amounts in category_trends.items():
            category_totals[category] = {
                'total': sum(amounts),
                'average_per_expense': sum(amounts) / len(amounts),
                'count': len(amounts)
            }
        
        # Sort categories by total spending
        top_categories = sorted(category_totals.items(), key=lambda x: x[1]['total'], reverse=True)
        
        client.close()
        
        return json.dumps({
            'analysis_period': '30 days',
            'daily_average': round(avg_daily, 2),
            'weekly_average': round(avg_weekly, 2),
            'total_days_with_expenses': len(daily_spending),
            'top_spending_categories': [
                {
                    'category': cat[0],
                    'total_spent': cat[1]['total'],
                    'average_per_expense': round(cat[1]['average_per_expense'], 2),
                    'expense_count': cat[1]['count']
                }
                for cat in top_categories[:5]
            ],
            'weekly_breakdown': dict(weekly_spending)
        }, indent=2)
    except Exception as e:
        return f"Error analyzing spending trends: {str(e)}"

@mcp.tool(
    name='set_my_budget_alert',
    description="Check if spending exceeds budget limits for the logged-in user"
)
def set_my_budget_alert(
    category: str = Field(description="Category to check budget for"),
    monthly_budget: float = Field(description="Monthly budget limit for this category"),
    period: str = Field(default="month", description="Period: 'week', 'month', or 'year'")
) -> str:
    """Check current spending against budget"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Calculate date range based on period
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=now.weekday())
            budget_amount = monthly_budget / 4  # Approximate weekly budget
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            budget_amount = monthly_budget
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            budget_amount = monthly_budget * 12
        else:
            return "Invalid period. Use 'week', 'month', or 'year'"
        
        # Get expenses for the period and category
        expenses = list(db.expenses.find({
            'user_id': user_id,
            'category': category,
            'date': {'$gte': start_date}
        }))
        client.close()
        
        total_spent = sum(expense['amount'] for expense in expenses)
        remaining_budget = budget_amount - total_spent
        percentage_used = (total_spent / budget_amount * 100) if budget_amount > 0 else 0
        
        status = "OK"
        if percentage_used >= 100:
            status = "OVER BUDGET"
        elif percentage_used >= 80:
            status = "WARNING - Close to limit"
        elif percentage_used >= 60:
            status = "CAUTION - 60% used"
        
        return json.dumps({
            'category': category,
            'period': period,
            'budget_limit': budget_amount,
            'amount_spent': total_spent,
            'remaining_budget': remaining_budget,
            'percentage_used': round(percentage_used, 1),
            'status': status,
            'days_in_period': (now - start_date).days + 1,
            'expense_count': len(expenses)
        }, indent=2)
    except Exception as e:
        return f"Error checking budget: {str(e)}"

@mcp.tool(
    name='get_my_recent_expenses',
    description="Get the most recent expenses for the logged-in user"
)
def get_my_recent_expenses(limit: int = Field(default=5, description="Number of recent expenses to show (1-20)")) -> str:
    """Get the most recent expenses"""
    user_id = require_auth()
    try:
        if limit < 1 or limit > 20:
            return "Limit must be between 1 and 20"
        
        client = get_mongo_client()
        db = client.expenses
        
        expenses = list(db.expenses.find({'user_id': user_id}).sort("date", -1).limit(limit))
        client.close()
        
        if not expenses:
            return "No expenses found."
        
        result = []
        total_amount = 0
        for expense in expenses:
            result.append({
                'id': str(expense['_id']),
                'category': expense['category'],
                'amount': expense['amount'],
                'date': expense['date'].strftime('%Y-%m-%d %H:%M'),
                'description': expense['description']
            })
            total_amount += expense['amount']
        
        return json.dumps({
            'recent_expenses_count': len(result),
            'total_amount_recent': total_amount,
            'expenses': result
        }, indent=2)
    except Exception as e:
        return f"Error retrieving recent expenses: {str(e)}"

@mcp.tool(
    name='duplicate_my_expense',
    description="Duplicate an existing expense for the logged-in user"
)
def duplicate_my_expense(
    expense_id: str = Field(description="ID of expense to duplicate"),
    new_date: typing.Optional[str] = Field(None, description="New date (YYYY-MM-DD), defaults to today"),
    new_amount: typing.Optional[float] = Field(None, description="New amount, defaults to original")
) -> str:
    """Duplicate an existing expense with optional modifications"""
    user_id = require_auth()
    try:
        client = get_mongo_client()
        db = client.expenses
        
        # Get original expense
        original = db.expenses.find_one({'_id': ObjectId(expense_id), 'user_id': user_id})
        if not original:
            client.close()
            return f"No expense found with ID: {expense_id} for this user."
        
        # Create new expense data
        new_expense = {
            'user_id': user_id,
            'category': original['category'],
            'amount': new_amount if new_amount is not None else original['amount'],
            'date': datetime.strptime(new_date, '%Y-%m-%d') if new_date else datetime.now(),
            'description': f"{original['description']} (duplicate)"
        }
        
        result = db.expenses.insert_one(new_expense)
        client.close()
        
        return f"Expense duplicated successfully with new ID: {str(result.inserted_id)}"
    except Exception as e:
        return f"Error duplicating expense: {str(e)}"

if __name__ == "__main__":
    # Get port from environment variable (Render sets PORT automatically)
    mcp.run(transport='streamable-http')
