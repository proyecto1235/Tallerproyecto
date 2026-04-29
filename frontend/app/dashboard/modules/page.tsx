"use client"

import { ModuleCard } from "@/components/dashboard/module-card"
import { Map, BookOpen, Trophy } from "lucide-react"
import { useRouter } from "next/navigation"

export default function ModulesPage() {
  const router = useRouter()
  const modules = [
    {
      id: "mod-1",
      title: "Fundamentos de la Programación",
      description: "Aprende qué es un algoritmo, cómo piensan las computadoras y da tus primeros pasos en el mundo del código.",
      level: 1,
      status: "completed" as const,
      progress: 100
    },
    {
      id: "mod-2",
      title: "Variables y Tipos de Datos",
      description: "Descubre cómo guardar información en la memoria de la computadora usando variables, números y textos.",
      level: 2,
      status: "in-progress" as const,
      progress: 45
    },
    {
      id: "mod-3",
      title: "Decisiones lógicas (If/Else)",
      description: "Enseña a tu programa a tomar decisiones basadas en condiciones para crear flujos inteligentes.",
      level: 3,
      status: "locked" as const,
      progress: 0
    },
    {
      id: "mod-4",
      title: "Bucles y Repeticiones",
      description: "Automatiza tareas repetitivas usando bucles For y While. ¡Haz que la computadora trabaje por ti!",
      level: 4,
      status: "locked" as const,
      progress: 0
    }
  ]

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary w-fit">
          <Map className="w-4 h-4" />
          <span className="text-sm font-bold uppercase tracking-wider">Tu Camino</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Ruta de Aprendizaje</h1>
        <p className="text-muted-foreground text-lg max-w-2xl">
          Avanza módulo por módulo para convertirte en un experto programador. ¡Cada nivel completado desbloquea nuevos poderes!
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mt-6">
        <div className="bg-card border rounded-xl p-4 flex items-center gap-4 neo-shadow">
          <div className="bg-primary/10 p-3 rounded-lg text-primary">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground font-medium">Módulos Totales</p>
            <p className="text-2xl font-bold">{modules.length}</p>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-4 flex items-center gap-4 neo-shadow">
          <div className="bg-green-500/10 p-3 rounded-lg text-green-500">
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground font-medium">Completados</p>
            <p className="text-2xl font-bold">{modules.filter(m => m.status === 'completed').length}</p>
          </div>
        </div>
      </div>

      <div className="relative mt-12">
        {/* Timeline Connecting Line */}
        <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-1 bg-border -translate-x-1/2 rounded-full" />
        
        <div className="space-y-12 relative">
          {modules.map((mod, index) => (
            <div key={mod.id} className={`flex flex-col lg:flex-row items-center gap-8 ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'}`}>
              
              <div className="flex-1 w-full lg:w-1/2" />

              {/* Timeline dot */}
              <div className="hidden lg:flex absolute left-1/2 -translate-x-1/2 w-12 h-12 rounded-full border-4 border-background bg-card shadow-sm items-center justify-center z-10">
                <span className={`font-bold text-lg ${mod.status === 'completed' ? 'text-green-500' : mod.status === 'in-progress' ? 'text-primary' : 'text-muted-foreground'}`}>
                  {mod.level}
                </span>
              </div>

              <div className="flex-1 w-full lg:w-1/2">
                <ModuleCard 
                  {...mod} 
                  onClick={() => router.push('/dashboard/exercises')}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
