"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowLeft, BookOpen } from "lucide-react"
import ReactMarkdown from "react-markdown"

export default function ModuleViewPage() {
  const params = useParams()
  const router = useRouter()
  const [module, setModule] = useState<any>(null)
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
            <ReactMarkdown>{module.description || "No hay contenido disponible para este módulo."}</ReactMarkdown>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
