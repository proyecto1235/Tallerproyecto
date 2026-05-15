"use client"

import { useState, useEffect } from "react"
import { ModuleCard } from "@/components/dashboard/module-card"
import { Map, BookOpen, Trophy, Loader2, Code, ChevronRight } from "lucide-react"
import { useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

const GLOBAL_MODULES = [
  { id: "g-1", title: "Introducción a Python", description: "Conoce el lenguaje, escribe tu primer programa y entiende la sintaxis básica.", level: 1, difficulty: "Principiante", lessons: 3, status: "in-progress", progress: 30 },
  { id: "g-2", title: "Variables y Tipos de Datos", description: "Aprende a almacenar información en variables y a trabajar con números y texto.", level: 2, difficulty: "Principiante", lessons: 3, status: "completed", progress: 100 },
  { id: "g-3", title: "Estructuras de Control", description: "Toma decisiones en tu código con if, elif y else.", level: 3, difficulty: "Intermedio", lessons: 2, status: "locked", progress: 0 },
  { id: "g-4", title: "Bucles y Repeticiones", description: "Domina for y while para automatizar tareas repetitivas.", level: 4, difficulty: "Intermedio", lessons: 2, status: "locked", progress: 0 },
  { id: "g-5", title: "Funciones", description: "Crea bloques de código reutilizables y organiza mejor tus programas.", level: 5, difficulty: "Avanzado", lessons: 3, status: "locked", progress: 0 },
  { id: "g-6", title: "Listas y Tuplas", description: "Trabaja con colecciones de datos y entiende sus diferencias.", level: 6, difficulty: "Intermedio", lessons: 2, status: "locked", progress: 0 },
  { id: "g-7", title: "Diccionarios y Sets", description: "Almacena datos con clave-valor y conjuntos sin duplicados.", level: 7, difficulty: "Intermedio", lessons: 2, status: "locked", progress: 0 },
  { id: "g-8", title: "Manejo de Archivos", description: "Lee y escribe archivos de texto y CSV con Python.", level: 8, difficulty: "Avanzado", lessons: 2, status: "locked", progress: 0 },
  { id: "g-9", title: "Módulos y Paquetes", description: "Organiza tu código en módulos reutilizables y usa pip.", level: 9, difficulty: "Avanzado", lessons: 2, status: "locked", progress: 0 },
  { id: "g-10", title: "Proyecto Final: Robot Autónomo", description: "Aplica todo lo aprendido para programar un robot virtual que navega solo.", level: 10, difficulty: "Avanzado", lessons: 3, status: "locked", progress: 0 },
]

const difficultyColors: Record<string, string> = {
  Principiante: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
  Intermedio: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  Avanzado: "bg-purple-500/10 text-purple-500 border-purple-500/20",
}

export default function ModulesPage() {
  const router = useRouter()
  const [modules, setModules] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/modules", { credentials: 'include' })
        const data = await res.json()
        if (data.success && data.modules) {
          const global = data.modules.filter((m: any) => m.is_global).sort((a: any, b: any) => a.order - b.order)
          if (global.length > 0) {
            // Fetch enrolled modules to get progress
            let enrolledMap: Record<string, any> = {}
            try {
              const enrRes = await fetch("http://localhost:8000/api/modules/enrolled", { credentials: 'include' })
              const enrData = await enrRes.json()
              if (enrData.success) {
                for (const m of enrData.modules) {
                  enrolledMap[m.id.toString()] = {
                    enrollment_status: m.enrollment_status,
                    progress: m.percentage || 0
                  }
                }
              }
            } catch (_) {}

            const mapped = global.map((m: any) => {
              const id = m.id.toString()
              const enrolled = enrolledMap[id]
              let status: string
              let progress: number

              if (enrolled) {
                if (enrolled.enrollment_status === "completed") {
                  status = "completed"; progress = 100
                } else {
                  status = "in-progress"; progress = enrolled.progress || 0
                }
              } else {
                // Check if previous module is completed to determine lock status
                status = "locked"; progress = 0
              }

              return {
                id,
                title: m.title,
                description: m.description,
                level: m.order || 0,
                difficulty: m.difficulty || "Principiante",
                lessons: m.lesson_count || 3,
                status,
                progress,
              }
            })

            // Fix lock status: first unlockable module should be in-progress or available
            let foundActive = false
            for (const mod of mapped) {
              if (mod.status === "in-progress") {
                foundActive = true; break
              }
              if (mod.status === "completed") continue
              if (!foundActive) {
                mod.status = "in-progress"
                foundActive = true
              }
            }

            setModules(mapped)
            setLoading(false)
            return
          }
        }
      } catch (_) {}

      setModules(GLOBAL_MODULES)
      setLoading(false)
    }
    fetchModules()
  }, [])

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  const completed = modules.filter(m => m.status === 'completed').length
  const inProgress = modules.filter(m => m.status === 'in-progress').length

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary w-fit">
          <Map className="w-4 h-4" />
          <span className="text-sm font-bold uppercase tracking-wider">Ruta Gratuita</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Aprende Python desde Cero</h1>
        <p className="text-muted-foreground text-lg max-w-2xl">
          Un roadmap completo y gratuito para llevar tu conocimiento de Python desde principiante hasta nivel intermedio. ¡10 módulos con teoría y ejercicios interactivos!
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-primary/10 p-3 rounded-lg text-primary"><BookOpen className="w-6 h-6" /></div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">Módulos</p>
              <p className="text-2xl font-bold">{modules.length}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-green-500/20 bg-green-500/5">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-green-500/10 p-3 rounded-lg text-green-500"><Trophy className="w-6 h-6" /></div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">Completados</p>
              <p className="text-2xl font-bold">{completed}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-amber-500/10 p-3 rounded-lg text-amber-500"><Code className="w-6 h-6" /></div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">En Progreso</p>
              <p className="text-2xl font-bold">{inProgress}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="relative mt-8">
        <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-1 bg-border -translate-x-1/2 rounded-full" />

        <div className="space-y-6 relative">
          {modules.map((mod, index) => {
            const isLeft = index % 2 === 0
            return (
              <div key={mod.id} className={`flex flex-col lg:flex-row items-center gap-6 ${isLeft ? '' : 'lg:flex-row-reverse'}`}>
                <div className="flex-1 w-full lg:w-1/2" />

                <div className="hidden lg:flex absolute left-1/2 -translate-x-1/2 w-14 h-14 rounded-full border-4 border-background bg-card shadow-sm items-center justify-center z-10">
                  <span className={`font-bold text-lg ${mod.status === 'completed' ? 'text-green-500' : mod.status === 'in-progress' ? 'text-primary' : 'text-muted-foreground'}`}>
                    {mod.level}
                  </span>
                </div>

                <div className="flex-1 w-full lg:w-1/2">
                  <div
                    onClick={() => mod.status !== 'locked' && router.push(`/dashboard/modules/${mod.id}`)}
                    className={`bg-card border rounded-xl p-5 transition-all duration-300 ${
                      mod.status === 'locked'
                        ? 'opacity-60 cursor-not-allowed'
                        : 'hover:shadow-lg hover:-translate-y-1 cursor-pointer'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Nivel {mod.level}</span>
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${difficultyColors[mod.difficulty] || difficultyColors.Principiante}`}>
                            {mod.difficulty}
                          </span>
                        </div>
                        <h3 className="font-bold text-xl">{mod.title}</h3>
                      </div>
                      <div className={`p-2 rounded-full shrink-0 ${
                        mod.status === 'completed' ? 'bg-green-500/10 text-green-500' :
                        mod.status === 'in-progress' ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                      }`}>
                        {mod.status === 'completed' ? <Trophy className="h-5 w-5" /> :
                         mod.status === 'locked' ? <BookOpen className="h-5 w-5" /> :
                         <Code className="h-5 w-5" />}
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{mod.description}</p>

                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                      <span>{mod.lessons} lecciones</span>
                      {mod.status === 'locked' && <span className="text-muted-foreground/60">Completa el nivel anterior</span>}
                    </div>

                    {mod.status !== 'locked' && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs font-medium">
                          <span>Progreso</span>
                          <span>{mod.progress}%</span>
                        </div>
                        <Progress value={mod.progress} className="h-2" />
                      </div>
                    )}

                    {mod.status !== 'locked' && (
                      <Button size="sm" className="w-full mt-3 group" variant={mod.status === 'completed' ? 'outline' : 'default'}>
                        {mod.status === 'completed' ? 'Repasar' : 'Continuar'}
                        <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}