"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, AlertTriangle, Clock, Zap, Lightbulb, User, BookOpen } from "lucide-react"
import { format } from "date-fns"
import { es } from "date-fns/locale"

interface AIAlert {
  id: string
  teacher_id: number
  student_id: number | null
  module_id: number | null
  type: "difficulty" | "slow_learner" | "fast_learner"
  priority: "high" | "medium" | "low"
  message: string
  recommendations: string[]
  created_at: string
  student_name: string | null
  module_name: string | null
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AIAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // Filters state
  const [filterType, setFilterType] = useState<string>("all")
  const [filterPriority, setFilterPriority] = useState<string>("all")
  const [filterModule, setFilterModule] = useState<string>("all")

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/teacher/alerts", {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          setAlerts(data.alerts)
        } else {
          setErrorMsg(data.error || "Error al cargar alertas IA.")
        }
      } catch (error: any) {
        console.error("Error fetching alerts:", error)
        setErrorMsg("Error de conexión con el servidor.")
      } finally {
        setIsLoading(false)
      }
    }
    fetchAlerts()
  }, [])

  // Extract unique modules for filter
  const modules = useMemo(() => {
    const mods = new Set<string>()
    alerts.forEach(a => {
      if (a.module_name) mods.add(a.module_name)
    })
    return Array.from(mods)
  }, [alerts])

  // Apply filters
  const filteredAlerts = useMemo(() => {
    return alerts.filter(a => {
      if (filterType !== "all" && a.type !== filterType) return false
      if (filterPriority !== "all" && a.priority !== filterPriority) return false
      if (filterModule !== "all" && a.module_name !== filterModule) return false
      return true
    })
  }, [alerts, filterType, filterPriority, filterModule])

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "difficulty": return <AlertTriangle className="h-5 w-5 text-destructive" />
      case "slow_learner": return <Clock className="h-5 w-5 text-orange-500" />
      case "fast_learner": return <Zap className="h-5 w-5 text-green-500" />
      default: return <Lightbulb className="h-5 w-5 text-primary" />
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "difficulty": return "Dificultad"
      case "slow_learner": return "Ritmo Lento"
      case "fast_learner": return "Avance Rápido"
      default: return type
    }
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high": return <Badge variant="destructive">Alta</Badge>
      case "medium": return <Badge className="bg-orange-500 hover:bg-orange-600">Media</Badge>
      case "low": return <Badge className="bg-blue-500 hover:bg-blue-600">Baja</Badge>
      default: return <Badge variant="outline">{priority}</Badge>
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (errorMsg) {
    return (
      <div className="flex flex-col justify-center items-center h-full min-h-[400px] text-muted-foreground gap-4">
        <AlertTriangle className="h-10 w-10 text-destructive/50" />
        <p className="font-medium text-lg text-foreground">No pudimos cargar las alertas</p>
        <p className="text-sm">{errorMsg}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-primary">Alertas Inteligentes</h1>
        <p className="text-muted-foreground mt-2">
          Recomendaciones y detecciones generadas por IA para mejorar la experiencia de tus estudiantes.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 bg-card p-4 rounded-xl border shadow-sm">
        <div className="flex flex-col gap-1.5 w-full sm:w-[200px]">
          <label className="text-xs font-medium text-muted-foreground">Tipo de Alerta</label>
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger>
              <SelectValue placeholder="Todos" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="difficulty">Dificultad</SelectItem>
              <SelectItem value="slow_learner">Ritmo Lento</SelectItem>
              <SelectItem value="fast_learner">Avance Rápido</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5 w-full sm:w-[200px]">
          <label className="text-xs font-medium text-muted-foreground">Prioridad</label>
          <Select value={filterPriority} onValueChange={setFilterPriority}>
            <SelectTrigger>
              <SelectValue placeholder="Todas" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              <SelectItem value="high">Alta</SelectItem>
              <SelectItem value="medium">Media</SelectItem>
              <SelectItem value="low">Baja</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5 w-full sm:w-[250px]">
          <label className="text-xs font-medium text-muted-foreground">Clase / Módulo</label>
          <Select value={filterModule} onValueChange={setFilterModule}>
            <SelectTrigger>
              <SelectValue placeholder="Todas" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              {modules.map(mod => (
                <SelectItem key={mod} value={mod}>{mod}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 bg-card rounded-xl border border-dashed text-center">
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <Lightbulb className="h-6 w-6 text-primary" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-1">No hay alertas activas</h3>
          <p className="text-muted-foreground text-sm max-w-sm">
            Tus estudiantes van por buen camino. Te avisaremos si detectamos anomalías o áreas de mejora.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
          {filteredAlerts.map(alert => (
            <Card key={alert.id} className="flex flex-col shadow-sm hover:shadow-md transition-shadow border-l-4" style={{
              borderLeftColor: alert.priority === 'high' ? 'hsl(var(--destructive))' : alert.priority === 'medium' ? '#f97316' : '#3b82f6'
            }}>
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(alert.type)}
                    <span className="font-semibold text-sm">{getTypeLabel(alert.type)}</span>
                  </div>
                  {getPriorityBadge(alert.priority)}
                </div>
                <CardTitle className="text-base leading-snug">
                  {alert.message}
                </CardTitle>
                <div className="flex flex-wrap gap-x-4 gap-y-2 mt-3 text-xs text-muted-foreground">
                  {alert.student_name && (
                    <span className="flex items-center gap-1.5 bg-secondary/50 px-2 py-1 rounded-md">
                      <User className="h-3 w-3" /> {alert.student_name}
                    </span>
                  )}
                  {alert.module_name && (
                    <span className="flex items-center gap-1.5 bg-secondary/50 px-2 py-1 rounded-md line-clamp-1">
                      <BookOpen className="h-3 w-3" /> {alert.module_name}
                    </span>
                  )}
                  <span className="flex items-center gap-1.5 ml-auto">
                    {format(new Date(alert.created_at), "d MMM, yyyy", { locale: es })}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="flex-grow">
                <div className="bg-primary/5 rounded-lg p-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-primary mb-2 flex items-center gap-1.5">
                    <Lightbulb className="h-3.5 w-3.5" /> Recomendaciones
                  </h4>
                  <ul className="space-y-1.5">
                    {alert.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm text-foreground flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span className="flex-1">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
