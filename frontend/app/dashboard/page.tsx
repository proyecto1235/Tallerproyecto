"use client"

import { useAuth } from "@/hooks/use-auth"
import { TeacherDashboard } from "@/components/dashboard/teacher-dashboard"
import { AdminDashboard } from "@/components/dashboard/admin-dashboard"
import { Loader2 } from "lucide-react"
import dynamic from "next/dynamic"

const StudentDashboard = dynamic(() => import("@/components/dashboard/student-dashboard").then(m => ({ default: m.StudentDashboard })), { ssr: false })

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
