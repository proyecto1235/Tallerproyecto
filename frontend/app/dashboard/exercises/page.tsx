"use client"

import { useState, useEffect } from "react"
import CodeMirror from "@uiw/react-codemirror"
import { python } from "@codemirror/lang-python"
import { oneDark } from "@codemirror/theme-one-dark"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Play, RotateCcw, CheckCircle2, XCircle, Zap, Code2, Terminal, Loader2, ArrowRight } from "lucide-react"

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<any[]>([])
  const [selectedExercise, setSelectedExercise] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const [code, setCode] = useState("")
  const [output, setOutput] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/exercises", {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success && data.exercises && data.exercises.length > 0) {
          setExercises(data.exercises)
          setSelectedExercise(data.exercises[0])
          setCode(data.exercises[0].instructions || "# Escribe tu código aquí\n")
          setLoading(false)
          return
        }
      } catch (e) {
        console.error("Error fetching exercises", e)
      }
      
      // Fallback a ejercicios piloto si el backend falla o está vacío
      const mockExercises = [
        { id: "ex-1", title: "Variables (Piloto)", module_title: "Programación Lógica Básica", description: "Crea una variable llamada 'velocidad' y asígnale el valor 100.", difficulty: 1, points: 10, instructions: "velocidad = 0\n# Cambia la velocidad a 100\n" },
        { id: "ex-2", title: "Bucles For (Piloto)", module_title: "Programación Lógica Básica", description: "Crea un bucle for que imprima los números del 1 al 5.", difficulty: 2, points: 20, instructions: "# Imprime los números del 1 al 5\n" },
        { id: "ex-3", title: "Funciones (Piloto)", module_title: "Programación Lógica Básica", description: "Crea una función llamada 'saludar' que imprima 'Hola Robot'.", difficulty: 3, points: 30, instructions: "def saludar():\n    # Escribe aquí\n    pass\n\nsaludar()" }
      ]
      
      setExercises(mockExercises)
      setSelectedExercise(mockExercises[0])
      setCode(mockExercises[0].instructions)
      setLoading(false)
    }
    fetchExercises()
  }, [])

  const handleSelectExercise = (ex: any) => {
    setSelectedExercise(ex)
    setCode(ex.instructions || "# Escribe tu código aquí\n")
    setOutput(null)
    setStatus("idle")
  }

  const handleRunCode = async () => {
    setStatus("running")
    setOutput("Ejecutando código...")


    try {
      const res = await fetch("http://localhost:8000/api/execute-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({ code })
      })

      const data = await res.json()

      if (data.output) {
        setOutput(data.output)
        setStatus("success")
      }

      if (data.error) {
        setOutput(prev => prev ? prev + `\nError: ${data.error}` : `Error: ${data.error}`)
        setStatus("error")
      }
    } catch (error) {
      setOutput("Error de conexión con el servidor")
      setStatus("error")
    }
  }

  const handleReset = () => {
    setCode(selectedExercise?.instructions || "# Escribe tu código aquí\n")
    setOutput(null)
    setStatus("idle")
  }

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (exercises.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <h2 className="text-2xl font-bold">No hay ejercicios disponibles</h2>
        <p className="text-muted-foreground">Vuelve más tarde cuando los profesores agreguen contenido.</p>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">

      {/* Ejercicios Menu / Header */}
      <div className="flex gap-2 overflow-x-auto pb-2 border-b border-border">
        {exercises.map(ex => (
          <Button
            key={ex.id}
            variant={selectedExercise?.id === ex.id ? "default" : "outline"}
            size="sm"
            onClick={() => handleSelectExercise(ex)}
            className="whitespace-nowrap"
          >
            {ex.title}
          </Button>
        ))}
      </div>

      <div className="flex flex-col md:flex-row gap-6 flex-1 overflow-hidden">
        {/* Panel Izquierdo: Instrucciones */}
        <div className="w-full md:w-1/3 flex flex-col gap-4 h-full">
          <Card className="flex-1 flex flex-col neo-shadow border-primary/20 overflow-hidden">
            <CardHeader className="bg-primary/5 pb-4 border-b shrink-0">
              <div className="text-xs text-muted-foreground mb-1 uppercase tracking-wider">{selectedExercise?.module_title}</div>
              <CardTitle className="text-xl flex items-center gap-2 text-primary">
                <Zap className="w-5 h-5 shrink-0" />
                <span className="truncate">{selectedExercise?.title}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6 flex-1 overflow-y-auto">
              <div className="prose dark:prose-invert prose-sm">
                <p className="text-base leading-relaxed whitespace-pre-wrap">{selectedExercise?.description}</p>

                <div className="mt-8 border-t border-border/50 pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                      Dificultad {selectedExercise?.difficulty}/5
                    </span>
                    <span className="text-sm font-bold text-primary flex items-center gap-1">
                      <Zap className="w-4 h-4" />
                      +{selectedExercise?.points} pts
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Panel Derecho: Editor y Consola */}
        <div className="w-full md:w-2/3 flex flex-col gap-4 h-full">

          {/* Toolbar */}
          <div className="flex items-center justify-between bg-card border rounded-lg p-2 shadow-sm">
            <div className="flex items-center gap-2 px-3 text-sm font-semibold text-muted-foreground">
              <Code2 className="w-4 h-4" />
              main.py
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                disabled={status === "running"}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reiniciar
              </Button>
              <Button
                size="sm"
                onClick={handleRunCode}
                disabled={status === "running"}
                className="bg-green-600 hover:bg-green-700 text-white font-bold"
              >
                <Play className="w-4 h-4 mr-2" />
                {status === "running" ? "Ejecutando..." : "Ejecutar Código"}
              </Button>
            </div>
          </div>

          {/* Editor */}
          <div className="flex-1 border rounded-xl overflow-hidden bg-[#282c34] shadow-inner relative">
            <CodeMirror
              value={code}
              height="100%"
              theme={oneDark}
              extensions={[python()]}
              onChange={(value) => setCode(value)}
              className="text-base h-full"
              style={{ height: '100%' }}
            />
          </div>

          {/* Console / Output */}
          <div className={`h-48 rounded-xl border-2 flex flex-col overflow-hidden transition-colors ${status === 'success' ? 'border-green-500/50 bg-green-500/5' :
              status === 'error' ? 'border-red-500/50 bg-red-500/5' :
                'border-border bg-card'
            }`}>
            <div className="bg-muted/50 border-b px-4 py-2 flex items-center gap-2 text-sm font-bold">
              <Terminal className="w-4 h-4" />
              Terminal de Salida
              {status === 'success' && <span className="ml-auto text-green-500 flex items-center gap-1"><CheckCircle2 className="w-4 h-4" /> ¡Correcto!</span>}
              {status === 'error' && <span className="ml-auto text-red-500 flex items-center gap-1"><XCircle className="w-4 h-4" /> Error</span>}
            </div>
            <div className="p-4 font-mono text-sm overflow-y-auto whitespace-pre-wrap flex-1">
              {output || <span className="text-muted-foreground italic">El resultado de tu código aparecerá aquí...</span>}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
