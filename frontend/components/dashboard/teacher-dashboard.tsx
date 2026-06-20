"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { User } from "@/hooks/use-auth"
import {
  Users,
  GraduationCap,
  Bell,
  BarChart3,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Clock,
  CheckCircle,
  FileText,
  Plus,
  ArrowRight,
  Trophy,
} from "lucide-react"
import Link from "next/link"

interface TeacherDashboardProps {
  user: User
}

export function TeacherDashboard({ user }: TeacherDashboardProps) {
  const [stats, setStats] = useState({
    totalStudents: 0,
    activeClasses: 0,
    pendingRequests: 0,
    avgProgress: 0,
    completionRate: 0,
    activeStudents: 0,
    insights: [] as string[],
  })
  const [alerts, setAlerts] = useState<any[]>([])
  const [students, setStudents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, alertsRes, studentsRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/teacher/dashboard`, { credentials: "include" }),
          fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/teacher/alerts`, { credentials: "include" }),
          fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/teacher/students`, { credentials: "include" }),
        ])
        const metricsData = await metricsRes.json()
        const alertsData = await alertsRes.json()
        const studentsData = await studentsRes.json()

        if (metricsData.success && metricsData.metrics) {
          setStats({
            totalStudents: metricsData.metrics.total_students || 0,
            activeClasses: metricsData.metrics.active_classes || (metricsData.metrics.course_progress?.length || 0),
            pendingRequests: metricsData.metrics.pending_requests || 0,
            avgProgress: metricsData.metrics.avg_progress || 0,
            completionRate: metricsData.metrics.completion_rate || 0,
            activeStudents: metricsData.metrics.active_students || 0,
            insights: metricsData.metrics.insights || [],
          })
        }
        if (alertsData.success && alertsData.alerts) {
          setAlerts(alertsData.alerts)
        }
        if (studentsData.success && studentsData.students) {
          setStudents(studentsData.students)
        }
      } catch (error) {
        console.error("Error fetching teacher data", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const topStudents = [...students]
    .sort((a, b) => b.progress - a.progress)
    .slice(0, 3)
    .map((s: any) => ({ name: s.full_name, points: 0, progress: s.progress }))

  const recentActivity = stats.insights.map((i: string) => ({
    action: "Insight",
    detail: i,
    time: "Hoy"
  }))

  const commonErrors = []

  if (loading) {
    return <div className="flex h-[400px] items-center justify-center">Cargando métricas...</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground md:text-3xl">
            Panel del Docente
          </h1>
          <p className="text-muted-foreground">Bienvenido, {user?.fullName || "Docente"}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/dashboard/challenges/create">
              <Trophy className="mr-2 h-4 w-4" />
              Crear Reto
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/dashboard/content">
              <FileText className="mr-2 h-4 w-4" />
              Crear contenido
            </Link>
          </Button>
          <Button asChild>
            <Link href="/dashboard/my-classes">
              <Plus className="mr-2 h-4 w-4" />
              Nueva clase
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <GraduationCap className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Estudiantes</p>
              <p className="text-2xl font-bold text-foreground">{stats.totalStudents}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <Users className="h-6 w-6 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Clases Activas</p>
              <p className="text-2xl font-bold text-foreground">{stats.activeClasses}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-500/10">
              <Clock className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Solicitudes</p>
              <p className="text-2xl font-bold text-foreground">{stats.pendingRequests}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <BarChart3 className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Progreso Promedio</p>
              <p className="text-2xl font-bold text-foreground">{stats.avgProgress}%</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* AI Alerts */}
          <Card className="border-orange-500/20 bg-orange-500/5">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-orange-500" />
                Alertas de IA
              </CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard/alerts">Ver todas</Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {alerts.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">No hay alertas generadas aún</p>
              ) : (
                alerts.slice(0, 5).map((alert: any) => (
                  <div
                    key={alert.id}
                    className="flex items-start gap-3 rounded-lg border bg-background p-3"
                  >
                    <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                      alert.priority === "high" ? "bg-red-500/10" :
                      alert.priority === "medium" ? "bg-orange-500/10" : "bg-yellow-500/10"
                    }`}>
                      <AlertTriangle className={`h-4 w-4 ${
                        alert.priority === "high" ? "text-red-500" :
                        alert.priority === "medium" ? "text-orange-500" : "text-yellow-500"
                      }`} />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">{alert.student_name || alert.student || "Estudiante"}</p>
                      <p className="text-sm text-muted-foreground">{alert.message}</p>
                      {alert.recommendations && alert.recommendations.length > 0 && (
                        <div className="mt-1 text-xs text-muted-foreground">
                          Sugerencia: {alert.recommendations[0]}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Insights from AI */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                Insights de IA
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="rounded-lg bg-primary/5 p-3 text-center">
                  <p className="text-2xl font-bold text-primary">{stats.completionRate}%</p>
                  <p className="text-xs text-muted-foreground">Tasa de completitud</p>
                </div>
                <div className="rounded-lg bg-accent/5 p-3 text-center">
                  <p className="text-2xl font-bold text-accent">{stats.activeStudents}</p>
                  <p className="text-xs text-muted-foreground">Estudiantes activos</p>
                </div>
              </div>
              {stats.insights.map((insight, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <div className="mt-1 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                  <span className="text-muted-foreground">{insight}</span>
                </div>
              ))}
              {stats.insights.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">No hay insights disponibles</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Top Students */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Mejores Estudiantes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {topStudents.map((student, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                    {index + 1}
                  </span>
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="text-xs">
                      {student.name.split(" ").map((n: string) => n[0]).join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{student.name}</p>
                    <p className="text-xs text-muted-foreground">{student.points} pts</p>
                  </div>
                  <span className="text-sm font-medium text-accent">{student.progress}%</span>
                </div>
              ))}
              <Button variant="ghost" size="sm" className="w-full" asChild>
                <Link href="/dashboard/students">Ver todos</Link>
              </Button>
            </CardContent>
          </Card>

          {/* Student Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Progreso de Estudiantes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {students.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">No hay estudiantes aún</p>
              )}
              {students.slice(0, 5).map((s: any, i: number) => (
                <div key={i} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium truncate">{s.full_name}</span>
                    <span className="text-muted-foreground">{s.progress}%</span>
                  </div>
                  <Progress value={s.progress} className="h-1.5" />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
