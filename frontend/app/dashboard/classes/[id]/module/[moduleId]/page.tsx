"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowLeft, BookOpen, AlertTriangle } from "lucide-react"
import { TheoryWithExercises } from "@/components/interactive/theory-with-exercises"
import { toast } from "sonner"
import API from "@/lib/api"

export default function ClassModuleContentPage() {
  const params = useParams()
  const router = useRouter()
  const classId = parseInt(params.id as string, 10)
  const moduleId = parseInt(params.moduleId as string, 10)
  const [moduleData, setModuleData] = useState<any | null>(null)
  const [classTitle, setClassTitle] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  useEffect(() => {
    if (isNaN(classId) || isNaN(moduleId)) {
      setErrorMsg("ID de clase o módulo inválido")
      setIsLoading(false)
      return
    }
    loadModule()
  }, [classId, moduleId])

  async function loadModule() {
    setIsLoading(true)
    try {
      const res = await fetch(`${API}/classes/${classId}/modules/${moduleId}`, { credentials: "include" })
      const data = await res.json()
      if (data.success) {
        setModuleData(data.module)
      } else {
        setErrorMsg(data.detail || "No se pudo cargar el módulo")
        setIsLoading(false)
        return
      }
    } catch (err) {
      console.error("Error loading module:", err)
      setErrorMsg("Error de conexión")
      setIsLoading(false)
      return
    }
    // Class title is cosmetic; don't block content if it fails
    try {
      const classRes = await fetch(`${API}/classes/${classId}`, { credentials: "include" })
      const classData = await classRes.json()
      if (classData.success) {
        setClassTitle(classData.class?.title || "")
      }
    } catch (err) {
      console.error("Error loading class title:", err)
    }
    setIsLoading(false)
  }

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (errorMsg) {
    return (
      <div className="max-w-4xl mx-auto p-4">
        <Button variant="ghost" onClick={() => router.push(`/dashboard/classes/${classId}`)}>
          <ArrowLeft className="w-4 h-4 mr-2" />Volver a la clase
        </Button>
        <Card className="mt-4 border-amber-500/20 bg-amber-500/5">
          <CardContent className="flex flex-col items-center py-12 gap-4">
            <AlertTriangle className="w-12 h-12 text-amber-500" />
            <h2 className="text-xl font-bold text-center">{errorMsg}</h2>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.push(`/dashboard/classes/${classId}`)}>
          <ArrowLeft className="w-4 h-4 mr-2" />{classTitle || "Clase"}
        </Button>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <BookOpen className="w-4 h-4" />
          {moduleData?.title || "Módulo"}
        </div>
      </div>

      {moduleData ? (
        <TheoryWithExercises
          theory={moduleData.theory_content || "*Contenido teórico próximamente*"}
          exercises={moduleData.exercises || []}
          moduleId={moduleData.id}
          classModuleId={moduleData.id}
          onComplete={() => toast.success("Ejercicio completado")}
        />
      ) : (
        <div className="text-center py-16 text-muted-foreground">
          <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium">Módulo no encontrado</p>
        </div>
      )}
    </div>
  )
}
