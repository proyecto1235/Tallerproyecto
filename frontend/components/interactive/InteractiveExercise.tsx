"use client"

import React, { useState, useEffect } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { Play, RotateCcw, Bot } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function InteractiveExercise() {
  const [code, setCode] = useState("# Haz que el robot salte 3 veces\nfor i in range(3):\n    jump()\n")
  const [isAnimating, setIsAnimating] = useState(false)
  const [jumps, setJumps] = useState(0)
  const [currentJump, setCurrentJump] = useState(0)

  const handleRun = () => {
    if (isAnimating) return
    
    // Naive parser for demo purposes
    let detectedJumps = 0
    if (code.includes('jump()')) {
      detectedJumps = 1
      const loopMatch = code.match(/for\s+.*in\s+range\(\s*(\d+)\s*\):/)
      if (loopMatch) {
        detectedJumps = parseInt(loopMatch[1]) || 1
      }
    }

    setJumps(detectedJumps)
    setCurrentJump(0)
    
    if (detectedJumps > 0) {
      setIsAnimating(true)
    }
  }

  useEffect(() => {
    if (isAnimating && currentJump < jumps) {
      const timer = setTimeout(() => {
        setCurrentJump(prev => prev + 1)
      }, 800) // Jump duration
      return () => clearTimeout(timer)
    } else if (currentJump >= jumps && jumps > 0) {
      setTimeout(() => {
        setIsAnimating(false)
      }, 500)
    }
  }, [isAnimating, currentJump, jumps])

  const reset = () => {
    setCode("# Haz que el robot salte 3 veces\nfor i in range(3):\n    jump()\n")
    setIsAnimating(false)
    setJumps(0)
    setCurrentJump(0)
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Editor Side */}
      <div className="flex flex-col rounded-xl overflow-hidden border border-border neo-shadow-primary bg-background">
        <div className="flex items-center justify-between bg-muted/50 px-4 py-2 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-destructive" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-primary" />
            </div>
            <span className="ml-2 text-sm font-mono text-muted-foreground">ejercicio.py</span>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="ghost" onClick={reset} disabled={isAnimating}>
              <RotateCcw className="w-4 h-4 mr-2" />
              Reiniciar
            </Button>
            <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90" onClick={handleRun} disabled={isAnimating}>
              <Play className="w-4 h-4 mr-2" />
              Ejecutar
            </Button>
          </div>
        </div>
        <div className="flex-1 min-h-[300px]">
          <CodeMirror
            value={code}
            height="100%"
            minHeight="300px"
            theme={oneDark}
            extensions={[python()]}
            onChange={(val) => setCode(val)}
            className="text-base"
          />
        </div>
      </div>

      {/* Visual Feedback Side */}
      <div className="relative flex flex-col items-center justify-end rounded-xl border border-border bg-card/80 backdrop-blur neo-shadow p-6 min-h-[350px] overflow-hidden">
        {/* Environment / Background grid */}
        <div className="absolute inset-0 scanline opacity-50" />
        
        {/* Status Text */}
        <div className="absolute top-4 left-4 z-10 font-mono text-sm">
          {isAnimating ? (
            <span className="text-primary animate-pulse">Ejecutando... Salto {currentJump}/{jumps}</span>
          ) : (
            <span className="text-muted-foreground">Esperando código...</span>
          )}
        </div>

        {/* Robot Character */}
        <div className="relative z-10 mb-8">
          <div
            className={`transition-transform duration-500 ease-in-out ${
              isAnimating && currentJump < jumps ? '-translate-y-24' : 'translate-y-0'
            }`}
            style={{
              /* We trigger re-animation by updating a key or changing state rapidly, 
                 but transition-transform works well if toggled.
                 Since we update currentJump every 800ms, we can use a keyframe animation instead for continuous jumping. */
            }}
          >
            {/* Custom Robot UI */}
            <div className={`relative flex flex-col items-center ${isAnimating ? 'animate-bounce' : ''}`}>
              <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center neo-shadow-primary z-10">
                <div className="flex gap-2">
                  <div className={`w-3 h-3 rounded-full bg-background ${isAnimating ? 'animate-pulse' : ''}`} />
                  <div className={`w-3 h-3 rounded-full bg-background ${isAnimating ? 'animate-pulse' : ''}`} />
                </div>
              </div>
              <div className="w-8 h-12 bg-secondary rounded-b-xl -mt-2 neo-shadow" />
              {/* Shadow on floor */}
              <div className={`absolute -bottom-4 w-12 h-3 bg-black/20 rounded-full blur-sm transition-transform duration-500 ${isAnimating ? 'scale-50' : 'scale-100'}`} />
            </div>
          </div>
        </div>

        {/* Floor */}
        <div className="w-full h-8 bg-muted rounded-t-xl border-t-2 border-primary/30 z-0" />
      </div>
    </div>
  )
}
