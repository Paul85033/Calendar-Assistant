from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.api.auth import get_auth_url, exchange_code_for_tokens
from app.agent.lagent import run_agent
from app.schema.chat import ChatRequest, ChatResponse
from app.func.config import STREAMLIT_URL
import traceback

router = APIRouter()

@router.get("/auth/google")
def auth_redirect():
    return RedirectResponse(url=get_auth_url())

@router.get("/auth/google/callback")
def auth_callback(request: Request):
    code = request.query_params.get("code")
    try:
        tokens = exchange_code_for_tokens(code)
        access_token = tokens["access_token"]
        return RedirectResponse(url=f"{STREAMLIT_URL}?access_token={access_token}")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@router.post("/chat",response_model=ChatResponse)
async def chat(request: Request):
    try:
        payload = await request.json()  
        user_input = payload.get("message")
        access_token = payload.get("access_token")

        if not user_input or not access_token:
            return JSONResponse(content={"error": "Missing message or access_token"}, status_code=400)

        state = run_agent({"user_input": user_input, "access_token": access_token})
        return JSONResponse(content={"response": state.get("bot_reply")})
    except Exception as e:
        print("Exception in /chat route:", e)
        traceback.print_exc()  
        return JSONResponse(content={"error": str(e)}, status_code=500)