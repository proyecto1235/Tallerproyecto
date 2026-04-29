"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Activity, ShieldAlert, CheckCircle, Clock, Database, Server, Users } from "lucide-react"

const MOCK_AUDIT_LOGS = [
  { id: 1, action: "Login Exitoso", user: "admin@robolearn.com", type: "info", date: "Hace 5 min" },
  { id: 2, action: "Rol de usuario actualizado", user: "Admin", details: "Ana García -> Profesor", type: "warning", date: "Hace 15 min" },
  { id: 3, action: "Módulo publicado", user: "Admin", details: "Fundamentos de Robótica", type: "success", date: "Hace 1 hora" },
  { id: 4, action: "Fallo de Autenticación", user: "desconocido@test.com", details: "Contraseña incorrecta (3 intentos)", type: "error", date: "Hace 2 horas" },
  { id: 5, action: "Nuevo Registro", user: "Estudiante", details: "carlos.perez@escuela.com", type: "info", date: "Hace 5 horas" },
  { id: 6, action: "Solicitud de Profesor Aprobada", user: "Admin", details: "Fernando Ruiz", type: "success", date: "Ayer" },
]

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([])

  useEffect(() => {
    setLogs(MOCK_AUDIT_LOGS)
  }, [])

  const getIconForType = (type: string) => {
    switch (type) {
      case "error": return <ShieldAlert className="h-5 w-5 text-red-500" />
      case "warning": return <Activity className="h-5 w-5 text-orange-500" />
      case "success": return <CheckCircle className="h-5 w-5 text-green-500" />
      default: return <Clock className="h-5 w-5 text-blue-500" />
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Sistema y Auditoría</h1>
        <p className="text-muted-foreground text-lg">
          Monitorea el estado de la plataforma y el registro de actividades críticas.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="neo-shadow border-primary/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
              <Server className="h-4 w-4" /> Estado del Servidor
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">Operativo</div>
            <p className="text-xs text-muted-foreground mt-1">Uptime: 99.9% (Últimos 30 días)</p>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-primary/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
              <Database className="h-4 w-4" /> Base de Datos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">Conectada</div>
            <p className="text-xs text-muted-foreground mt-1">Latencia: 24ms</p>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-primary/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
              <Users className="h-4 w-4" /> Usuarios Activos Hoy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">142</div>
            <p className="text-xs text-muted-foreground mt-1">+12% vs semana anterior</p>
          </CardContent>
        </Card>
      </div>

      <Card className="neo-shadow border-primary/20">
        <CardHeader>
          <CardTitle>Historial de Auditoría</CardTitle>
          <CardDescription>
            Registro inmutable de las acciones administrativas y de seguridad recientes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {logs.map((log, index) => (
              <div key={log.id} className="flex gap-4 relative">
                {/* Línea conectora */}
                {index !== logs.length - 1 && (
                  <div className="absolute left-2.5 top-8 bottom-[-2rem] w-[2px] bg-border" />
                )}
                
                <div className="relative z-10 flex h-6 w-6 items-center justify-center rounded-full bg-background ring-4 ring-background">
                  {getIconForType(log.type)}
                </div>
                
                <div className="flex-1 pb-4">
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1">
                    <h4 className="font-semibold">{log.action}</h4>
                    <span className="text-sm text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {log.date}
                    </span>
                  </div>
                  <div className="mt-1 flex flex-col text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">{log.user}</span>
                    {log.details && <span>{log.details}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
