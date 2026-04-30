"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { User } from "@/hooks/use-auth"
import {
  Users,
  GraduationCap,
  BookOpen,
  UserCheck,
  Shield,
  Settings,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Activity,
  FileText,
  ArrowRight,
} from "lucide-react"
import Link from "next/link"

interface AdminDashboardProps {
  user: User
}

export function AdminDashboard({ user }: AdminDashboardProps) {
  const [stats, setStats] = useState({
    totalUsers: 0,
    students: 0,
    teachers: 0,
    admins: 0,
    pendingTeacherRequests: 0,
    pendingContent: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/dashboard/admin", {
          credentials: "include"
        })
        const data = await res.json()
        if (data.success && data.stats) {
          setStats(prev => ({
            ...prev,
            totalUsers: data.stats.totalUsers,
            students: data.stats.activeStudents,
            teachers: data.stats.activeTeachers,
            totalModules: data.stats.totalModules
          }))
        }
      } catch (error) {
        console.error("Error fetching admin stats", error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])
  const teacherRequests = [
    { id: 1, name: "Laura Fernandez", email: "laura@email.com", date: "Hace 2 dias" },
    { id: 2, name: "Miguel Torres", email: "miguel@email.com", date: "Hace 3 dias" },
    { id: 3, name: "Carmen Diaz", email: "carmen@email.com", date: "Hace 5 dias" },
  ]

  const systemHealth = [
    { name: "Base de datos", status: "healthy", latency: "12ms" },
    { name: "Autenticacion", status: "healthy", latency: "45ms" },
    { name: "API Principal", status: "healthy", latency: "23ms" },
  ]

  const recentAudit = [
    { action: "Usuario creado", user: "maria@email.com", time: "Hace 1 hora" },
    { action: "Docente aprobado", user: "pedro@email.com", time: "Hace 3 horas" },
    { action: "Contenido aprobado", user: "admin", time: "Hace 5 horas" },
    { action: "Configuracion actualizada", user: "admin", time: "Ayer" },
  ]

  const pendingContent = [
    { id: 1, title: "Ejercicio: Bucles anidados", type: "Ejercicio", author: "Prof. Garcia" },
    { id: 2, title: "Leccion: Funciones recursivas", type: "Leccion", author: "IA" },
  ]

  if (loading) {
    return <div className="flex h-[400px] items-center justify-center">Cargando panel de administración...</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground md:text-3xl">
            Panel de Administracion
          </h1>
          <p className="text-muted-foreground">Supervision general del sistema</p>
        </div>
        <Button asChild>
          <Link href="/dashboard/settings">
            <Settings className="mr-2 h-4 w-4" />
            Configuracion
          </Link>
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Usuarios</p>
              <p className="text-2xl font-bold text-foreground">{stats.totalUsers}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <GraduationCap className="h-6 w-6 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Estudiantes</p>
              <p className="text-2xl font-bold text-foreground">{stats.students}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <BookOpen className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Docentes</p>
              <p className="text-2xl font-bold text-foreground">{stats.teachers}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-500/10">
              <Clock className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pendientes</p>
              <p className="text-2xl font-bold text-foreground">
                {stats.pendingTeacherRequests + stats.pendingContent}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Teacher Requests */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5 text-primary" />
                Solicitudes de Docentes
                <span className="ml-2 rounded-full bg-yellow-500/10 px-2 py-0.5 text-xs font-medium text-yellow-600">
                  {stats.pendingTeacherRequests}
                </span>
              </CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard/teacher-requests">Ver todas</Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {teacherRequests.map((request) => (
                <div
                  key={request.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback>
                        {request.name.split(" ").map((n) => n[0]).join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-medium text-foreground">{request.name}</p>
                      <p className="text-xs text-muted-foreground">{request.email}</p>
                      <p className="text-xs text-muted-foreground">{request.date}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="text-destructive hover:text-destructive">
                      <XCircle className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline" className="text-accent hover:text-accent">
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Pending Content */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Contenido Pendiente
              </CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard/content-review">Ver todo</Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {pendingContent.map((content) => (
                <div
                  key={content.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-foreground">{content.title}</p>
                      <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">
                        {content.type}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">Por: {content.author}</p>
                  </div>
                  <Button size="sm">Revisar</Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* System Health */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Activity className="h-5 w-5 text-primary" />
                Estado del Sistema
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {systemHealth.map((service, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-accent" />
                    <span className="text-sm text-foreground">{service.name}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{service.latency}</span>
                </div>
              ))}
              <Button variant="outline" className="mt-2 w-full" asChild>
                <Link href="/dashboard/audit">
                  Ver detalles
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Recent Audit */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Shield className="h-5 w-5 text-primary" />
                Auditoria Reciente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentAudit.map((entry, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">{entry.action}</p>
                    <p className="text-xs text-muted-foreground">{entry.user}</p>
                    <p className="text-xs text-muted-foreground">{entry.time}</p>
                  </div>
                </div>
              ))}
              <Button variant="ghost" size="sm" className="w-full" asChild>
                <Link href="/dashboard/audit">Ver historial completo</Link>
              </Button>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="h-5 w-5 text-primary" />
                Esta Semana
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Nuevos usuarios</span>
                <span className="text-sm font-medium text-foreground">+12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Lecciones completadas</span>
                <span className="text-sm font-medium text-foreground">234</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Ejercicios resueltos</span>
                <span className="text-sm font-medium text-foreground">567</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Tiempo promedio</span>
                <span className="text-sm font-medium text-foreground">25 min/dia</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
