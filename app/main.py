from fastapi import FastAPI
from app.llm import chat_with_llm

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Planner API is running"
    }


@app.post("/chat")
def chat(user_message: str):

    response = chat_with_llm(user_message)

    return {
        "response": response
    }