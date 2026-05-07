"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useAuth, type User } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Code,
  LayoutDashboard,
  BookOpen,
  Trophy,
  Users,
  Settings,
  LogOut,
  GraduationCap,
  BarChart3,
  Bell,
  FileText,
  UserCheck,
  Shield,
  Menu,
  X,
  Flame,
  Star,
} from "lucide-react"
import { useState } from "react"

interface SidebarProps {
  user: User
}

const studentLinks = [
  { href: "/dashboard", label: "Inicio", icon: LayoutDashboard },
  { href: "/dashboard/modules", label: "Modulos", icon: BookOpen },
  { href: "/dashboard/exercises", label: "Ejercicios", icon: Code },
  { href: "/dashboard/challenges", label: "Retos", icon: Trophy },
  { href: "/dashboard/classes", label: "Mis Clases", icon: Users },
  { href: "/dashboard/achievements", label: "Logros", icon: Star },
  { href: "/dashboard/settings", label: "Ajustes", icon: Settings },
]

const teacherLinks = [
  { href: "/dashboard", label: "Inicio", icon: LayoutDashboard },
  { href: "/dashboard/my-classes", label: "Mis Clases", icon: Users },
  { href: "/dashboard/students", label: "Estudiantes", icon: GraduationCap },
  { href: "/dashboard/metrics", label: "Metricas", icon: BarChart3 },
  { href: "/dashboard/alerts", label: "Alertas IA", icon: Bell },
  { href: "/dashboard/challenges", label: "Retos", icon: Trophy },
  { href: "/dashboard/settings", label: "Ajustes", icon: Settings },
]

const adminLinks = [
  { href: "/dashboard", label: "Inicio", icon: LayoutDashboard },
  { href: "/dashboard/users", label: "Usuarios", icon: Users },
  { href: "/dashboard/teacher-requests", label: "Solicitudes", icon: UserCheck },
  { href: "/dashboard/modules", label: "Módulos Globales", icon: BookOpen },
  { href: "/dashboard/content-review", label: "Revisión", icon: FileText },
  { href: "/dashboard/audit", label: "Auditoría", icon: Shield },
  { href: "/dashboard/settings", label: "Ajustes", icon: Settings },
]

export function Sidebar({ user }: SidebarProps) {
  const pathname = usePathname()
  const { logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

  const userRole = user?.role || "student"

  const links =
    userRole === "admin"
      ? adminLinks
      : userRole === "teacher"
        ? teacherLinks
        : studentLinks

  const roleLabels = {
    student: "Estudiante",
    teacher: "Docente",
    admin: "Administrador",
  }

  // Generar iniciales de forma segura
  const initials = (user?.fullName || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
    || "U"

  return (
    <>
      {/* Mobile header */}
      <div className="fixed left-0 right-0 top-0 z-50 flex h-16 items-center justify-between border-b bg-background px-4 lg:hidden">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Code className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="font-bold text-foreground">RoboLearn</span>
        </Link>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="rounded-lg p-2 hover:bg-muted"
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-foreground/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-50 flex h-full w-64 flex-col bg-sidebar text-sidebar-foreground transition-transform lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-sidebar-border px-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-primary">
            <Code className="h-5 w-5 text-sidebar-primary-foreground" />
          </div>
          <span className="text-xl font-bold">RoboLearn</span>
        </div>

        {/* User info */}
        <div className="border-b border-sidebar-border p-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10 border-2 border-sidebar-accent">
              <AvatarFallback className="bg-sidebar-accent text-sidebar-accent-foreground">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium">{user?.fullName || "Usuario"}</p>
              <p className="text-xs text-sidebar-foreground/70">{user?.role ? roleLabels[user.role] : "Usuario"}</p>
            </div>
          </div>
          {user?.role === "student" && (
            <div className="mt-3 flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <Star className="h-3.5 w-3.5 text-yellow-500" />
                <span>{user?.points || 0} pts</span>
              </div>
              <div className="flex items-center gap-1">
                <Flame className="h-3.5 w-3.5 text-orange-500" />
                <span>{user?.streakDays || 0} dias</span>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-3">
          <ul className="space-y-1">
            {links.map((link) => {
              const isActive = pathname === link.href || (link.href !== "/dashboard" && pathname.startsWith(link.href))
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "text-sidebar-foreground/80 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                    )}
                  >
                    <link.icon className="h-5 w-5" />
                    {link.label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border p-3">
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-sidebar-foreground/80 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
            onClick={logout}
          >
            <LogOut className="h-5 w-5" />
            Cerrar sesion
          </Button>
        </div>
      </aside>
    </>
  )
}
