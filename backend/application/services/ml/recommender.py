from typing import List, Dict, Any, Optional


class Recommender:
    def generate_student_recommendations(
        self,
        engagement: Optional[float] = None,
        performance: Optional[float] = None,
        dropout_prob: Optional[float] = None,
        frustration: Optional[int] = None,
        cluster_name: Optional[str] = None,
        anomaly: Optional[Dict] = None,
    ) -> List[str]:
        recommendations = []

        if dropout_prob is not None:
            if dropout_prob > 0.6:
                recommendations.append(
                    "Riesgo de abandono alto. Programa una reunión con el estudiante "
                    "para identificar las causas y ofrecer apoyo personalizado."
                )
            elif dropout_prob > 0.3:
                recommendations.append(
                    "Riesgo de abandono moderado. Envía recordatorios motivacionales "
                    "y ofrece contenido adicional de refuerzo."
                )

        if frustration is not None:
            if frustration == 2:
                recommendations.append(
                    "Frustración alta detectada. Sugiere ejercicios más sencillos "
                    "y ofrece pausas activas. Revisa la dificultad del contenido actual."
                )
            elif frustration == 1:
                recommendations.append(
                    "Signos de frustración media. Monitorea los ejercicios recientes "
                    "y considera ajustar la dificultad."
                )

        if engagement is not None:
            if engagement < 0.3:
                recommendations.append(
                    "Engagement críticamente bajo. Recomienda contenido gamificado "
                    "o proyectos prácticos que conecten con sus intereses."
                )
            elif engagement < 0.5:
                recommendations.append(
                    "Engagement por debajo del promedio. Sugiere actividades "
                    "interactivas y retos cortos para recuperar su atención."
                )
            elif engagement > 0.8:
                recommendations.append(
                    "Engagement alto. Ofrece retos avanzados y contenido "
                    "complementario para mantener su motivación."
                )

        if performance is not None:
            if performance < 0.3:
                recommendations.append(
                    "Rendimiento bajo. Recomienda repasar los fundamentos "
                    "y realizar ejercicios de práctica adicional."
                )
            elif performance > 0.8:
                recommendations.append(
                    "Rendimiento sobresaliente. Propón proyectos desafiantes "
                    "y contenido de nivel avanzado."
                )

        if cluster_name == "En Riesgo":
            recommendations.append(
                "Estudiante clasificado en cluster 'En Riesgo'. Activar "
                "seguimiento intensivo semanal con el tutor."
            )
        elif cluster_name == "Principiante":
            recommendations.append(
                "Estudiante nuevo o con poca actividad. Ofrece una guía "
                "de inicio rápido y contenido introductorio."
            )

        if anomaly and anomaly.get("is_anomaly"):
            recommendations.append(
                "Comportamiento atípico detectado en la actividad reciente. "
                "Revisar el historial de las últimas semanas para identificar "
                "cambios bruscos en el patrón de estudio."
            )

        if not recommendations:
            recommendations.append(
                "El estudiante mantiene un progreso estable. Continuar "
                "monitoreo regular sin intervenciones adicionales."
            )

        return recommendations

    def generate_teacher_insights(
        self,
        cluster_summary: List[Dict],
        at_risk_count: int,
        high_frustration_count: int,
        avg_engagement: float,
        avg_performance: float,
    ) -> List[Dict[str, Any]]:
        insights = []

        total = sum(c["count"] for c in cluster_summary)
        if total == 0:
            return insights

        for c in cluster_summary:
            pct = (c["count"] / total) * 100
            if c["cluster_name"] == "En Riesgo" and pct > 20:
                insights.append({
                    "type": "warning",
                    "message": f"El {pct:.0f}% de los estudiantes está en el cluster "
                               f"'En Riesgo'. Revisar estrategias pedagógicas.",
                    "cluster": c["cluster_name"],
                    "percentage": round(pct, 1),
                })

        if at_risk_count > 0:
            pct = (at_risk_count / total) * 100
            insights.append({
                "type": "critical" if pct > 15 else "warning",
                "message": f"{at_risk_count} estudiante(s) ({(at_risk_count/total)*100:.0f}%) "
                           f"presentan alto riesgo de abandono.",
                "metric": "dropout_risk",
                "count": at_risk_count,
            })

        if high_frustration_count > 0:
            insights.append({
                "type": "warning",
                "message": f"{high_frustration_count} estudiante(s) muestran niveles "
                           f"altos de frustración. Revisar dificultad de ejercicios.",
                "metric": "frustration",
                "count": high_frustration_count,
            })

        if avg_engagement < 0.4:
            insights.append({
                "type": "warning",
                "message": f"Engagement promedio bajo ({avg_engagement:.2f}). "
                           f"Considerar actividades grupales o gamificación.",
                "metric": "engagement",
                "value": round(avg_engagement, 2),
            })

        if avg_performance < 0.4:
            insights.append({
                "type": "info",
                "message": f"Rendimiento promedio bajo ({avg_performance:.2f}). "
                           f"Sugerir repaso de conceptos fundamentales.",
                "metric": "performance",
                "value": round(avg_performance, 2),
            })

        return insights
