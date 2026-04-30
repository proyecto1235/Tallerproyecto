"use client"

import React, { useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { Play, Terminal } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export function InlineExercise({ exercise }: { exercise: any }) {
  const [code, setCode] = useState(exercise.instructions || "# Escribe tu código aquí\n")
  const [output, setOutput] = useState<string>("")
  const [isExecuting, setIsExecuting] = useState(false)

  const handleRun = async () => {
    if (isExecuting) return
    setIsExecuting(true)
    setOutput("")
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/execute-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({ code })
      })
      
      const data = await res.json()
      
      if (data.output) {
        setOutput(data.output)
      }
      
      if (data.error) {
        setOutput(prev => prev + `\nError: ${data.error}`)
      }
    } catch (error) {
      setOutput("Error de conexión con el servidor")
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <Card className="flex flex-col rounded-xl overflow-hidden border border-primary/20 bg-card/80 backdrop-blur my-6">
      <div className="flex items-center justify-between bg-primary/10 px-4 py-3 border-b border-primary/20">
        <div>
          <h3 className="font-bold text-primary flex items-center gap-2">
            <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded-md uppercase tracking-wider">Ejercicio</span>
            {exercise.title}
          </h3>
          {exercise.description && <p className="text-sm text-muted-foreground mt-1">{exercise.description}</p>}
        </div>
        <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={handleRun} disabled={isExecuting}>
          <Play className="w-4 h-4 mr-2" />
          {isExecuting ? 'Ejecutando...' : 'Ejecutar'}
        </Button>
      </div>
      
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
          <div className="p-4 font-mono text-sm text-green-400 whitespace-pre-wrap min-h-[160px]">
            {output || <span className="text-gray-500 italic">La salida del código aparecerá aquí...</span>}
          </div>
        </div>
      </div>
    </Card>
  )
}
