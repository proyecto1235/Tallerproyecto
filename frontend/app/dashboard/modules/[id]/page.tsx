"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowLeft, BookOpen, CheckCircle2, Lock, Code, ChevronDown, ChevronRight, Trophy } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { InlineExercise } from "@/components/interactive/InlineExercise"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { toast } from "sonner"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export default function ModuleViewPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const numericId = parseInt(id || "0", 10)

  const [moduleData, setModuleData] = useState<any>(null)
  const [lessons, setLessons] = useState<any[]>([])
  const [progress, setProgress] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeLesson, setActiveLesson] = useState<string | null>(null)
  const [completing, setCompleting] = useState(false)
  const [completedLessonIds, setCompletedLessonIds] = useState<Set<number>>(new Set())
  const [unlockedLessons, setUnlockedLessons] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!numericId) return
    loadData()
  }, [numericId])

  async function loadData() {
    setIsLoading(true)
    setError(null)
    try {
      const [modRes, progRes, lessRes] = await Promise.all([
        fetch(`${API_URL}/modules/${numericId}`, { credentials: "include" }),
        fetch(`${API_URL}/modules/${numericId}/progress`, { credentials: "include" }),
        fetch(`${API_URL}/modules/${numericId}/lessons`, { credentials: "include" }),
      ])
      const modData = await modRes.json()
      const progData = await progRes.json()
      const lessData = await lessRes.json()

      if (!modData.success) { setError("Módulo no encontrado"); return }
      setModuleData(modData.module)
      setProgress(progData.progress)

      if (lessData.success && lessData.lessons) {
        setLessons(lessData.lessons)
        const completed = new Set<number>()
        const unlocked = new Set<number>()
        lessData.lessons.forEach((l: any, i: number) => {
          if (l.completed) completed.add(l.id)
          if (i === 0 || completed.has(lessData.lessons[i - 1]?.id)) unlocked.add(l.id)
        })
        setCompletedLessonIds(completed)
        setUnlockedLessons(unlocked)
      }
    } catch (e) {
      setError("Error al cargar el módulo")
    } finally {
      setIsLoading(false)
    }
  }

  function refreshLessonData() {
    fetch(`${API_URL}/modules/${numericId}/lessons`, { credentials: "include" })
      .then(r => r.json())
      .then(data => {
        if (data.success && data.lessons) {
          setLessons(data.lessons)
          const completed = new Set<number>()
          const unlocked = new Set<number>()
          data.lessons.forEach((l: any, i: number) => {
            if (l.completed) completed.add(l.id)
            if (i === 0) unlocked.add(l.id)
            else if (completed.has(data.lessons[i - 1]?.id)) unlocked.add(l.id)
          })
          setCompletedLessonIds(completed)
          setUnlockedLessons(unlocked)
          setProgress((prev: any) => prev ? {
            ...prev,
            completed_exercises: data.lessons.reduce((s: number, l: any) => s + l.passed_exercises, 0),
            total_exercises: data.lessons.reduce((s: number, l: any) => s + l.total_exercises, 0),
            percentage: data.total_lessons > 0 ? Math.round(data.completed_lessons / data.total_lessons * 100) : 0,
          } : prev)
        }
      })
      .catch(() => {})
  }

  async function handleCompleteModule() {
    setCompleting(true)
    try {
      const res = await fetch(`${API_URL}/modules/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ module_id: numericId })
      })
      const data = await res.json()
      if (data.success) {
        toast.success(`¡Módulo completado! +${data.points_earned || 50} pts`)
        refreshLessonData()
      } else {
        toast.error(data.message || "Error al completar módulo")
      }
    } catch (e) {
      toast.error("Error de conexión")
    } finally {
      setCompleting(false)
    }
  }

  function toggleLesson(lessonId: number) {
    if (!unlockedLessons.has(lessonId)) return
    setActiveLesson(prev => prev === String(lessonId) ? null : String(lessonId))
  }

  function scrollToLesson(lessonId: number) {
    setActiveLesson(String(lessonId))
    setTimeout(() => {
      document.getElementById(`lesson-${lessonId}`)?.scrollIntoView({ behavior: "smooth", block: "start" })
    }, 100)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !moduleData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-lg font-semibold text-red-500">{error || "Módulo no encontrado"}</p>
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" /> Volver
        </Button>
      </div>
    )
  }

  const allLessonsCompleted = completedLessonIds.size > 0 && completedLessonIds.size >= lessons.length
  const progressPercent = lessons.length > 0 ? Math.round((completedLessonIds.size / lessons.length) * 100) : 0
  const totalExercises = lessons.reduce((s, l) => s + l.total_exercises, 0)
  const completedExercises = lessons.reduce((s, l) => s + l.passed_exercises, 0)

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard/modules")}>
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold">{moduleData.title}</h1>
          <p className="text-muted-foreground">{moduleData.description}</p>
        </div>
      </div>

      <Card className="neo-shadow border-primary/20">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row justify-between gap-4">
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-4 text-sm">
                <span className="px-2 py-1 rounded bg-primary/10 text-primary font-medium">{moduleData.difficulty || "Principiante"}</span>
                <span className="text-muted-foreground">{lessons.length} lecciones</span>
                <span className="text-muted-foreground">{totalExercises} ejercicios</span>
              </div>
              <Progress value={progressPercent} className="h-2" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{completedExercises}/{totalExercises} ejercicios completados</span>
                <span>{completedLessonIds.size}/{lessons.length} lecciones</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-center px-4 py-2 rounded-lg bg-primary/5">
                <p className="text-2xl font-bold text-primary">{progressPercent}%</p>
                <p className="text-xs text-muted-foreground">progreso</p>
              </div>
              <Button
                size="lg"
                className="bg-primary hover:bg-primary/90"
                disabled={!allLessonsCompleted || completing}
                onClick={handleCompleteModule}
              >
                {completing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Trophy className="w-4 h-4 mr-2" />}
                {completing ? "Completando..." : allLessonsCompleted ? "Completar Módulo" : "🔒 Completa todas las lecciones"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {lessons.map((lesson, index) => {
        const isUnlocked = unlockedLessons.has(lesson.id)
        const isCompleted = completedLessonIds.has(lesson.id)
        const isActive = activeLesson === String(lesson.id)
        const prevCompleted = index === 0 || completedLessonIds.has(lessons[index - 1]?.id)

        return (
          <div key={lesson.id} id={`lesson-${lesson.id}`}>
            <Card
              className={cn(
                "neo-shadow border-primary/20 overflow-hidden transition-all",
                !isUnlocked && "opacity-50",
                isActive && "ring-2 ring-primary/30"
              )}
            >
              <div
                className={cn(
                  "flex items-center justify-between px-4 py-3 cursor-pointer border-b transition-colors",
                  isActive ? "bg-primary/10 border-primary/30" : "bg-card hover:bg-muted/50 border-transparent"
                )}
                onClick={() => toggleLesson(lesson.id)}
              >
                <div className="flex items-center gap-3">
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : !isUnlocked ? (
                    <Lock className="w-5 h-5 text-muted-foreground" />
                  ) : (
                    <BookOpen className="w-5 h-5 text-primary" />
                  )}
                  <div>
                    <span className="font-semibold">
                      Lección {lesson.order}: {lesson.title}
                    </span>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                      <span>{lesson.passed_exercises}/{lesson.total_exercises} ejercicios</span>
                      {!isUnlocked && <span>• Bloqueada</span>}
                      {isCompleted && <span className="text-green-500">• Completada</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isUnlocked && !isCompleted && lesson.passed_exercises === lesson.total_exercises && lesson.total_exercises > 0 && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-green-600 border-green-300"
                      onClick={(e) => {
                        e.stopPropagation()
                        if (index + 1 < lessons.length) {
                          const nextId = lessons[index + 1].id
                          setUnlockedLessons(prev => new Set([...prev, nextId]))
                          scrollToLesson(nextId)
                        }
                      }}
                    >
                      Continuar <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  )}
                  {isActive ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </div>
              </div>

              {isActive && (
                <div className="p-4 md:p-6 space-y-6">
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {lesson.theory || "*Contenido teórico próximamente*"}
                    </ReactMarkdown>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-semibold flex items-center gap-2">
                      <Code className="w-4 h-4" /> Ejercicios
                    </h4>
                    {(lesson.exercises || []).map((ex: any) => (
                      <InlineExercise
                        key={ex.id}
                        exercise={ex}
                        moduleId={numericId}
                        onComplete={refreshLessonData}
                      />
                    ))}
                    {(!lesson.exercises || lesson.exercises.length === 0) && (
                      <p className="text-sm text-muted-foreground italic">No hay ejercicios en esta lección</p>
                    )}
                  </div>

                  {isCompleted && index + 1 < lessons.length && (
                    <div className="flex justify-center pt-2">
                      <Button
                        variant="default"
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => {
                          const nextId = lessons[index + 1].id
                          setUnlockedLessons(prev => new Set([...prev, nextId]))
                          scrollToLesson(nextId)
                        }}
                      >
                        Continuar a siguiente lección <ChevronRight className="w-4 h-4 ml-2" />
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </Card>

            {!isActive && index + 1 < lessons.length && !isCompleted && (
              <div className="flex justify-center -my-2 relative z-10">
                <div className="bg-muted rounded-full p-1 shadow-sm">
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                </div>
              </div>
            )}
          </div>
        )
      })}

      {allLessonsCompleted && (
        <Card className="neo-shadow-success border-green-400 bg-green-50 dark:bg-green-950/20">
          <CardContent className="py-6 text-center">
            <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <h3 className="text-xl font-bold text-green-700 dark:text-green-400">¡Todas las lecciones completadas!</h3>
            <p className="text-sm text-muted-foreground mt-1">Haz clic en "Completar Módulo" para finalizar y ganar puntos.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
