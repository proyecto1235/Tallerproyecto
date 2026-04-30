from typing import List, Optional
from datetime import datetime
from domain.entities.enrollment import Enrollment
from domain.ports.enrollment_repository import EnrollmentRepository
from infrastructure.adapters.output.postgres.connection import PostgresConnection

class EnrollmentRepositoryImpl(EnrollmentRepository):
    
    async def create(self, enrollment: Enrollment) -> Enrollment:
        query = """
            INSERT INTO enrollments (student_id, module_id, status)
            VALUES (%s, %s, %s)
            RETURNING id, enrolled_at, completed_at
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(
                query,
                (enrollment.student_id, enrollment.module_id, enrollment.status)
            )
            result = cursor.fetchone()
            enrollment.id = result[0]
            enrollment.enrolled_at = result[1]
            enrollment.completed_at = result[2]
            return enrollment
            
    async def get_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        query = "SELECT id, student_id, module_id, status, enrolled_at, completed_at FROM enrollments WHERE id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (enrollment_id,))
            row = cursor.fetchone()
            if row:
                return Enrollment(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    status=row[3],
                    enrolled_at=row[4],
                    completed_at=row[5]
                )
        return None

    async def get_by_student_and_module(self, student_id: int, module_id: int) -> Optional[Enrollment]:
        query = "SELECT id, student_id, module_id, status, enrolled_at, completed_at FROM enrollments WHERE student_id = %s AND module_id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (student_id, module_id))
            row = cursor.fetchone()
            if row:
                return Enrollment(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    status=row[3],
                    enrolled_at=row[4],
                    completed_at=row[5]
                )
        return None

    async def get_by_student(self, student_id: int) -> List[Enrollment]:
        query = "SELECT id, student_id, module_id, status, enrolled_at, completed_at FROM enrollments WHERE student_id = %s ORDER BY enrolled_at DESC"
        enrollments = []
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (student_id,))
            rows = cursor.fetchall()
            for row in rows:
                enrollments.append(Enrollment(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    status=row[3],
                    enrolled_at=row[4],
                    completed_at=row[5]
                ))
        return enrollments

    async def get_by_module(self, module_id: int) -> List[Enrollment]:
        query = "SELECT id, student_id, module_id, status, enrolled_at, completed_at FROM enrollments WHERE module_id = %s"
        enrollments = []
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (module_id,))
            rows = cursor.fetchall()
            for row in rows:
                enrollments.append(Enrollment(
                    id=row[0],
                    student_id=row[1],
                    module_id=row[2],
                    status=row[3],
                    enrolled_at=row[4],
                    completed_at=row[5]
                ))
        return enrollments

    async def update(self, enrollment: Enrollment) -> Enrollment:
        query = """
            UPDATE enrollments 
            SET status = %s, completed_at = %s
            WHERE id = %s
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(
                query,
                (enrollment.status, enrollment.completed_at, enrollment.id)
            )
        return enrollment

    async def delete(self, enrollment_id: int) -> bool:
        query = "DELETE FROM enrollments WHERE id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (enrollment_id,))
            return cursor.rowcount > 0
