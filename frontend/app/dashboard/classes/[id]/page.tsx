"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, ArrowLeft, BookOpen, PlayCircle, Trophy, AlertTriangle, FileText, CheckCircle2 } from "lucide-react"

export default function ClassDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const classId = params.id as string

  const [classData, setClassData] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  useEffect(() => {
    if (!classId) return

    const fetchClassDetails = async () => {
      try {
        // Obtenemos los módulos en los que el usuario está matriculado
        const res = await fetch("http://localhost:8000/api/modules/enrolled", {
          credentials: 'include'
        })
        const data = await res.json()

        if (data.success && data.modules) {
          // Buscamos el curso específico en la lista de matriculados
          const currentClass = data.modules.find((m: any) => m.id.toString() === classId)
          if (currentClass) {
            setClassData(currentClass)
            setIsLoading(false)
            return
          }
        }
      } catch (error) {
        console.error("Error fetching class details:", error)
      }
      
      // Fallback: Si no hay backend o estamos usando el curso piloto
      if (classId.startsWith("piloto-")) {
        setClassData({
          id: classId,
          title: classId === "piloto-1" ? "Fundamentos de Robótica" : "Clase Piloto de Prueba",
          description: "Bienvenido a tu clase piloto. Aquí aprenderás los conceptos clave interactuando con teoría y ejercicios.",
          order: 1,
          enrollment_status: "in-progress",
          enrolled_at: new Date().toISOString()
        })
        setErrorMsg(null)
      } else {
        setErrorMsg("No tienes acceso a este curso o el backend no está disponible.")
      }
      setIsLoading(false)
    }

    fetchClassDetails()
  }, [classId])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (errorMsg || !classData) {
    return (
      <div className="flex flex-col justify-center items-center h-full min-h-[60vh] gap-4">
        <AlertTriangle className="h-12 w-12 text-destructive/50" />
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Acceso Denegado</h2>
        <p className="text-muted-foreground">{errorMsg || "Curso no encontrado."}</p>
        <Button onClick={() => router.push('/dashboard/classes')} variant="outline" className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> Volver a Mis Clases
        </Button>
      </div>
    )
  }

  // Mock de temas/lecciones para mostrar algo visual. 
  // En una versión real esto vendría en classData.lessons o similar.
  const lessons = [
    { id: 1, title: "Introducción y Conceptos Básicos", type: "video", duration: "15 min", completed: true },
    { id: 2, title: "Material de Lectura", type: "document", duration: "10 min", completed: true },
    { id: 3, title: "Primer Ejercicio Práctico", type: "exercise", duration: "25 min", completed: false },
    { id: 4, title: "Reto Final del Módulo", type: "challenge", duration: "45 min", completed: false }
  ]

  const getLessonIcon = (type: string) => {
    switch (type) {
      case "video": return <PlayCircle className="w-5 h-5 text-blue-500" />
      case "document": return <FileText className="w-5 h-5 text-orange-500" />
      case "exercise": return <BookOpen className="w-5 h-5 text-green-500" />
      case "challenge": return <Trophy className="w-5 h-5 text-purple-500" />
      default: return <BookOpen className="w-5 h-5" />
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      {/* Botón Volver */}
      <Button
        variant="ghost"
        onClick={() => router.push('/dashboard/classes')}
        className="text-muted-foreground hover:text-foreground -ml-4"
      >
        <ArrowLeft className="w-4 h-4 mr-2" /> Mis Clases
      </Button>

      {/* Header del Curso */}
      <div className="flex flex-col md:flex-row gap-6 items-start justify-between bg-card p-6 rounded-2xl border shadow-sm">
        <div className="space-y-4 flex-1">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-primary mb-2">{classData.title}</h1>
            <p className="text-muted-foreground">{classData.description}</p>
          </div>

          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-md font-medium text-foreground">
              <CheckCircle2 className="w-4 h-4 text-primary" /> Activo
            </span>
            <span>Matriculado: {new Date(classData.enrolled_at || Date.now()).toLocaleDateString('es-ES')}</span>
          </div>
        </div>

        <div className="w-full md:w-72 bg-secondary/20 p-5 rounded-xl border border-primary/10">
          <div className="flex justify-between items-end mb-2">
            <span className="text-sm font-semibold">Tu Progreso</span>
            <span className="text-lg font-bold text-primary">45%</span>
          </div>
          <Progress value={45} className="h-2.5 mb-3 bg-secondary/50" />
          <p className="text-xs text-muted-foreground text-center">Continúa aprendiendo para completar este módulo.</p>
        </div>
      </div>

      {/* Contenido del Curso */}
      <Tabs defaultValue="content" className="w-full">
        <TabsList className="grid w-full grid-cols-2 md:w-[400px]">
          <TabsTrigger value="content">Contenido del Curso</TabsTrigger>
          <TabsTrigger value="info">Información</TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="mt-6 space-y-4">
          <h3 className="text-xl font-bold">Lecciones y Actividades</h3>
          <div className="grid gap-3">
            {lessons.map((lesson) => (
              <Card key={lesson.id} className={`transition-colors hover:bg-secondary/10 cursor-pointer ${lesson.completed ? 'border-l-4 border-l-green-500 opacity-80' : 'border-l-4 border-l-primary'}`}>
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-secondary/30 rounded-lg">
                      {getLessonIcon(lesson.type)}
                    </div>
                    <div>
                      <h4 className={`font-semibold ${lesson.completed ? 'text-muted-foreground line-through decoration-muted-foreground/50' : 'text-foreground'}`}>
                        {lesson.title}
                      </h4>
                      <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                        {lesson.duration}
                      </p>
                    </div>
                  </div>

                  <div>
                    {lesson.completed ? (
                      <span className="flex items-center gap-1.5 text-xs font-semibold text-green-500 bg-green-500/10 px-2.5 py-1 rounded-full">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Completado
                      </span>
                    ) : (
                      <Button size="sm" variant={lesson.id === 3 ? "default" : "secondary"} className="rounded-full px-5">
                        {lesson.id === 3 ? "Continuar" : "Iniciar"}
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="info" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Sobre este Módulo</CardTitle>
              <CardDescription>Detalles técnicos y objetivos de aprendizaje.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-1">Descripción General</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {classData.description}
                  Este módulo está diseñado para proveer una base sólida sobre el tema, con ejercicios prácticos y retos interactivos.
                </p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Nivel</p>
                  <p className="text-sm font-semibold">{classData.order ? `Nivel ${classData.order}` : "Básico"}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Estado</p>
                  <p className="text-sm font-semibold capitalize">{classData.enrollment_status}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">ID</p>
                  <p className="text-sm font-semibold font-mono">{classData.id}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
