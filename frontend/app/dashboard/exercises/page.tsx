"use client"

import { useState, useEffect } from "react"
import CodeMirror from "@uiw/react-codemirror"
import { python } from "@codemirror/lang-python"
import { oneDark } from "@codemirror/theme-one-dark"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Play, RotateCcw, CheckCircle2, XCircle, Zap, Code2, Terminal, Loader2, Eye, Trophy } from "lucide-react"
import { toast } from "sonner"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<any[]>([])
  const [selectedExercise, setSelectedExercise] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const [code, setCode] = useState("")
  const [output, setOutput] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")
  const [attempts, setAttempts] = useState(0)
  const [passed, setPassed] = useState(false)
  const [canViewSolution, setCanViewSolution] = useState(false)
  const [showSolution, setShowSolution] = useState(false)
  const [solution, setSolution] = useState<string | null>(null)
  const [solutionOutput, setSolutionOutput] = useState<string | null>(null)
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const res = await fetch(`${API_URL}/exercises`, {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success && data.exercises && data.exercises.length > 0) {
          const mapped = data.exercises.map((e: any) => ({
            ...e,
            _id: e.id?.toString() || `ex-${Math.random()}`
          }))
          setExercises(mapped)
          setSelectedExercise(mapped[0])
          setCode(mapped[0].instructions || "# Escribe tu código aquí\n")
          setLoading(false)
          return
        }
      } catch (e) {
        console.error("Error fetching exercises", e)
      }

      const mockExercises = [
        { _id: "ex-1", id: "ex-1", title: "Variables (Piloto)", module_title: "Programación Lógica Básica", description: "Crea una variable llamada 'velocidad' y asígnale el valor 100.", difficulty: 1, points: 10, instructions: "velocidad = 0\n# Cambia la velocidad a 100\n" },
        { _id: "ex-2", id: "ex-2", title: "Bucles For (Piloto)", module_title: "Programación Lógica Básica", description: "Crea un bucle for que imprima los números del 1 al 5.", difficulty: 2, points: 20, instructions: "# Imprime los números del 1 al 5\n" },
        { _id: "ex-3", id: "ex-3", title: "Funciones (Piloto)", module_title: "Programación Lógica Básica", description: "Crea una función llamada 'saludar' que imprima 'Hola Robot'.", difficulty: 3, points: 30, instructions: "def saludar():\n    # Escribe aquí\n    pass\n\nsaludar()" }
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
    setAttempts(0)
    setPassed(false)
    setCanViewSolution(false)
    setShowSolution(false)
    setSolution(null)
    setSolutionOutput(null)
  }

  const handleRunCode = async () => {
    if (passed) return
    setStatus("running")
    setOutput("Ejecutando código...")
    setShowSolution(false)

    try {
      const res = await fetch(`${API_URL}/exercises/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({
          exercise_id: selectedExercise.id,
          code: code,
          module_id: selectedExercise.module_id || 0
        })
      })

      const data = await res.json()

      let outputText = data.output || ""

      if (data.passed) {
        setPassed(true)
        setStatus("success")
        setCompletedIds(prev => new Set(prev).add(selectedExercise._id))
        outputText += "\n\n✅ ¡Ejercicio completado correctamente!"
        toast.success(`¡Ejercicio completado! +${data.points_earned || 0} pts`)
      } else {
        setStatus("error")
        setAttempts(data.attempts || attempts + 1)
        if (data.error) outputText += `\nError: ${data.error}`

        if (data.can_view_solution) {
          setCanViewSolution(true)
          setSolution(data.solution)
        }
      }

      setOutput(outputText)
      setSolutionOutput(data.solution || null)
    } catch (error) {
      setOutput("Error de conexión con el servidor")
      setStatus("error")
    }
  }

  const handleShowSolution = () => {
    setShowSolution(true)
  }

  const handleReset = () => {
    setCode(selectedExercise?.instructions || "# Escribe tu código aquí\n")
    setOutput(null)
    setStatus("idle")
    setAttempts(0)
    setShowSolution(false)
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
      <div className="flex gap-2 overflow-x-auto pb-2 border-b border-border">
        {exercises.map(ex => (
          <Button
            key={ex._id}
            variant={selectedExercise?._id === ex._id ? "default" : "outline"}
            size="sm"
            onClick={() => handleSelectExercise(ex)}
            className="whitespace-nowrap"
          >
            {completedIds.has(ex._id) && <CheckCircle2 className="w-3 h-3 mr-1 text-green-500" />}
            {ex.title}
          </Button>
        ))}
      </div>

      <div className="flex flex-col md:flex-row gap-6 flex-1 overflow-hidden">
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
                {attempts > 0 && !passed && (
                  <div className="mt-4 p-3 bg-amber-500/10 rounded-lg border border-amber-500/20">
                    <p className="text-sm font-medium text-amber-600">Intentos: {attempts}/3</p>
                    {canViewSolution && (
                      <Button size="sm" variant="outline" className="mt-2 w-full text-amber-600 border-amber-500/30" onClick={handleShowSolution}>
                        <Eye className="w-4 h-4 mr-2" /> Ver Solución
                      </Button>
                    )}
                  </div>
                )}
                {passed && (
                  <div className="mt-4 p-3 bg-green-500/10 rounded-lg border border-green-500/20 flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-green-500" />
                    <span className="font-bold text-green-600">¡Completado!</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="w-full md:w-2/3 flex flex-col gap-4 h-full">
          <div className="flex items-center justify-between bg-card border rounded-lg p-2 shadow-sm">
            <div className="flex items-center gap-2 px-3 text-sm font-semibold text-muted-foreground">
              <Code2 className="w-4 h-4" />
              main.py
            </div>
            <div className="flex items-center gap-2">
              {showSolution && solution && (
                <div className="text-xs text-amber-500 font-bold px-2">Mostrando solución</div>
              )}
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
                disabled={status === "running" || passed}
                className={passed ? "bg-green-600" : "bg-green-600 hover:bg-green-700 text-white font-bold"}
              >
                {passed ? <CheckCircle2 className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                {status === "running" ? "Ejecutando..." : passed ? "Completado" : "Ejecutar Código"}
              </Button>
            </div>
          </div>

          {showSolution && solution ? (
            <div className="flex-1 border rounded-xl overflow-hidden bg-amber-500/5 border-amber-500/30">
              <div className="bg-amber-500/10 px-4 py-2 border-b border-amber-500/20 flex items-center gap-2">
                <Eye className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-bold text-amber-600">Solución</span>
              </div>
              <pre className="p-4 font-mono text-sm whitespace-pre-wrap overflow-auto h-full">{solution}</pre>
            </div>
          ) : (
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
          )}

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