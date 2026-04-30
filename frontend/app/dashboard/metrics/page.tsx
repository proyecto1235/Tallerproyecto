"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  LineChart,
  Line,
  Legend
} from "recharts"
import { Loader2, Users, BookOpen, Target, TrendingUp, Lightbulb, AlertTriangle } from "lucide-react"

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/teacher/dashboard", {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          setMetrics(data.metrics)
        } else {
          setErrorMsg(data.error || "Error desconocido al cargar métricas.")
        }
      } catch (error: any) {
        console.error("Error fetching metrics:", error)
        setErrorMsg(error.message || "Error de conexión con el servidor.")
      } finally {
        setIsLoading(false)
      }
    }
    fetchMetrics()
  }, [])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (errorMsg || !metrics) {
    return (
      <div className="flex flex-col justify-center items-center h-full min-h-[400px] text-muted-foreground gap-4">
        <AlertTriangle className="h-10 w-10 text-destructive/50" />
        <p className="font-medium text-lg text-foreground">No pudimos cargar las métricas</p>
        <p className="text-sm">{errorMsg || "Aún no tienes estudiantes matriculados o hubo un problema interno."}</p>
      </div>
    )
  }

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Métricas y Analíticas</h1>
        <p className="text-muted-foreground">
          Visualiza el rendimiento de tus estudiantes y el progreso de tus clases.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="neo-shadow border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Estudiantes</CardTitle>
            <Users className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_students}</div>
            <p className="text-xs text-muted-foreground">En todos tus módulos</p>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Promedio de Progreso</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.avg_progress}%</div>
            <p className="text-xs text-muted-foreground">Promedio general</p>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-orange-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasa de Finalización</CardTitle>
            <Target className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.completion_rate}%</div>
            <p className="text-xs text-muted-foreground">Módulos completados</p>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-purple-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cursos Activos</CardTitle>
            <BookOpen className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.course_progress?.length || 0}</div>
            <p className="text-xs text-muted-foreground">Módulos con matrículas</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        
        {/* Progreso por Curso */}
        <Card className="col-span-1 lg:col-span-4 neo-shadow">
          <CardHeader>
            <CardTitle>Progreso Promedio por Curso</CardTitle>
            <CardDescription>
              Comparativa del avance de los estudiantes en cada módulo.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.course_progress || []} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="name" type="category" width={150} tick={{fontSize: 12}} />
                  <RechartsTooltip 
                    formatter={(value) => [`${value}%`, "Progreso"]}
                    contentStyle={{ borderRadius: '8px', border: '1px solid hsl(var(--border))', backgroundColor: 'hsl(var(--card))', color: 'hsl(var(--foreground))' }}
                  />
                  <Bar dataKey="progress" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]}>
                    {(metrics.course_progress || []).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Distribución de Rendimiento */}
        <Card className="col-span-1 lg:col-span-3 neo-shadow">
          <CardHeader>
            <CardTitle>Distribución de Rendimiento</CardTitle>
            <CardDescription>
              Porcentaje de estudiantes según su nivel de avance.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={metrics.performance_distribution || []}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => percent > 0 ? `${(percent * 100).toFixed(0)}%` : ''}
                  >
                    {(metrics.performance_distribution || []).map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '8px', border: '1px solid hsl(var(--border))', backgroundColor: 'hsl(var(--card))', color: 'hsl(var(--foreground))' }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Actividad Semanal */}
        <Card className="col-span-1 lg:col-span-2 neo-shadow">
          <CardHeader>
            <CardTitle>Actividad Semanal</CardTitle>
            <CardDescription>
              Interacción de los estudiantes en los últimos 7 días.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics.weekly_activity || []} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '8px', border: '1px solid hsl(var(--border))', backgroundColor: 'hsl(var(--card))', color: 'hsl(var(--foreground))' }}
                  />
                  <Line type="monotone" dataKey="activos" stroke="hsl(var(--primary))" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Insights AI */}
        <Card className="col-span-1 neo-shadow-primary bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-primary" />
              Insights de IA
            </CardTitle>
            <CardDescription>Recomendaciones automáticas</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {(metrics.insights || []).map((insight: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-sm bg-card p-3 rounded-lg border">
                  <div className="mt-0.5 h-2 w-2 rounded-full bg-primary flex-shrink-0" />
                  <span className="text-foreground">{insight}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

    </div>
  )
}
