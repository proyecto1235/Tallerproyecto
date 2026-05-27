"use client"

import { MarkdownContent } from "@/components/ui/markdown-content"
import { InlineExercise } from "@/components/interactive/InlineExercise"

interface TheoryWithExercisesProps {
  theory: string
  exercises: any[]
  moduleId?: number
  onComplete?: () => void
  classModuleId?: number
}

export function TheoryWithExercises({ theory, exercises, moduleId, onComplete, classModuleId }: TheoryWithExercisesProps) {
  const parts = theory.split(/\[\s*ejercicio\s*\]/gi)
  const elements: React.ReactNode[] = []
  let exerciseIndex = 0

  parts.forEach((part, i) => {
    if (part.trim()) {
      elements.push(
        <MarkdownContent key={`theory-${i}`} content={part} />
      )
    }

    if (i < parts.length - 1) {
      if (exerciseIndex < exercises.length) {
        const ex = exercises[exerciseIndex]
        elements.push(
          <div key={`exercise-${ex.id}`} className="my-6 border-l-2 border-primary/30 pl-4">
            <InlineExercise
              exercise={ex}
              moduleId={moduleId}
              onComplete={onComplete}
              classModuleId={classModuleId}
            />
          </div>
        )
        exerciseIndex++
      } else {
        elements.push(
          <div key={`missing-${i}`} className="my-4 p-3 border border-dashed border-destructive/30 rounded-lg text-sm text-destructive italic">
            ⚠️ Se esperaba un ejercicio aquí, pero no hay más ejercicios definidos
          </div>
        )
      }
    }
  })

  while (exerciseIndex < exercises.length) {
    const ex = exercises[exerciseIndex]
    elements.push(
      <div key={`unplaced-${ex.id}`} className="my-6 border border-dashed border-muted-foreground/30 rounded-lg p-4">
        <div className="text-xs text-muted-foreground mb-2 uppercase tracking-wider font-semibold">
          📎 Ejercicio &ldquo;{ex.title || exerciseIndex + 1}&rdquo; (sin posici&oacute;n en el contenido)
        </div>
        <InlineExercise
          exercise={ex}
          moduleId={moduleId}
          onComplete={onComplete}
          classModuleId={classModuleId}
        />
      </div>
    )
    exerciseIndex++
  }

  return <>{elements}</>
}
