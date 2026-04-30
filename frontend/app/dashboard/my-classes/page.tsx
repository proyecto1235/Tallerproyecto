"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Search, Clock, Users, Star, PlayCircle, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

export default function MyClassesPage() {
  const [filter, setFilter] = useState("Todas")
  const [classes, setClasses] = useState<any[]>([])
  const [enrolledClasses, setEnrolledClasses] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const router = useRouter()

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/modules/search?q=${searchQuery}`, {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          const formatted = data.results.map((m: any) => ({
            id: m.id.toString(),
            title: m.title,
            instructor: m.teacher_name,
            category: "General", // Placeholder
            level: "Básico",
            duration: "N/A",
            students: 0,
            rating: 5.0,
            progress: 0,
            imageColor: "from-blue-500 to-cyan-500"
          }))
          setClasses(formatted)
        }
        
        // Also fetch enrolled classes to determine status
        const enrRes = await fetch("http://localhost:8000/api/modules/enrolled", {
          credentials: 'include'
        })
        const enrData = await enrRes.json()
        if (enrData.success) {
          setEnrolledClasses(enrData.modules.map((m: any) => m.id.toString()))
          
          // Map progress from enrollments to classes
          setClasses(prev => prev.map(c => {
            const enr = enrData.modules.find((m: any) => m.id.toString() === c.id)
            if (enr) {
              return { ...c, progress: enr.enrollment_status === 'completed' ? 100 : 45 }
            }
            return c
          }))
        }
      } catch (error) {
        console.error("Error fetching classes", error)
      } finally {
        setLoading(false)
      }
    }
    fetchModules()
  }, [searchQuery])

  const categories = ["Todas", "Python", "Robótica", "Web", "Juegos"]



  const handleEnrollment = async (id: string, isEnrolled: boolean) => {
    if (isEnrolled) {
      router.push(`/dashboard/modules/${id}`)
    } else {
      try {
        const res = await fetch(`http://localhost:8000/api/modules/${id}/enroll`, {
          method: "POST",
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          setEnrolledClasses(prev => [...prev, id])
          toast.success("¡Te has inscrito correctamente!")
        } else {
          toast.error("Error al inscribirse: " + data.error)
        }
      } catch (error) {
        toast.error("Error de red al inscribirse")
      }
    }
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col gap-4">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-primary" />
          Biblioteca de Clases
        </h1>
        <p className="text-muted-foreground text-lg max-w-3xl">
          Explora todos los cursos disponibles. Inscríbete en nuevas aventuras de aprendizaje o continúa donde te quedaste.
        </p>
      </div>

      {/* Toolbar / Filters */}
      <div className="flex flex-col sm:flex-row justify-between gap-4 items-center bg-card p-4 rounded-xl border neo-shadow">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Buscar clases..." 
            className="pl-9" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-2 w-full sm:w-auto">
          {categories.map(cat => (
            <Button 
              key={cat}
              variant={filter === cat ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(cat)}
              className="rounded-full font-bold"
            >
              {cat}
            </Button>
          ))}
        </div>
      </div>

      {/* Grid de Clases */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {classes.map(cls => (
          <Card key={cls.id} className="overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-primary/10 group flex flex-col">
            <div className={`h-32 bg-gradient-to-br ${cls.imageColor} relative flex items-center justify-center`}>
              <PlayCircle className="w-12 h-12 text-white/50 group-hover:text-white/90 transition-colors" />
              {cls.progress === 100 && (
                <div className="absolute top-2 right-2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-md">
                  Completado
                </div>
              )}
            </div>
            
            <CardHeader className="pb-2 flex-none">
              <div className="flex justify-between items-start mb-2">
                <Badge variant="secondary" className="font-semibold text-[10px] uppercase tracking-wider">
                  {cls.category}
                </Badge>
                <Badge variant="outline" className="font-semibold text-[10px] uppercase tracking-wider">
                  {cls.level}
                </Badge>
              </div>
              <h3 className="font-bold text-lg leading-tight line-clamp-2">{cls.title}</h3>
              <p className="text-sm text-muted-foreground">{cls.instructor}</p>
            </CardHeader>
            
            <CardContent className="py-2 flex-1">
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                <span className="flex items-center gap-1"><Clock className="w-3 h-3"/> {cls.duration}</span>
                <span className="flex items-center gap-1"><Users className="w-3 h-3"/> {cls.students}</span>
                <span className="flex items-center gap-1 text-yellow-600 font-bold"><Star className="w-3 h-3 fill-yellow-500 text-yellow-500"/> {cls.rating}</span>
              </div>

              {cls.progress > 0 && cls.progress < 100 && (
                <div className="space-y-1.5 mt-auto">
                  <div className="flex justify-between text-xs font-bold">
                    <span>Progreso</span>
                    <span className="text-primary">{cls.progress}%</span>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${cls.progress}%` }} />
                  </div>
                </div>
              )}
            </CardContent>

            <CardFooter className="pt-4 border-t flex-none">
              <Button 
                className="w-full font-bold" 
                variant={enrolledClasses.includes(cls.id) ? (cls.progress === 100 ? "outline" : "default") : "secondary"}
                onClick={() => handleEnrollment(cls.id, enrolledClasses.includes(cls.id))}
              >
                {enrolledClasses.includes(cls.id) 
                  ? (cls.progress === 100 ? "Repasar" : "Continuar") 
                  : "Inscribirse"}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
      
      {classes.length === 0 && (
        <div className="text-center py-20">
          <BookOpen className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-muted-foreground">No hay clases en esta categoría</h3>
        </div>
      )}
    </div>
  )
}
