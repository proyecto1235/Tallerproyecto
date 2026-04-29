"use client"

import { useState } from "react"
import CodeMirror from "@uiw/react-codemirror"
import { python } from "@codemirror/lang-python"
import { oneDark } from "@codemirror/theme-one-dark"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Play, RotateCcw, CheckCircle2, XCircle, Zap, Code2, Terminal } from "lucide-react"

export default function ExercisesPage() {
  const [code, setCode] = useState("print(\"Hola Robolearn!\")\n\n# Escribe tu codigo aqui\n")
  const [output, setOutput] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")

  const exercise = {
    title: "Misión 1: Saludo al Robot",
    description: "Tu robot está encendido pero no sabe qué decir. Escribe un código en Python usando la función `print()` para que el robot diga 'Hola Mundo'.",
    hints: [
      "Recuerda usar comillas dobles o simples para el texto.",
      "La función print se escribe en minúsculas."
    ]
  }

  const handleRunCode = () => {
    setStatus("running")
    setOutput("Ejecutando código...")
    
    // Simulate API delay
    setTimeout(() => {
      if (code.includes("print(\"Hola Mundo\")") || code.includes("print('Hola Mundo')")) {
        setStatus("success")
        setOutput("> Hola Mundo\n\n¡Excelente! Has completado el ejercicio exitosamente. +10 puntos")
      } else {
        setStatus("error")
        // Basic error detection for mock
        if (!code.includes("print")) {
          setOutput("Error: Parece que olvidaste usar la función print().")
        } else if (!code.includes("Hola Mundo")) {
          setOutput("> " + (code.match(/print\((["'])(.*?)\1\)/)?.[2] || "...") + "\n\nError: El robot no dijo 'Hola Mundo'. Revisa el texto exacto.")
        } else {
          setOutput("Error de sintaxis: Revisa que hayas cerrado los paréntesis y las comillas.")
        }
      }
    }, 1500)
  }

  const handleReset = () => {
    setCode("print(\"Hola Robolearn!\")\n\n# Escribe tu codigo aqui\n")
    setOutput(null)
    setStatus("idle")
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col md:flex-row gap-6">
      
      {/* Panel Izquierdo: Instrucciones */}
      <div className="w-full md:w-1/3 flex flex-col gap-4 h-full">
        <Card className="flex-1 flex flex-col neo-shadow border-primary/20">
          <CardHeader className="bg-primary/5 pb-4 border-b">
            <CardTitle className="text-xl flex items-center gap-2 text-primary">
              <Zap className="w-5 h-5" />
              {exercise.title}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 flex-1 overflow-y-auto">
            <div className="prose dark:prose-invert prose-sm">
              <p className="text-base leading-relaxed">{exercise.description}</p>
              
              <div className="mt-8">
                <h4 className="font-bold flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  Pistas
                </h4>
                <ul className="space-y-2">
                  {exercise.hints.map((hint, i) => (
                    <li key={i} className="bg-muted/50 p-3 rounded-lg text-sm border flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                      {hint}
                    </li>
                  ))}
                </ul>
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
        <div className={`h-48 rounded-xl border-2 flex flex-col overflow-hidden transition-colors ${
          status === 'success' ? 'border-green-500/50 bg-green-500/5' :
          status === 'error' ? 'border-red-500/50 bg-red-500/5' :
          'border-border bg-card'
        }`}>
          <div className="bg-muted/50 border-b px-4 py-2 flex items-center gap-2 text-sm font-bold">
            <Terminal className="w-4 h-4" />
            Terminal de Salida
            {status === 'success' && <span className="ml-auto text-green-500 flex items-center gap-1"><CheckCircle2 className="w-4 h-4"/> ¡Correcto!</span>}
            {status === 'error' && <span className="ml-auto text-red-500 flex items-center gap-1"><XCircle className="w-4 h-4"/> Error</span>}
          </div>
          <div className="p-4 font-mono text-sm overflow-y-auto whitespace-pre-wrap flex-1">
            {output || <span className="text-muted-foreground italic">El resultado de tu código aparecerá aquí...</span>}
          </div>
        </div>

      </div>
    </div>
  )
}
