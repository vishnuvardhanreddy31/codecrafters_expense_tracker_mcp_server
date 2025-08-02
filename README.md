# Expense Tracker MCP Server

An MCP (Model Context Protocol) server for expense tracking with user authentication and comprehensive expense management tools.

## Features

- **User Authentication**: Register, login, and logout functionality
- **Expense Management**: Add, view, update, and delete expenses
- **Smart Tools**: Natural language expense adding, budget alerts, trend analysis
- **Multi-user Support**: Each user only sees and manages their own expenses
- **Data Visualization**: Summaries, reports, and trends analysis

## Setup

### Prerequisites

- Python 3.11+
- MongoDB Atlas account (or local MongoDB instance)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/vishnuvardhanreddy31/codecrafters_expense_tracker_mcp_server.git
   cd codecrafters_expense_tracker_mcp_server
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your MongoDB connection string:

   ```
   MONGO_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/expenses
   ```

4. Run the server:
   ```bash
   python main.py
   ```

## Deployment on Render

1. Create a new Web Service on Render
2. Link your GitHub repository
3. Use the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment Variables**: Add `MONGO_URI` with your MongoDB connection string

## Using with Cline

Add the MCP server configuration to Cline's settings.json:

```json
{
  "cline.mcpServers": {
    "expense-tracker": {
      "command": "python",
      "args": ["-u", "path/to/main.py"],
      "env": {}
    }
  }
}
```

## Available Tools

### Authentication

| Tool       | Description                                    |
| ---------- | ---------------------------------------------- |
| `register` | Register a new user with username and password |
| `login`    | Log in with username and password              |
| `logout`   | Log out the current user                       |

### Core Expense Operations

| Tool                   | Description                              |
| ---------------------- | ---------------------------------------- |
| `add_expense`          | Add a new expense for the logged-in user |
| `get_my_expenses`      | Get all expenses for the logged-in user  |
| `get_my_expense_by_id` | Get a specific expense by ID             |
| `update_my_expense`    | Update an existing expense               |
| `delete_my_expense`    | Delete an expense                        |

### Reports and Analysis

| Tool                          | Description                       |
| ----------------------------- | --------------------------------- |
| `get_my_expenses_by_category` | Get expenses filtered by category |
| `get_my_monthly_report`       | Generate a monthly expense report |
| `get_my_expense_summary`      | Get summary with category totals  |
| `get_my_week_summary`         | Current week's expense summary    |
| `get_my_spending_trends`      | Analyze 30-day spending patterns  |

### Practical Utilities

| Tool                     | Description                                               |
| ------------------------ | --------------------------------------------------------- |
| `quick_add_expense`      | Add expense using natural language (e.g., "coffee $5.50") |
| `get_my_today_expenses`  | See today's expenses                                      |
| `get_my_recent_expenses` | View recent expenses                                      |
| `find_my_expenses`       | Search with flexible criteria                             |
| `set_my_budget_alert`    | Check spending against budget                             |
| `duplicate_my_expense`   | Copy existing expenses with modifications                 |

## Example Usage

### Adding an Expense

```
User: Add a new expense for lunch today that cost $15
AI: I'll help you add that expense. Let me log you in first.
User: My username is john and password is pass123
AI: Logged in as john. I'll add your expense now.
    Expense added for john with ID: 64f7a1b3e4b0a2c5d6e7f8g9
```

### Getting Expense Summary

```
User: Show me my spending summary for this month
AI: Here's your expense summary for August 2025:
    Total expenses: 15
    Total amount: $523.45
    Top categories:
    - Food: $203.50 (38.9%)
    - Transport: $145.20 (27.7%)
    - Entertainment: $95.75 (18.3%)
```

## Author

CodeCrafter

## Contact

For questions or support, please open an issue on GitHub.
