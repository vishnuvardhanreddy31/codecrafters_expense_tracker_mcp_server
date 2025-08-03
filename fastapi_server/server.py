import os
import sys
import contextlib
from fastapi import FastAPI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_servers.expense_tracker import mcp as expense_tracker_mcp
from mcp_servers.eval_expression import mcp as exp_eval_mcp
from mcp_servers.weather_mcp import mcp as weather_mcp

# Create the SSE apps first to initialize session managers
expense_tracker_sse_app = expense_tracker_mcp.sse_app()
exp_eval_sse_app = exp_eval_mcp.sse_app()
weather_sse_app = weather_mcp.sse_app()

@contextlib.asynccontextmanager
async def lifespan(app :FastAPI):
  # SSE apps handle their own lifecycle, no need for manual session management
  yield
    
app = FastAPI(lifespan=lifespan)
app.mount("/expense_tracker", expense_tracker_sse_app)
app.mount("/exp_eval", exp_eval_sse_app)
app.mount("/weather", weather_sse_app)

if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host='0.0.0.0',port = 8000)
