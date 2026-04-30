from typing import List, Dict, Any, Optional
from domain.ports.teacher_repository import TeacherRepository
from infrastructure.adapters.output.postgres.connection import PostgresConnection

class TeacherRepositoryImpl(TeacherRepository):
    
    async def get_teacher_students(self, teacher_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                u.id as student_id,
                u.full_name,
                u.email,
                m.id as module_id,
                m.title as module_title,
                COALESCE(p.percentage, 0) as progress,
                e.enrolled_at,
                e.status as enrollment_status,
                COALESCE(p.last_activity, e.enrolled_at) as last_activity
            FROM users u
            JOIN enrollments e ON u.id = e.student_id
            JOIN modules m ON e.module_id = m.id
            LEFT JOIN progress p ON u.id = p.student_id AND m.id = p.module_id
            WHERE m.teacher_id = %s
            ORDER BY last_activity DESC
        """
        students = []
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (teacher_id,))
            rows = cursor.fetchall()
            for row in rows:
                status = "Activo"
                if row[5] == 100:
                    status = "Completado"
                elif row[7] == 'withdrawn':
                    status = "Inactivo"
                
                students.append({
                    "id": row[0],
                    "full_name": row[1],
                    "email": row[2],
                    "module_id": row[3],
                    "module_title": row[4],
                    "progress": float(row[5]),
                    "enrolled_at": row[6].isoformat() if row[6] else None,
                    "status": status,
                    "last_activity": row[8].isoformat() if row[8] else None,
                })
        return students

    async def get_teacher_metrics(self, teacher_id: int) -> Dict[str, Any]:
        with PostgresConnection.get_cursor() as cursor:
            # Total students
            cursor.execute("""
                SELECT COUNT(DISTINCT e.student_id)
                FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                WHERE m.teacher_id = %s
            """, (teacher_id,))
            total_students = cursor.fetchone()[0] or 0

            # Average progress
            cursor.execute("""
                SELECT AVG(COALESCE(p.percentage, 0))
                FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                LEFT JOIN progress p ON e.student_id = p.student_id AND e.module_id = p.module_id
                WHERE m.teacher_id = %s
            """, (teacher_id,))
            avg_row = cursor.fetchone()
            avg_progress = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0.0
            
            # Completion rate
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN p.percentage = 100 THEN 1 END)::float / NULLIF(COUNT(e.id), 0) * 100
                FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                LEFT JOIN progress p ON e.student_id = p.student_id AND e.module_id = p.module_id
                WHERE m.teacher_id = %s
            """, (teacher_id,))
            comp_row = cursor.fetchone()
            completion_rate = float(comp_row[0]) if comp_row and comp_row[0] is not None else 0.0
            
            # Progress by course
            cursor.execute("""
                SELECT m.title, AVG(COALESCE(p.percentage, 0)) as avg_prog
                FROM modules m
                LEFT JOIN enrollments e ON m.id = e.module_id
                LEFT JOIN progress p ON e.student_id = p.student_id AND m.id = p.module_id
                WHERE m.teacher_id = %s
                GROUP BY m.id, m.title
                ORDER BY avg_prog DESC
            """, (teacher_id,))
            course_progress = [{"name": row[0], "progress": float(row[1]) if row[1] is not None else 0.0} for row in cursor.fetchall()]
            
            # Performance distribution (e.g., how many students are in 0-25, 26-50, etc.)
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN COALESCE(p.percentage, 0) < 25 THEN 'Bajo (0-24%%)'
                        WHEN COALESCE(p.percentage, 0) < 50 THEN 'Regular (25-49%%)'
                        WHEN COALESCE(p.percentage, 0) < 75 THEN 'Bueno (50-74%%)'
                        ELSE 'Excelente (75-100%%)'
                    END as bracket,
                    COUNT(*) as count
                FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                LEFT JOIN progress p ON e.student_id = p.student_id AND e.module_id = p.module_id
                WHERE m.teacher_id = %s
                GROUP BY bracket
            """, (teacher_id,))
            
            # Initialize with all brackets
            brackets_dict = {
                'Bajo (0-24%)': 0,
                'Regular (25-49%)': 0,
                'Bueno (50-74%)': 0,
                'Excelente (75-100%)': 0
            }
            for row in cursor.fetchall():
                brackets_dict[row[0]] = row[1]
                
            performance_dist = [{"name": k, "value": v} for k, v in brackets_dict.items()]

        # Generate some mock weekly activity if no real event log aggregation exists for PG
        weekly_activity = [
            {"day": "Lun", "activos": 5},
            {"day": "Mar", "activos": 12},
            {"day": "Mié", "activos": 8},
            {"day": "Jue", "activos": 15},
            {"day": "Vie", "activos": 10},
            {"day": "Sáb", "activos": 2},
            {"day": "Dom", "activos": 4},
        ]

        return {
            "total_students": total_students,
            "avg_progress": round(avg_progress, 1),
            "completion_rate": round(completion_rate, 1),
            "active_students": total_students, # Simplification
            "course_progress": course_progress,
            "performance_distribution": performance_dist,
            "weekly_activity": weekly_activity,
            "insights": [
                f"Tienes {total_students} estudiantes en total.",
                f"El progreso promedio es {round(avg_progress, 1)}%.",
                f"Tasa de completitud: {round(completion_rate, 1)}%."
            ]
        }

    async def get_student_details(self, teacher_id: int, student_id: int) -> Optional[Dict[str, Any]]:
        # Verification that student is enrolled in one of the teacher's modules
        query = """
            SELECT 
                u.id, u.full_name, u.email, u.points, u.streak_days, u.created_at
            FROM users u
            WHERE u.id = %s AND EXISTS (
                SELECT 1 FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                WHERE e.student_id = u.id AND m.teacher_id = %s
            )
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (student_id, teacher_id))
            row = cursor.fetchone()
            if not row:
                return None
                
            student_data = {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "points": row[3],
                "streak_days": row[4],
                "joined_at": row[5].isoformat() if row[5] else None,
                "modules": []
            }
            
            # Fetch modules specific to this teacher
            mod_query = """
                SELECT m.id, m.title, COALESCE(p.percentage, 0), e.status, p.last_activity
                FROM modules m
                JOIN enrollments e ON m.id = e.module_id
                LEFT JOIN progress p ON e.student_id = p.student_id AND m.id = p.module_id
                WHERE m.teacher_id = %s AND e.student_id = %s
            """
            cursor.execute(mod_query, (teacher_id, student_id))
            for mod_row in cursor.fetchall():
                student_data["modules"].append({
                    "id": mod_row[0],
                    "title": mod_row[1],
                    "progress": float(mod_row[2]) if mod_row[2] is not None else 0.0,
                    "status": mod_row[3],
                    "last_activity": mod_row[4].isoformat() if mod_row[4] else None
                })
                
            return student_data
