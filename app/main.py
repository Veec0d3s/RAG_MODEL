import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from rag_engine import build_chatbot

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("📄💬 Chat with Your Document")

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
with st.sidebar:
    uploaded_file = st.file_uploader("📎 Upload a document", type=["pdf", "txt"])
    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            st.session_state.chatbot = build_chatbot(file_path)
            st.session_state.messages = []
            st.success("✅ File uploaded, chatbot ready!")
        except Exception as e:
            st.error(f"❌ Failed to build chatbot: {e}")

user_input = st.chat_input("Ask a question about the uploaded document...")

if user_input:
    user_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(user_msg)

    if st.session_state.chatbot:
        try:
            response = st.session_state.chatbot.invoke({
                "question": user_input,
                "chat_history": st.session_state.messages,
            })
            answer = response.get("answer", "🤖 No answer returned.")
            bot_msg = AIMessage(content=answer)
            st.session_state.messages.append(bot_msg)
        except Exception as e:
            st.session_state.messages.append(AIMessage(content=f"❌ Error: {e}"))
    else:
        st.session_state.messages.append(AIMessage(content="⚠️ Upload a document first."))

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

with st.sidebar:
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
