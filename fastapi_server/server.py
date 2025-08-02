import os
import sys
import contextlib
from fastapi import FastAPI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_servers.expense_tracker import mcp as expense_tracker_mcp
from mcp_servers.eval_expression import mcp as exp_eval_mcp

@contextlib.asynccontextmanager
async def lifespan(app :FastAPI):
  async with contextlib.AsyncExitStack() as stack:
    await stack.enter_async_context(expense_tracker_mcp.session_manager.run())
    await stack.enter_async_context(exp_eval_mcp.session_manager.run())
    yield
    
app = FastAPI(lifespan=lifespan)
app.mount("/expense_tracker",expense_tracker_mcp.streamable_http_app())
app.mount("/exp_eval",exp_eval_mcp.streamable_http_app())

if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host='0.0.0.0',port = 8000)
