from fastapi import FastAPI , HTTPException
from app.llm2 import chat_with_llm
from app.services.user_services import UserService
from app.services.habit_log_services import HabitLogService
from datetime import date
from app.database.connection import get_db
from app.services.password_reset_services import PasswordResetService


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

@app.post("/change-password")
def change_password(user_id: int, old_password: str, new_password: str):
    user_services = UserService()
    try:
        return user_services.change_password(
            user_id,
            old_password,
            new_password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



@app.post("/create_habit_log")
def create_habit_log(
    habit_id: int,
    scheduled_date: date,
    status: str
):

    db = get_db()

    service = HabitLogService(db)

    try:

        result = service.create_log(
            habit_id=habit_id,
            scheduled_date=scheduled_date,
            status=status
        )

        return {
            "success": True,
            "message": "Habit log created successfully",
            "habit_log": {
                "id": result[0],
                "habit_id": result[1],
                "scheduled_date": result[2],
                "status": result[3],
                "points_earned": result[4]
            }
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    
@app.post("/forgot-password")
def forgot_password(
    user_id: int,
    email: str
):

    db = get_db()

    service = PasswordResetService(db)

    try:
        return service.send_code(
            user_id=user_id,
            email=email
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/verify-reset-code")
def verify_reset_code(email: str, code: str):

    db = get_db()
    service = PasswordResetService(db)

    try:
        return service.verify_code(
            email=email,
            code=code
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/reset-password")
def reset_password(
    reset_token: str,
    new_password: str
):

    db = get_db()
    service = PasswordResetService(db)

    try:
        return service.reset_password(
            reset_token=reset_token,
            new_password=new_password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )