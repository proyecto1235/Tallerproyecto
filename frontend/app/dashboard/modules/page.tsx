"use client"

import { useState, useEffect } from "react"
import { ModuleCard } from "@/components/dashboard/module-card"
import { Map, BookOpen, Trophy, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"

export default function ModulesPage() {
  const router = useRouter()
  const [modules, setModules] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchModules = async () => {
      const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/$/, "")
      try {
        const res = await fetch(`${API_URL}/modules/enrolled`, {
          credentials: 'include'
        })
        if (!res.ok) {
          throw new Error(`Network error: ${res.status}`)
        }
        const data = await res.json()
        if (data.success && data.modules && data.modules.length > 0) {
          const mapped = data.modules.map((m: any) => ({
            id: m.id.toString(),
            title: m.title,
            description: m.description,
            level: m.order || 1,
            status: m.enrollment_status === "completed" ? "completed" : "in-progress",
            progress: m.enrollment_status === "completed" ? 100 : 45 
          }))
          setModules(mapped.sort((a: any, b: any) => a.level - b.level))
          setLoading(false)
          return
        }
      } catch (error) {
        console.error("Error fetching modules", error)
      }
      
      // Fallback a datos mockeados (Cursos Piloto) si falla la DB o está vacía
      setModules([
        { id: "piloto-1", title: "Fundamentos de Robótica", description: "Aprende qué es un robot, sus partes y cómo piensa.", level: 1, status: "completed", progress: 100 },
        { id: "piloto-2", title: "Programación Lógica Básica", description: "Variables, bucles y condicionales. El cerebro del robot.", level: 2, status: "in-progress", progress: 45 },
        { id: "piloto-3", title: "Sensores y Entorno", description: "Cómo los robots ven y sienten el mundo que los rodea.", level: 3, status: "locked", progress: 0 },
        { id: "piloto-4", title: "Tu Primer Proyecto Autónomo", description: "Programa un robot que esquive obstáculos por sí solo.", level: 4, status: "locked", progress: 0 },
      ])
      setLoading(false)
    }
    fetchModules()
  }, [])

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }


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
                  onClick={() => router.push(`/dashboard/modules/${mod.id}`)}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
