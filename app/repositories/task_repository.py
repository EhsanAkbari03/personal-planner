from app.models.task import Task


class TaskRepository:

    def __init__(self, db):
        self.db = db

    # ==========================================
    # CREATE
    # ==========================================

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

    # ==========================================
    # GET BY ID
    # ==========================================

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
            AND user_id = %s;
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

    # ==========================================
    # DELETE
    # ==========================================

    def delete(self, task_id: int, user_id: int) -> bool:

        query = """
            DELETE FROM tasks
            WHERE id = %s
            AND user_id = %s;
        """

        with self.db.cursor() as cursor:

            cursor.execute(query, (task_id,user_id))

            deleted = cursor.rowcount > 0

        self.db.commit()

        return deleted

    def get_today_tasks(self, user_id: int):
        query = """
            SELECT
                id,
                user_id,
                title,
                description,
                start_at,
                end_at,
                priority,
                status,
                created_at
            FROM tasks
            WHERE user_id = %s
            AND start_at >= CURRENT_DATE
            AND start_at < CURRENT_DATE + INTERVAL '1 day'
            ORDER BY start_at ASC;
        """

        cursor = self.db.cursor()

        cursor.execute(
            query,
            (user_id,)
        )

        rows = cursor.fetchall()

        cursor.close()

        tasks = []

        for row in rows:
            tasks.append(
                Task(
                    id=row[0],
                    user_id=row[1],
                    title=row[2],
                    description=row[3],
                    start_at=row[4],
                    end_at=row[5],
                    priority=row[6],
                    status=row[7],
                    created_at=row[8]
                )
            )

        return tasks

    def find_by_title(
        self,
        title: str,
        user_id: int
    ) -> list[Task]:

        query = """
            SELECT
                id,
                user_id,
                title,
                description,
                start_at,
                end_at,
                priority,
                status,
                created_at
            FROM tasks
            WHERE user_id = %s
              AND title ILIKE %s
            ORDER BY start_at ASC;
        """

        # %title% برای جستجوی بخشی از عنوان
        search_title = f"%{title}%"

        with self.db.cursor() as cursor:
            cursor.execute(
                query,
                (user_id, search_title)
            )
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
                status=row[7],
                created_at=row[8]
            )
            for row in rows
        ]