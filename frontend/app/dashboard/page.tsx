"use client"

import { useAuth } from "@/hooks/use-auth"
import { StudentDashboard } from "@/components/dashboard/student-dashboard"
import { TeacherDashboard } from "@/components/dashboard/teacher-dashboard"
import { AdminDashboard } from "@/components/dashboard/admin-dashboard"
import { Loader2 } from "lucide-react"

export default function DashboardPage() {
  const { user, isLoading } = useAuth()

  if (isLoading || !user) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  switch (user.role) {
    case "admin":
      return <AdminDashboard user={user} />
    case "teacher":
      return <TeacherDashboard user={user} />
    default:
      return <StudentDashboard user={user} />
  }
}
