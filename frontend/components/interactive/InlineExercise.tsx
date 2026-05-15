"use client"

import React, { useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { Play, Terminal, CheckCircle2, XCircle, Eye, RotateCcw, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { toast } from 'sonner'

export function InlineExercise({ exercise, moduleId, onComplete }: { exercise: any; moduleId?: number; onComplete?: () => void }) {
  const [code, setCode] = useState(exercise.instructions || "# Escribe tu código aquí\n")
  const [output, setOutput] = useState<string>("")
  const [isExecuting, setIsExecuting] = useState(false)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")
  const [attempts, setAttempts] = useState(0)
  const [canViewSolution, setCanViewSolution] = useState(false)
  const [showSolution, setShowSolution] = useState(false)
  const [passed, setPassed] = useState(false)
  const [solution, setSolution] = useState<string | null>(null)

  const handleRun = async () => {
    if (isExecuting || passed) return
    setIsExecuting(true)
    setStatus("running")
    setOutput("Ejecutando código...")
    setShowSolution(false)

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/exercises/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({
          exercise_id: exercise.id,
          code: code,
          module_id: moduleId || exercise.module_id || 0
        })
      })

      const data = await res.json()

      if (data.output) {
        setOutput(data.output)
      }

      if (data.passed) {
        setStatus("success")
        setPassed(true)
        setOutput(prev => prev + "\n\n✅ ¡Ejercicio completado correctamente!")
        toast.success(`¡Ejercicio completado! +${data.points_earned || 0} pts`)
        if (onComplete) onComplete()
      } else {
        setStatus("error")
        setAttempts(data.attempts || attempts + 1)
        setOutput(prev => {
          let msg = prev || ""
          if (data.error) msg += `\nError: ${data.error}`
          return msg
        })
        
        if (data.can_view_solution) {
          setCanViewSolution(true)
          setSolution(data.solution)
        }
      }
    } catch (error) {
      setOutput("Error de conexión con el servidor")
      setStatus("error")
    } finally {
      setIsExecuting(false)
    }
  }

  const handleShowSolution = () => {
    setShowSolution(true)
  }

  const handleReset = () => {
    setCode(exercise.instructions || "# Escribe tu código aquí\n")
    setOutput("")
    setStatus("idle")
    setShowSolution(false)
  }

  return (
    <Card className="flex flex-col rounded-xl overflow-hidden border border-primary/20 bg-card/80 backdrop-blur my-6">
      <div className="flex items-center justify-between bg-primary/10 px-4 py-3 border-b border-primary/20">
        <div className="flex items-center gap-3">
          <h3 className="font-bold text-primary flex items-center gap-2">
            <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded-md uppercase tracking-wider">Ejercicio</span>
            {exercise.title}
          </h3>
          {passed && <CheckCircle2 className="w-5 h-5 text-green-500" />}
        </div>
        <div className="flex items-center gap-2">
          {status !== "idle" && (
            <span className={`text-xs font-bold px-2 py-1 rounded-full ${
              status === "success" ? "bg-green-500/10 text-green-500" :
              "bg-red-500/10 text-red-500"
            }`}>
              {status === "success" ? "Completado" : `${attempts} intento${attempts !== 1 ? 's' : ''}`}
            </span>
          )}
          <Button size="sm" variant="ghost" onClick={handleReset} disabled={isExecuting}>
            <RotateCcw className="w-4 h-4" />
          </Button>
          {canViewSolution && !passed && (
            <Button size="sm" variant="outline" className="text-amber-500 border-amber-500/30" onClick={handleShowSolution}>
              <Eye className="w-4 h-4 mr-1" /> Ver Solución
            </Button>
          )}
          <Button size="sm" className="bg-primary" onClick={handleRun} disabled={isExecuting || passed}>
            {isExecuting ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Play className="w-4 h-4 mr-1" />}
            {isExecuting ? 'Evaluando...' : passed ? 'Completado' : 'Enviar'}
          </Button>
        </div>
      </div>

      {showSolution && (
        <div className="bg-amber-500/5 border-b border-amber-500/20 px-4 py-3">
          <p className="text-sm font-bold text-amber-500 mb-2">Solución:</p>
          <pre className="text-sm font-mono bg-muted p-3 rounded-lg overflow-x-auto whitespace-pre-wrap">{solution || "No hay solución disponible"}</pre>
        </div>
      )}

      <div className="grid lg:grid-cols-2">
        <div className="border-r border-border">
          <CodeMirror
            value={code}
            height="100%"
            minHeight="200px"
            theme={oneDark}
            extensions={[python()]}
            onChange={(val) => setCode(val)}
            className="text-sm"
          />
        </div>
        <div className="bg-[#1e1e1e] flex flex-col">
          <div className="flex items-center gap-2 bg-[#2d2d2d] px-4 py-2 border-b border-[#3d3d3d]">
            <Terminal className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-mono text-muted-foreground">Terminal</span>
          </div>
          <div className={`p-4 font-mono text-sm whitespace-pre-wrap min-h-[160px] ${
            status === "success" ? "text-green-400" :
            status === "error" ? "text-red-400" :
            "text-green-400"
          }`}>
            {output || <span className="text-gray-500 italic">La salida del código aparecerá aquí...</span>}
          </div>
        </div>
      </div>
    </Card>
  )
}