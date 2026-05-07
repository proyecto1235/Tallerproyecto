"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Loader2, ArrowLeft, BookOpen, CheckCircle2, Lock, ChevronRight, FileText, Users, Clock, AlertTriangle } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const STORAGE_KEY = "robolearn_teacher_classes"
const ENROLLMENTS_KEY = "robolearn_enrollments"

export default function ClassDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const classId = params.id as string

  const [classData, setClassData] = useState<any | null>(null)
  const [modules, setModules] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [isEnrolled, setIsEnrolled] = useState(false)

  useEffect(() => {
    if (!classId) return

    const saved = localStorage.getItem(STORAGE_KEY)
    const enrollSaved = localStorage.getItem(ENROLLMENTS_KEY)

    let foundClass = null
    let foundModules = []

    if (saved) {
      const all = JSON.parse(saved)
      foundClass = all.find((c: any) => c.id === classId)
      if (foundClass) {
        foundModules = (foundClass.modules || []).map((m: any, i: number) => ({
          ...m,
          exercise_count: m.exercises?.length || 0,
          order: m.order || i + 1
        }))
      }
    }

    if (enrollSaved) {
      const enrollments = JSON.parse(enrollSaved)
      const enrollment = enrollments.find((e: any) => e.classId === classId)
      if (enrollment?.status === "approved") setIsEnrolled(true)
      else if (enrollment?.status === "pending") setErrorMsg("Tu solicitud de matrícula está pendiente de aprobación.")
      else if (enrollment?.status === "rejected") setErrorMsg("Tu solicitud de matrícula fue rechazada.")
      else setErrorMsg("No estás matriculado en esta clase.")
    } else {
      setErrorMsg("No estás matriculado en esta clase.")
    }

    if (foundClass) {
      setClassData(foundClass)
      setModules(foundModules)
    } else {
      setErrorMsg("Clase no encontrada.")
    }

    setIsLoading(false)
  }, [classId])

  if (isLoading) {
    return <div className="flex justify-center items-center h-full min-h-[60vh]"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (errorMsg || !classData) {
    return (
      <div className="flex flex-col justify-center items-center h-full min-h-[60vh] gap-4">
        <AlertTriangle className="h-12 w-12 text-destructive/50" />
        <h2 className="text-2xl font-bold tracking-tight text-foreground">{errorMsg?.includes("pendiente") ? "Solicitud Pendiente" : "Acceso Denegado"}</h2>
        <p className="text-muted-foreground">{errorMsg || "Clase no encontrada."}</p>
        <div className="flex gap-3">
          <Button onClick={() => router.push('/dashboard/classes')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" /> Volver a Clases
          </Button>
          {errorMsg?.includes("pendiente") && (
            <Button onClick={() => router.push('/dashboard/classes')}>
              Ver otras clases
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <Button variant="ghost" onClick={() => router.push('/dashboard/classes')} className="text-muted-foreground hover:text-foreground -ml-4">
        <ArrowLeft className="w-4 h-4 mr-2" /> Mis Clases
      </Button>

      <div className="flex flex-col md:flex-row gap-6 items-start justify-between bg-card p-6 rounded-2xl border shadow-sm">
        <div className="space-y-4 flex-1">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium text-muted-foreground">{classData.category}</span>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                classData.difficulty === "Principiante" ? "border-emerald-500/20 text-emerald-500" :
                classData.difficulty === "Intermedio" ? "border-amber-500/20 text-amber-500" :
                "border-purple-500/20 text-purple-500"
              }`}>{classData.difficulty}</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-primary mb-2">{classData.title}</h1>
            <p className="text-muted-foreground">{classData.description}</p>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-md font-medium text-foreground">
              <CheckCircle2 className="w-4 h-4 text-green-500" /> Activo
            </span>
            <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {classData.student_count || 0} estudiantes</span>
            <span className="flex items-center gap-1"><BookOpen className="w-4 h-4" /> {modules.length} módulos</span>
          </div>
        </div>

        <div className="w-full md:w-72 bg-secondary/20 p-5 rounded-xl border border-primary/10 space-y-3">
          <div className="flex justify-between items-end mb-2">
            <span className="text-sm font-semibold">Tu Progreso</span>
            <span className="text-lg font-bold text-primary">0%</span>
          </div>
          <Progress value={0} className="h-2.5 mb-3 bg-secondary/50" />
          <Button className="w-full" size="sm" disabled={modules.length === 0}>
            <BookOpen className="w-4 h-4 mr-2" /> Comenzar
          </Button>
          <p className="text-xs text-muted-foreground text-center">Explora los módulos de esta clase</p>
        </div>
      </div>

      <Tabs defaultValue="modules" className="w-full">
        <TabsList className="grid w-full grid-cols-2 md:w-[300px]">
          <TabsTrigger value="modules">Módulos</TabsTrigger>
          <TabsTrigger value="info">Información</TabsTrigger>
        </TabsList>

        <TabsContent value="modules" className="mt-6 space-y-4">
          <h3 className="text-xl font-bold">Módulos de la Clase</h3>
          {modules.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground border-2 border-dashed rounded-xl">
              <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>El docente aún no ha agregado módulos a esta clase.</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {modules.map((mod, index) => (
                <Card key={mod.id} className="hover:bg-secondary/10 transition-colors cursor-pointer border-l-4 border-l-primary"
                  onClick={() => router.push(`/dashboard/modules/${mod.id}`)}>
                  <CardContent className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary shrink-0">
                        {mod.order}
                      </div>
                      <div>
                        <h4 className="font-semibold">{mod.title}</h4>
                        <p className="text-xs text-muted-foreground">{mod.description || "Sin descripción"} · {mod.exercise_count} ejercicios</p>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-muted-foreground" />
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="info" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Sobre esta Clase</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-1">Descripción General</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">{classData.description}</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Categoría</p>
                  <p className="text-sm font-semibold">{classData.category}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Dificultad</p>
                  <p className="text-sm font-semibold">{classData.difficulty}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Módulos</p>
                  <p className="text-sm font-semibold">{modules.length}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Estudiantes</p>
                  <p className="text-sm font-semibold">{classData.student_count || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}