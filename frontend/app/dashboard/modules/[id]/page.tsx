"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowLeft, BookOpen } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { InlineExercise } from "@/components/interactive/InlineExercise"

export default function ModuleViewPage() {
  const params = useParams()
  const router = useRouter()
  const [module, setModule] = useState<any>(null)
  const [exercises, setExercises] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchModule = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/modules/${params.id}`, {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          setModule(data.module)
          // Fetch exercises too
          const exRes = await fetch(`http://localhost:8000/api/modules/${params.id}/exercises`, {
            credentials: 'include'
          })
          const exData = await exRes.json()
          if (exData.success) {
            setExercises(exData.exercises)
          }
        }
      } catch (error) {
        console.error("Error fetching module", error)
      } finally {
        setIsLoading(false)
      }
    }
    
    if (params.id) fetchModule()
  }, [params.id])

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!module) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <h2 className="text-2xl font-bold">Módulo no encontrado</h2>
        <Button onClick={() => router.back()} variant="outline">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Button variant="ghost" onClick={() => router.back()} className="mb-4">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Volver a clases
      </Button>

      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
          <BookOpen className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{module.title}</h1>
          <p className="text-muted-foreground">Material de estudio</p>
        </div>
      </div>

      <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
        <CardContent className="p-6">
          <div className="prose prose-invert max-w-none">
            {module.theory_content ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{module.theory_content}</ReactMarkdown>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{module.description || "No hay teoría disponible para este módulo."}</ReactMarkdown>
            )}
          </div>
          
          {exercises.length > 0 && (
            <div className="mt-12 space-y-12 border-t border-border pt-8">
              {exercises.map((exercise, index) => (
                <div key={exercise.id} className="space-y-6">
                  {exercise.theory_content && (
                    <div className="prose prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{exercise.theory_content}</ReactMarkdown>
                    </div>
                  )}
                  <InlineExercise exercise={exercise} />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
