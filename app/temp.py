import sys
from datetime import datetime
from app.services.task_services import TaskService  # مسیر فایل TaskService خود را وارد کنید


def run_manual_test():
    # ۱. نمونه‌سازی از سرویس
    service = TaskService()

    # ۲. تعریف داده‌های تست
    test_user_id = 2
    test_date = "2026-09-12"

    print(f"--- شروع تست تابع get_tasks_by_date برای کاربر {test_user_id} و تاریخ {test_date} ---")

    try:
        # ۳. فراخوانی تابع
        tasks = service.get_tasks_by_date(date=test_date, user_id=test_user_id)

        # ۴. بررسی و چاپ خروجی
        print(f"تعداد تسک‌های یافت شده: {len(tasks)}")
        for idx, task in enumerate(tasks, start=1):
            print(f"\nتسک #{idx}:")
            print(f"  - شناسه: {getattr(task, 'id', 'N/A')}")
            print(f"  - عنوان: {getattr(task, 'title', 'N/A')}")
            print(f"  - زمان شروع: {getattr(task, 'start_at', 'N/A')}")
            print(f"  - وضعیت: {getattr(task, 'status', 'N/A')}")

    except ValueError as ve:
        print(f"❌ خطای اعتبارسنجی ورودی: {ve}")
    except Exception as e:
        print(f"❌ خطای غیرمنتظره در زمان اجرا: {e}")

    # ۵. تست حالت‌های استثنا (Validation Edge Cases)
    print("\n--- تست ورودی‌های نامعتبر (اعتبارسنجی) ---")
    try:
        service.get_tasks_by_date(date=test_date, user_id=-1)
    except ValueError as ve:
        print(f"✅ تست user_id نامعتبر با موفقیت Pass شد: {ve}")


if __name__ == "__main__":
    run_manual_test()