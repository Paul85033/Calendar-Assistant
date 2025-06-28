import streamlit as st
import requests
from datetime import datetime, timezone
import json
from config import BACKEND_URL, AUTH_URL


query_params = st.query_params
if "access_token" in query_params and "access_token" not in st.session_state:
    st.session_state.access_token = query_params["access_token"]
    st.rerun()

st.set_page_config(page_title="Calendar Assistant", layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>Calendar Assistant</h1>",
    unsafe_allow_html=True
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "access_token" not in st.session_state:
    st.session_state.access_token = ""

if "booking_history" not in st.session_state:
    st.session_state.booking_history = []

if "google_logged_in" not in st.session_state:
    st.session_state.google_logged_in = False

with st.sidebar:
    st.header("Google Calendar Login")
    
    if not st.session_state.access_token:
        if st.button("Connect Google Calendar"):
            st.markdown(f"[Click here to login with Google]({AUTH_URL})", unsafe_allow_html=True)
    else:
        st.success("Connected to Google Calendar")
    
    st.divider()
    st.header("Booking History")
    if st.session_state.booking_history:
        for event in st.session_state.booking_history:
            st.markdown(
                f"**{event['summary']}**  \n{event['start']} → {event['end']}",
                unsafe_allow_html=True,
            )
    else:
        st.info("No bookings yet.")

st.markdown("""
<style>
.chat-container {
    max-width: 800px;
    margin: 0 auto;
}

.chat-message {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 0.5rem;
    max-width: 80%;
}

.user-message {
    background-color: black;
    color: white;
    margin-left: auto;
    text-align: right;
    font-size: 1.2rem;
}

.bot-message {
    background-color: grey;
    color: black;
    margin-right: auto;
    font-size: 1.2rem;
}

.stChatInput > div > div > div > div {
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

chat_container = st.container()

with chat_container:
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'''
            <div class="chat-message user-message">
                {message}
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-message bot-message">
                {message}
            </div>
            ''', unsafe_allow_html=True)

user_input = st.chat_input("Ask me to book a meeting...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    
    if not st.session_state.access_token:
        st.session_state.chat_history.append(("bot", "Please connect your Google Calendar first."))
    else:
        try:
            with st.spinner("Processing your request..."):
                res = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "message": user_input,
                        "access_token": st.session_state.access_token
                    },
                    timeout=30  
                )
                res.raise_for_status()
                result = res.json()
                
                reply = result.get("response", "Something went wrong.")
                st.session_state.chat_history.append(("bot", reply))
                if "booked" in reply.lower() and "http" in reply:
                    now = datetime.now(timezone.utc).isoformat().replace("+00:00")
                    st.session_state.booking_history.append({
                        "summary": user_input,
                        "start": now,
                        "end": now
                    })
                
                print("Reply from server:", reply)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection Error: Unable to reach backend server. {str(e)}"
            st.session_state.chat_history.append(("bot", error_msg))
            print(f"Request error: {e}")
        except json.JSONDecodeError as e:
            error_msg = f"Response Error: Invalid response from server."
            st.session_state.chat_history.append(("bot", error_msg))
            print(f"JSON decode error: {e}")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.chat_history.append(("bot", error_msg))
            print(f"General error: {e}")
    
    st.rerun()