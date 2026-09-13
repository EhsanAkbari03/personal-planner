from fastapi import FastAPI , HTTPException
from app.llm2 import chat_with_llm
from app.services.user_services import UserService


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Planner API is running"
    }


@app.post("/chat")
def chat(user_message: str, user_id: int):
    print("========== CHAT START ==========")
    print("User message:", user_message)

    print("Calling LLM...")

    response = chat_with_llm(user_message, user_id)

    print("LLM response received!")

    return {
      #  "response": response.text
        "response": response
    }


@app.post("/signup")
def signup(
    username: str | None,
    email: str | None,
    password: str,
    timezone: str = "Asia/Tehran"
):
    user_service = UserService()

    try:
        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
            timezone=timezone
        )

        return {
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "timezone": user.timezone,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/login")
def login(email: str, password: str):
    user_service = UserService()

    try:
        user = user_service.login(email=email, password=password)

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "timezone": user.timezone,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )