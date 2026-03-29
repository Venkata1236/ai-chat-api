"""
🔗 Chat Chain - LangChain Conversational Chain (v1.0.0 - 2026)
==============================================================
Builds GPT-4o-mini chain with persistent message history per session.
Uses RunnableWithMessageHistory + ChatPromptTemplate with MessagesPlaceholder.
Supports custom system prompts. Streamlit/CLI unified key resolution.
Author: Venkata Reddy (@Venkata1236)
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from chains.memory import get_session_history
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable AI assistant.
You provide clear, accurate, and concise answers.
You remember the conversation history and can refer back to previous messages.
Always be polite and professional."""


def get_api_key():
    try:
        import streamlit as st
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def create_chat_chain(system_prompt: str = None):
    """
    Creates a LangChain chat chain with message history.
    Returns a RunnableWithMessageHistory.
    """
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=get_api_key()
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt or DEFAULT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    return chain_with_history


def run_chat(
    session_id: str,
    message: str,
    system_prompt: str = None
) -> str:
    """
    Runs one turn of the chat chain.
    Returns AI response as string.
    """
    chain = create_chat_chain(system_prompt)

    response = chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )

    return response.content