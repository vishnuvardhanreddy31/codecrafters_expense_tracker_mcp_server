from mcp.server.fastmcp import FastMCP
from pydantic import Field



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

