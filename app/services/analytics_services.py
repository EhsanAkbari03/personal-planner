
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.repositories.analytics_repository import AnalyticsRepository


TEHRAN = ZoneInfo("Asia/Tehran")

PERSIAN_DAYS = {
    0: "ش",  # دوشنبه
    1: "ی",  # سه‌شنبه
    2: "د",  # چهارشنبه
    3: "س",  # پنجشنبه
    4: "چ",  # جمعه
    5: "پ",  # شنبه
    6: "ج",  # یکشنبه
}


class AnalyticsService:
    def __init__(self, db):
        self.repository = AnalyticsRepository(db)

    def get_weekly_analytics(self, user_id: int):
        # تاریخ امروز بر اساس ساعت تهران
        today = datetime.now(TEHRAN).date()

        # بازه هفت روز اخیر، شامل امروز
        start_date = today - timedelta(days=6)

        # ------------------------------------------
        # 1. آمار تسک‌های هفتگی
        # ------------------------------------------
        task_rows = self.repository.get_weekly_task_stats(
            user_id,
            start_date,
            today,
        )

        tasks_by_date = {
            row[0]: {
                "total": row[1],
                "completed": row[2],
            }
            for row in task_rows
        }

        # مجموع تسک‌های ایجادشده در بازه هفتگی
        weekly_task_count = sum(
            item["total"]
            for item in tasks_by_date.values()
        )

        # ------------------------------------------
        # 2. پیشرفت روزانه تسک‌ها
        # ------------------------------------------
        weekly_progress = []

        for offset in range(7):
            current_date = start_date + timedelta(days=offset)

            stats = tasks_by_date.get(
                current_date,
                {
                    "total": 0,
                    "completed": 0,
                },
            )

            total = stats["total"]
            completed = stats["completed"]

            progress = (
                round(completed / total * 100)
                if total > 0
                else 0
            )

            # اگر تاریخ مربوط به امروز باشد، «امروز» نمایش داده می‌شود
            day_label = (
                "امروز"
                if current_date == today
                else PERSIAN_DAYS[current_date.weekday()]
            )

            weekly_progress.append({
                "date": current_date.isoformat(),
                "day": day_label,
                "progress": progress,
            })

        # ------------------------------------------
        # 3. درصد موفقیت عادت‌ها
        # ------------------------------------------
        log_stats = self.repository.get_habit_log_stats(
            user_id,
            start_date,
            today,
        )

        completed_logs = log_stats[0] or 0
        missed_logs = log_stats[1] or 0

        total_logs = completed_logs + missed_logs

        success_rate = (
            round(completed_logs / total_logs * 100)
            if total_logs > 0
            else 0
        )

        # ------------------------------------------
        # 4. پیشرفت هر عادت
        # ------------------------------------------
        habit_rows = self.repository.get_habits_progress(
            user_id,
            start_date,
            today,
        )

        habits = []

        for row in habit_rows:
            habit_id, title, streak, total, completed = row

            progress = (
                round(completed / total * 100)
                if total > 0
                else 0
            )

            habits.append({
                "id": habit_id,
                "name": title,
                "progress": progress,
                "streak_count": streak,
            })

        # ------------------------------------------
        # 5. خروجی نهایی API
        # ------------------------------------------
        return {
            "success_rate": success_rate,
            "weekly_task_count": weekly_task_count,
            "weekly_progress": weekly_progress,
            "habits": habits,
        }
