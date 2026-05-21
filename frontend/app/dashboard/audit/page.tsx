"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Activity, ShieldAlert, CheckCircle, Clock, Database, Server, Users, RefreshCw, Loader2 } from "lucide-react"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ server: "Verificando...", db: "Verificando...", users: 0 })

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const [logRes, statRes] = await Promise.all([
        fetch(`${API}/admin/audit-logs`, { credentials: "include" }),
        fetch(`${API}/admin/dashboard`, { credentials: "include" })
      ])
      const logData = await logRes.json()
      if (logData.success) {
        setLogs(logData.events.map((e: any, i: number) => ({
          id: e._id || i,
          action: e.event_type.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
          user: e.user_id ? `Usuario #${e.user_id}` : "Sistema",
          details: e.data ? Object.entries(e.data).map(([k, v]) => `${k}: ${v}`).join(", ") : "",
          type: e.event_type.includes("error") || e.event_type.includes("fail") ? "error" :
                e.event_type.includes("approved") || e.event_type.includes("completed") || e.event_type.includes("passed") ? "success" :
                e.event_type.includes("pending") || e.event_type.includes("request") ? "warning" : "info",
          date: e.timestamp ? new Date(e.timestamp).toLocaleString("es-ES") : "",
        })))
      }
      const statData = await statRes.json()
      if (statData.success) {
        setStats({
          server: "Operativo",
          db: "Conectada",
          users: statData.stats.activeStudents || 0,
        })
      }
    } catch (_) {
      setStats({ server: "Fuera de línea", db: "Desconectada", users: 0 })
    }
    setLoading(false)
  }

  useEffect(() => { fetchLogs() }, [])

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
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Sistema y Auditoría</h1>
          <p className="text-muted-foreground">Monitorea el estado de la plataforma y el registro de actividades críticas.</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchLogs} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-1 ${loading ? "animate-spin" : ""}`} />
          Actualizar
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
              <Server className="h-4 w-4" /> Estado del Servidor
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${stats.server === "Operativo" ? "text-green-500" : "text-red-500"}`}>
              {stats.server}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Uptime: 99.9% (Últimos 30 días)</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
              <Database className="h-4 w-4" /> Base de Datos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${stats.db === "Conectada" ? "text-green-500" : "text-red-500"}`}>
              {stats.db}
            </div>
            <p className="text-xs text-muted-foreground mt-1">PostgreSQL + MongoDB</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-muted-foreground">
              <Users className="h-4 w-4" /> Estudiantes Activos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.users}</div>
            <p className="text-xs text-muted-foreground mt-1">Usuarios registrados en la plataforma</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historial de Auditoría</CardTitle>
          <CardDescription>Registro de actividades recientes del sistema.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No hay eventos registrados aún.</div>
          ) : (
            <div className="space-y-8">
              {logs.map((log, index) => (
                <div key={log.id} className="flex gap-4 relative">
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
          )}
        </CardContent>
      </Card>
    </div>
  )
}
