"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Loader2, ArrowLeft, BookOpen, CheckCircle2, Lock, ChevronRight, FileText, Users, Clock, AlertTriangle } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "sonner"
import { useAuth } from "@/hooks/use-auth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export default function ClassDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const classId = parseInt(params.id as string, 10)

  const [classData, setClassData] = useState<any | null>(null)
  const [modules, setModules] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [enrollmentStatus, setEnrollmentStatus] = useState<string | null>(null)
  const [requesting, setRequesting] = useState(false)

  useEffect(() => {
    if (!classId) return
    loadData()
  }, [classId])

  async function loadData() {
    setIsLoading(true)
    try {
      const [classRes, enrolledRes] = await Promise.all([
        fetch(`${API}/classes/${classId}`, { credentials: "include" }),
        fetch(`${API}/classes/enrolled`, { credentials: "include" })
      ])
      const classData = await classRes.json()
      if (classData.success) {
        setClassData(classData.class)
        setModules((classData.class.class_modules || []).map((m: any, i: number) => ({
          ...m,
          exercise_count: m.exercises?.length || 0,
          order: m.order || i + 1
        })))
      } else {
        setErrorMsg("Clase no encontrada")
      }

      const enrolledData = await enrolledRes.json()
      if (enrolledData.success) {
        const enrollment = enrolledData.classes?.find((c: any) => c.id === classId)
        if (enrollment) {
          setEnrollmentStatus(enrollment.enrollment_status)
          if (enrollment.enrollment_status === "approved") {
            setErrorMsg(null)
          } else if (enrollment.enrollment_status === "pending") {
            setErrorMsg("Tu solicitud de matrícula está pendiente de aprobación.")
          } else if (enrollment.enrollment_status === "rejected") {
            setErrorMsg("Tu solicitud de matrícula fue rechazada.")
          }
        } else {
          setErrorMsg("No estás matriculado en esta clase.")
        }
      }
    } catch (_) {
      // Fallback to localStorage
      const saved = localStorage.getItem("robolearn_teacher_classes")
      if (saved) {
        const all = JSON.parse(saved)
        const found = all.find((c: any) => c.id === params.id)
        if (found) {
          setClassData(found)
          setModules((found.modules || []).map((m: any, i: number) => ({
            ...m,
            exercise_count: m.exercises?.length || 0,
            order: m.order || i + 1
          })))
        } else {
          setErrorMsg("Clase no encontrada")
        }
      }
    }
    setIsLoading(false)
  }

  async function handleEnroll() {
    setRequesting(true)
    try {
      const res = await fetch(`${API}/classes/${classId}/enroll`, {
        method: "POST",
        credentials: "include"
      })
      const data = await res.json()
      if (data.success) {
        setEnrollmentStatus("pending")
        setErrorMsg("Tu solicitud de matrícula está pendiente de aprobación.")
        toast.success("Solicitud enviada. Espera la aprobación del docente.")
      } else {
        toast.error(data.error || "Error al solicitar matrícula")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
    setRequesting(false)
  }

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (!classData) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <h2 className="text-2xl font-bold">Clase no encontrada</h2>
        <Button onClick={() => router.push('/dashboard/classes')} variant="outline"><ArrowLeft className="w-4 h-4 mr-2" />Volver</Button>
      </div>
    )
  }

  if (errorMsg && enrollmentStatus !== "approved") {
    return (
      <div className="max-w-4xl mx-auto p-4 space-y-6">
        <Button variant="ghost" onClick={() => router.push('/dashboard/classes')}>
          <ArrowLeft className="w-4 h-4 mr-2" />Clases
        </Button>
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardContent className="flex flex-col items-center py-12 gap-4">
            <AlertTriangle className="w-12 h-12 text-amber-500" />
            <h2 className="text-xl font-bold text-center">{errorMsg}</h2>
            {enrollmentStatus === null && (
              <Button onClick={handleEnroll} disabled={requesting} size="lg">
                {requesting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                Solicitar Matrícula
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <Button variant="ghost" onClick={() => router.push('/dashboard/classes')}>
        <ArrowLeft className="w-4 h-4 mr-2" />Clases
      </Button>

      <div className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10">
          <BookOpen className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">{classData.title}</h1>
          <p className="text-muted-foreground flex items-center gap-2 mt-1">
            {classData.category} · {classData.difficulty}
          </p>
        </div>
      </div>

      <Tabs defaultValue="modules" className="space-y-4">
        <TabsList>
          <TabsTrigger value="modules" className="flex items-center gap-2">
            <FileText className="w-4 h-4" /> Módulos
          </TabsTrigger>
          <TabsTrigger value="info" className="flex items-center gap-2">
            <Users className="w-4 h-4" /> Información
          </TabsTrigger>
        </TabsList>

        <TabsContent value="modules" className="space-y-4">
          {modules.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground border-2 border-dashed rounded-xl">
              <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="font-medium">No hay módulos disponibles aún</p>
            </div>
          ) : (
            modules.map((mod, index) => (
              <Card key={mod.id || index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-bold">
                      {mod.order}
                    </div>
                    <div>
                      <h3 className="font-semibold">{mod.title}</h3>
                      <p className="text-xs text-muted-foreground">{mod.exercise_count} ejercicios</p>
                    </div>
                  </div>
                  <Button size="sm" disabled>
                    <Lock className="w-4 h-4 mr-1" /> Próximamente
                  </Button>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="info">
          <Card>
            <CardContent className="p-6 space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Descripción</h3>
                <p className="text-muted-foreground">{classData.description || "Sin descripción disponible."}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Categoría</p>
                  <p className="font-medium">{classData.category || "General"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Dificultad</p>
                  <p className="font-medium">{classData.difficulty || "No especificada"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Módulos</p>
                  <p className="font-medium">{modules.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
