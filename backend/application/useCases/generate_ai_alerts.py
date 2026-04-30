from typing import List, Dict, Any
import datetime
import uuid
from domain.entities.alert import Alert, AlertType, AlertPriority
from domain.ports.teacher_repository import TeacherRepository

class GenerateAIAlertsUseCase:
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    async def execute(self, teacher_id: int) -> Dict[str, Any]:
        try:
            # 1. Obtener datos reales de los estudiantes del profesor
            students = await self.teacher_repository.get_teacher_students(teacher_id)
            
            if not students:
                return {"success": True, "alerts": []}

            alerts: List[Alert] = []
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # Agrupar estudiantes por módulo para calcular promedios de grupo
            modules_data = {}
            for s in students:
                mod_id = s.get("module_id")
                if not mod_id:
                    continue
                if mod_id not in modules_data:
                    modules_data[mod_id] = {
                        "module_title": s.get("module_title"),
                        "students": [],
                        "total_progress": 0,
                        "total_days": 0
                    }
                
                enrolled_str = s.get("enrolled_at")
                days_enrolled = 1
                if enrolled_str:
                    try:
                        # Handle strings like '2023-10-10T12:00:00+00:00'
                        enrolled_date = datetime.datetime.fromisoformat(enrolled_str.replace("Z", "+00:00"))
                        if enrolled_date.tzinfo is None:
                            enrolled_date = enrolled_date.replace(tzinfo=datetime.timezone.utc)
                        delta = now - enrolled_date
                        days_enrolled = max(1, delta.days)
                    except Exception:
                        pass
                
                progress = s.get("progress", 0)
                
                student_data = {
                    "student_id": s.get("student_id") or s.get("id"),
                    "full_name": s.get("full_name"),
                    "progress": progress,
                    "days_enrolled": days_enrolled,
                    "progress_velocity": progress / days_enrolled if days_enrolled > 0 else 0
                }
                
                modules_data[mod_id]["students"].append(student_data)
                modules_data[mod_id]["total_progress"] += progress
                modules_data[mod_id]["total_days"] += days_enrolled
                
            # 2. Generar alertas basadas en umbrales dinámicos (comparar contra promedio)
            for mod_id, data in modules_data.items():
                mod_title = data["module_title"]
                mod_students = data["students"]
                num_students = len(mod_students)
                
                if num_students == 0:
                    continue
                    
                avg_progress = data["total_progress"] / num_students
                avg_velocity = sum(s["progress_velocity"] for s in mod_students) / num_students
                
                # Para dificultad de clase
                low_progress_count = sum(1 for s in mod_students if s["progress"] < avg_progress * 0.5)
                if num_students >= 3 and low_progress_count / num_students >= 0.4:
                    alerts.append(Alert(
                        id=str(uuid.uuid4()),
                        teacher_id=teacher_id,
                        module_id=mod_id,
                        type=AlertType.DIFFICULTY,
                        priority=AlertPriority.HIGH,
                        message=f"El {round((low_progress_count/num_students)*100)}% de la clase tiene dificultades en el módulo.",
                        recommendations=[
                            "Revisar si el contenido del módulo es muy complejo.",
                            "Publicar material de apoyo o ejercicios más sencillos.",
                            "Programar una sesión de repaso en clase."
                        ],
                        created_at=now.isoformat(),
                        module_name=mod_title
                    ))
                
                # Evaluar individualmente
                for s in mod_students:
                    # Detectar ritmo lento o inactividad
                    if s["days_enrolled"] > 7 and s["progress_velocity"] < avg_velocity * 0.3:
                        alerts.append(Alert(
                            id=str(uuid.uuid4()),
                            teacher_id=teacher_id,
                            student_id=s["student_id"],
                            module_id=mod_id,
                            type=AlertType.SLOW_LEARNER,
                            priority=AlertPriority.MEDIUM,
                            message=f"Ritmo lento: {s['full_name']} tiene un progreso muy bajo ({round(s['progress'])}%) comparado con el promedio después de {s['days_enrolled']} días.",
                            recommendations=[
                                "Sugerir ejercicios de refuerzo más sencillos.",
                                "Enviar un mensaje motivacional al estudiante.",
                                "Proponer acompañamiento o tutoría."
                            ],
                            created_at=now.isoformat(),
                            student_name=s["full_name"],
                            module_name=mod_title
                        ))
                    
                    # Detectar ritmo rápido
                    elif s["days_enrolled"] > 1 and s["progress_velocity"] > avg_velocity * 2.0 and s["progress"] > 50:
                        alerts.append(Alert(
                            id=str(uuid.uuid4()),
                            teacher_id=teacher_id,
                            student_id=s["student_id"],
                            module_id=mod_id,
                            type=AlertType.FAST_LEARNER,
                            priority=AlertPriority.LOW,
                            message=f"Avance rápido: {s['full_name']} está completando el módulo significativamente más rápido que el promedio.",
                            recommendations=[
                                "Sugerir retos o ejercicios más avanzados.",
                                "Proponer contenido complementario.",
                                "Incentivar al alumno a ayudar a sus compañeros."
                            ],
                            created_at=now.isoformat(),
                            student_name=s["full_name"],
                            module_name=mod_title
                        ))
            
            # Ordenar alertas: HIGH -> MEDIUM -> LOW
            priority_order = {AlertPriority.HIGH: 0, AlertPriority.MEDIUM: 1, AlertPriority.LOW: 2}
            alerts.sort(key=lambda x: priority_order[x.priority])
            
            return {
                "success": True,
                "alerts": [alert.model_dump() for alert in alerts]
            }
            
        except Exception as e:
            print(f"Error GenerateAIAlertsUseCase: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
