from app.models.task import Task

class TaskRepository:

    def __init__(self, db):
        self.db = db

    def create(self, task: Task) -> Task:
        query = """
            INSERT INTO tasks (
                user_id,
                title,
                description,
                start_at,
                end_at,
                priority,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        values = (
            task.user_id,
            task.title,
            task.description,
            task.start_at,
            task.end_at,
            task.priority,
            task.status
        )
        with self.db.cursor() as cursor:
            cursor.execute(query, values)
            task.id = cursor.fetchone()[0]

        self.db.commit()
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        query = """
            SELECT
                id,
                user_id,
                title,
                description,
                start_at,
                end_at,
                priority,
                status
            FROM tasks
            WHERE id = %s;
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (task_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return Task(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            start_at=row[4],
            end_at=row[5],
            priority=row[6],
            status=row[7]
        )

    def delete(self, task_id: int, user_id: int) -> bool:
        query = """
            DELETE FROM tasks
            WHERE id = %s
            AND user_id = %s;
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (task_id, user_id))
            deleted = cursor.rowcount > 0

        self.db.commit()
        return deleted
    
    def get_tasks(self, user_id: int, date: str | None = None) -> list[Task]:
        # اگر تاریخی پاس داده شده باشد، فقط تسک‌های همان بازه زمانی روز فیلتر می‌شوند
        if date:
            date_only = date.split(" ")[0].strip()
            start_of_day = f"{date_only} 00:00:00"
            end_of_day = f"{date_only} 23:59:59"
            
            query = """
                SELECT
                    id, user_id, title, description,
                    start_at, end_at, priority, status
                FROM tasks
                WHERE user_id = %s
                  AND start_at >= %s
                  AND start_at <= %s
                ORDER BY start_at ASC;
            """
            params = (user_id, start_of_day, end_of_day)
        else:
            # اگر تاریخی ارسال نشود (لحظه ورود به برنامه)، تمام تسک‌های کاربر واکشی می‌شوند
            query = """
                SELECT
                    id, user_id, title, description,
                    start_at, end_at, priority, status
                FROM tasks
                WHERE user_id = %s
                ORDER BY start_at ASC;
            """
            params = (user_id,)

        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [
            Task(
                id=row[0],
                user_id=row[1],
                title=row[2],
                description=row[3],
                start_at=row[4],
                end_at=row[5],
                priority=row[6],
                status=row[7]
            )
            for row in rows
        ]

    # برای اینکه توابع قبلی پروژه کرش نکنند، این متدها را به عنوان متد کمکی نگه می‌داریم:
    def get_tasks_by_date(self, date: str, user_id: int) -> list[Task]:
        return self.get_tasks(user_id=user_id, date=date)

    def get_today_tasks(self, user_id: int) -> list[Task]:
        return self.get_tasks(user_id=user_id)

    def find_by_title(self, title: str, user_id: int) -> list[Task]:
        query = """
            SELECT
                id,
                user_id,
                title,
                description,
                start_at,
                end_at,
                priority,
                status
            FROM tasks
            WHERE user_id = %s
              AND title ILIKE %s
            ORDER BY start_at ASC;
        """
        search_title = f"%{title}%"
        with self.db.cursor() as cursor:
            cursor.execute(query, (user_id, search_title))
            rows = cursor.fetchall()

        return [
            Task(
                id=row[0],
                user_id=row[1],
                title=row[2],
                description=row[3],
                start_at=row[4],
                end_at=row[5],
                priority=row[6],
                status=row[7]
            )
            for row in rows
        ]

    def update(self, task: Task) -> bool:
        # 🌟 ستون start_at به کوئری آپدیت اضافه شد تا زمانِ جدید روی دیتابیس بنشیند
        query = """
            UPDATE tasks
            SET title = %s, description = %s, status = %s, start_at = %s
            WHERE id = %s;
        """
        with self.db.cursor() as cursor:
            cursor.execute(query, (task.title, task.description, task.status, task.start_at, task.id))
            updated = cursor.rowcount > 0

        self.db.commit()
        return updated