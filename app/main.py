from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.llm2 import chat_with_llm
from app.services.user_services import UserService
from app.services.task_services import TaskService
from app.services.habit_log_services import HabitLogService
from datetime import date
from app.database.connection import get_db
from app.services.password_reset_services import PasswordResetService

app = FastAPI()

# 🌟 فیلد تاریخ (start_at) به مدل اضافه شد
class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    status: str
    start_at: str | None = None 

@app.get("/")
def home():
    return {"message": "Planner API is running"}

@app.post("/chat")
def chat(user_message: str, user_id: int):
    print("========== CHAT START ==========")
    print("User message:", user_message)
    print("Calling Gemini...")
    try:
        response = chat_with_llm(user_message, user_id)
        print("Gemini response received!")
        return {"response": response}
    except Exception as e:
        print(f"Error in /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
def get_user_tasks(user_id: int, date: str | None = None):
    task_service = TaskService()
    try:
        tasks = task_service.get_today_tasks(user_id) 
        return {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "start_at": t.start_at.isoformat() if t.start_at else None,
                    "status": t.status
                }
                for t in tasks
            ]
        }
    except Exception as e:
        print(f"Error in /tasks: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        task_service.repository.db.close()

@app.delete("/tasks/{task_id}")
def delete_task_endpoint(task_id: int, user_id: int):
    task_service = TaskService()
    try:
        success = task_service.delete_task(task_id=task_id, user_id=user_id)
        return {"success": success}
    finally:
        task_service.repository.db.close()

@app.put("/tasks/{task_id}")
def update_task_endpoint(task_id: int, payload: TaskUpdate):
    task_service = TaskService()
    try:
        success = task_service.update_task(
            task_id=task_id, 
            title=payload.title, 
            description=payload.description, 
            status=payload.status,
            start_at=payload.start_at # 🌟 پاس دادن تاریخ جدید به سرویس
        )
        return {"success": success}
    finally:
        task_service.repository.db.close()

@app.post("/signup")
def signup(username: str | None, email: str | None, password: str, timezone: str = "Asia/Tehran"):
    user_service = UserService()
    try:
        user = user_service.create_user(username=username, email=email, password=password, timezone=timezone)
        return {
            "message": "User created successfully",
            "user": {
                "id": user.id, "username": user.username, "email": user.email,
                "timezone": user.timezone, "created_at": user.created_at, "updated_at": user.updated_at,
                "subscription_level": user.subscription_level,
                "active_days_streak": user.active_days_streak,
                "profile_image_uri": user.profile_image_uri
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        user_service.repository.db.close()

@app.post("/login")
def login(email: str, password: str):
    user_service = UserService()
    try:
        user = user_service.login(email=email, password=password)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {
            "message": "Login successful",
            "user": {
                "id": user.id, "username": user.username, "email": user.email,
                "timezone": user.timezone, "created_at": user.created_at, "updated_at": user.updated_at,
                "subscription_level": user.subscription_level,
                "active_days_streak": user.active_days_streak,
                "profile_image_uri": user.profile_image_uri,
                "last_login_date": str(user.last_login_date) if user.last_login_date else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        user_service.repository.db.close()


@app.get("/profile/{user_id}")
def get_user_profile(user_id: int):
    user_service = UserService()
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db = user_service.repository.db
    
    # 🌟 آپدیت خودکار تاریخ آخرین ورود و روزهای فعال با هر بار باز شدن برنامه و دریافت پروفایل
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET active_days_streak = CASE 
                    WHEN last_login_date = CURRENT_DATE - 1 THEN active_days_streak + 1
                    WHEN last_login_date = CURRENT_DATE THEN active_days_streak
                    ELSE 1 
                END,
                last_login_date = CURRENT_DATE
                WHERE id = %s;
            """, (user_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating login streak: {e}")

    # شمارش زنده تعداد تسک‌های تکمیل شده این کاربر
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s AND status = 'completed';", (user_id,))
        completed_tasks = cursor.fetchone()[0]
        
    # گرفتن عادت‌های این کاربر و تبدیل تاریخ به True/False
    # گرفتن عادت‌های این کاربر به همراه روزها و ساعت برای تقویم اندروید
    with db.cursor() as cursor:
        query = """
            SELECT id, title, streak_count, 
                   (last_completed_date = CURRENT_DATE) AS is_completed_today,
                   weekdays, checkin_time
            FROM habits 
            WHERE user_id = %s;
        """
        cursor.execute(query, (user_id,))
        habits_rows = cursor.fetchall()
        habits = [{
            "id": r[0], 
            "title": r[1], 
            "streak_count": r[2], 
            "is_completed_today": bool(r[3]),
            "weekdays": r[4] if r[4] else [], # آرایه‌ای از روزها [0, 2, 4]
            "reminder_time": str(r[5]) if r[5] else "08:00" # ساعت اجرا
        } for r in habits_rows]

    # گرفتن اطلاعات جدید و آپدیت‌شده کاربر از دیتابیس
    updated_user = user_service.get_user(user_id)
    user_service.repository.db.close()

    return {
        "name": updated_user.username or "کاربر هابیتو",
        "email": updated_user.email,
        "profile_image_uri": updated_user.profile_image_uri,
        "subscription_level": updated_user.subscription_level,
        "active_days_streak": updated_user.active_days_streak,
        "completed_tasks_count": completed_tasks,
        "habits": habits
    }


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
    finally:
        user_services.repository.db.close()
    

@app.post("/habits/{habit_id}/complete")
def complete_habit(habit_id: int, user_id: int):
    user_service = UserService()
    db = user_service.repository.db
    try:
        with db.cursor() as cursor:
            # بررسی اینکه آیا امروز انجام شده است؟
            cursor.execute("SELECT (last_completed_date = CURRENT_DATE) FROM habits WHERE id = %s AND user_id = %s;", (habit_id, user_id))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Habit not found")
            
            if row[0] is True:
                return {"message": "Already completed today"}
            
            # آپدیت Streak و تاریخ آخرین انجام به امروز
            cursor.execute("""
                UPDATE habits 
                SET streak_count = streak_count + 1, last_completed_date = CURRENT_DATE
                WHERE id = %s AND user_id = %s;
            """, (habit_id, user_id))
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


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
    email: str
):

    db = get_db()

    service = PasswordResetService(db)

    try:
        return service.send_code(
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