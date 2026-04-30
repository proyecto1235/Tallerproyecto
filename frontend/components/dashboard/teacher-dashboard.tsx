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
  })
  
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/teacher/dashboard", {
          credentials: "include"
        })
        const data = await res.json()
        if (data.success && data.metrics) {
          setStats({
            totalStudents: data.metrics.total_students || 0,
            activeClasses: data.metrics.active_classes || 0,
            pendingRequests: data.metrics.pending_requests || 0,
            avgProgress: data.metrics.avg_progress || 0,
          })
        }
      } catch (error) {
        console.error("Error fetching teacher metrics", error)
      } finally {
        setLoading(false)
      }
    }
    fetchMetrics()
  }, [])

  const alerts = [
    {
      id: 1,
      student: "Maria Garcia",
      type: "difficulty",
      message: "Dificultades con bucles for",
      time: "Hace 2 horas",
    },
    {
      id: 2,
      student: "Carlos Lopez",
      type: "inactive",
      message: "Sin actividad por 5 dias",
      time: "Hace 1 dia",
    },
    {
      id: 3,
      student: "Ana Martinez",
      type: "difficulty",
      message: "Errores frecuentes en condicionales",
      time: "Hace 3 horas",
    },
  ]

  const topStudents = [
    { name: "Juan Perez", points: 450, progress: 85 },
    { name: "Sofia Ruiz", points: 420, progress: 78 },
    { name: "Pedro Sanchez", points: 380, progress: 72 },
  ]

  const recentActivity = [
    { action: "Nuevo estudiante", detail: "Maria se unio a Python Basico", time: "Hace 1 hora" },
    { action: "Ejercicio completado", detail: "15 estudiantes completaron Bucles", time: "Hace 3 horas" },
    { action: "Reto finalizado", detail: "Reto semanal: Variables", time: "Ayer" },
  ]

  const commonErrors = [
    { topic: "Bucles for", percentage: 35, trend: "up" },
    { topic: "Condicionales", percentage: 28, trend: "down" },
    { topic: "Variables", percentage: 15, trend: "stable" },
  ]

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
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start gap-3 rounded-lg border bg-background p-3"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-500/10">
                    <AlertTriangle className="h-4 w-4 text-orange-500" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{alert.student}</p>
                    <p className="text-sm text-muted-foreground">{alert.message}</p>
                    <p className="text-xs text-muted-foreground">{alert.time}</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Ver
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Common Errors */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                Errores Comunes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {commonErrors.map((error, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">{error.topic}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">{error.percentage}%</span>
                      {error.trend === "up" ? (
                        <TrendingUp className="h-4 w-4 text-destructive" />
                      ) : error.trend === "down" ? (
                        <TrendingDown className="h-4 w-4 text-accent" />
                      ) : null}
                    </div>
                  </div>
                  <Progress value={error.percentage} className="h-2" />
                </div>
              ))}
              <Button variant="outline" className="w-full" asChild>
                <Link href="/dashboard/metrics">
                  Ver metricas detalladas
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
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
                      {student.name.split(" ").map((n) => n[0]).join("")}
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

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actividad Reciente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.detail}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
