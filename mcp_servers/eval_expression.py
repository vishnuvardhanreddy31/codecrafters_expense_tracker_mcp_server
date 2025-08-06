from mcp.server.fastmcp import FastMCP
from pydantic import Field
import datetime
import pytz



mcp = FastMCP("expression_evaluator")


@mcp.tool(
  name = 'calculator',
  description= "Tool to evaluate mathemetical expressions"
)
def evaluate_expression(math_exp : str) -> float:
  """ Evaluate given mathematics expression and returns the result"""
  
  if not math_exp:
    raise ValueError(f"Provide any expression to evaluate")
  return eval(math_exp)

@mcp.tool(
  name='date_time',
  description="Get current date and time in IST (Indian Standard Time)"
)
def date_time() -> str:
  """Get current date and time in IST"""
  
  # Get current time in IST
  ist = pytz.timezone('Asia/Kolkata')
  now_ist = datetime.datetime.now(ist)
  
  return now_ist.strftime("%A, %B %d, %Y at %I:%M:%S %p IST")

