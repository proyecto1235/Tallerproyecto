"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, BookOpen, Clock, Loader2, CheckCircle2, ChevronRight } from "lucide-react"
import { useRouter } from "next/navigation"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { useToast } from "@/components/ui/use-toast"

export default function ClassesPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [availableClasses, setAvailableClasses] = useState<any[]>([])
  const [enrolledModules, setEnrolledModules] = useState<any[]>([])
  const [enrolledModuleIds, setEnrolledModuleIds] = useState<number[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const [selectedClass, setSelectedClass] = useState<any | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isEnrolling, setIsEnrolling] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  // Fetch enrolled modules to disable button
  useEffect(() => {
    const fetchEnrolled = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/modules/enrolled", {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success && data.modules && data.modules.length > 0) {
          setEnrolledModules(data.modules)
          setEnrolledModuleIds(data.modules.map((m: any) => m.id))
          return
        }
      } catch (error) {
        console.error("Error fetching enrolled modules:", error)
      }
      
      // Fallback si no hay backend o está vacío
      const mockEnrolled = [
        { id: "piloto-1", title: "Fundamentos de Robótica", description: "Aprende qué es un robot, sus partes y cómo piensa.", teacher_name: "Admin", enrollment_status: "active" }
      ]
      setEnrolledModules(mockEnrolled)
      setEnrolledModuleIds(["piloto-1" as any])
    }
    fetchEnrolled()
  }, [])

  // Fetch classes dynamically
  useEffect(() => {
    const fetchClasses = async () => {
      setIsLoading(true)
      try {
        const res = await fetch(`http://localhost:8000/api/modules/search?q=${searchQuery}`, {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success && data.results && data.results.length > 0) {
          setAvailableClasses(data.results)
          setIsLoading(false)
          return
        }
      } catch (error) {
        console.error("Error fetching classes:", error)
      }
      
      // Fallback de clases piloto para matricularse
      const mockAvailable = [
        { id: "piloto-2", title: "Programación Lógica Básica", description: "Variables, bucles y condicionales. El cerebro del robot.", teacher_name: "Prof. Carlos" },
        { id: "piloto-3", title: "Sensores y Entorno", description: "Cómo los robots ven y sienten el mundo que los rodea.", teacher_name: "Escuela San José" }
      ].filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()) || c.teacher_name.toLowerCase().includes(searchQuery.toLowerCase()))
      
      setAvailableClasses(mockAvailable)
      setIsLoading(false)
    }

    const delayDebounceFn = setTimeout(() => {
      fetchClasses()
    }, 300)

    return () => clearTimeout(delayDebounceFn)
  }, [searchQuery])

  const handleEnrollClick = (cls: any) => {
    setSelectedClass(cls)
    setIsModalOpen(true)
  }

  const handleConfirmEnroll = async () => {
    if (!selectedClass) return

    setIsEnrolling(true)
    try {
      const res = await fetch(`http://localhost:8000/api/modules/${selectedClass.id}/enroll`, {
        method: "POST",
        credentials: 'include'
      })
      const data = await res.json()

      if (data.success) {
        toast({
          title: "¡Matriculado con éxito!",
          description: `Te has inscrito en ${selectedClass.title}`,
        })
        setEnrolledModuleIds(prev => [...prev, selectedClass.id])
        setEnrolledModules(prev => [{ ...selectedClass, enrollment_status: 'active' }, ...prev])
      } else {
        toast({
          title: "Error al matricular",
          description: data.error || "Ocurrió un problema, intenta nuevamente.",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error de conexión",
        description: "No se pudo conectar con el servidor.",
        variant: "destructive"
      })
    } finally {
      setIsEnrolling(false)
      setIsModalOpen(false)
      setSelectedClass(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">Mis Clases</h1>
        <p className="text-muted-foreground">Explora y únete a nuevas clases (módulos)</p>
      </div>

      {/* Enrolled classes */}
      {enrolledModules.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Mis cursos activos</h2>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
            {enrolledModules.map((cls) => (
              <Card key={cls.id} className="border-primary/20 bg-primary/5">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{cls.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{cls.description}</p>
                  <Button
                    size="sm"
                    className="w-full group"
                    onClick={() => router.push(`/dashboard/classes/${cls.id}`)}
                  >
                    Ir a clase <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Browse classes */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Explorar Clases</CardTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar por clase o docente..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-64"
            />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : availableClasses.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No se encontraron clases
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {availableClasses.map((cls) => (
                <div key={cls.id} className="rounded-lg border p-4 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-foreground">{cls.title}</h3>
                      <p className="text-sm text-muted-foreground">Prof. {cls.teacher_name}</p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground line-clamp-2">{cls.description}</p>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <Button size="sm" variant="outline">
                      <BookOpen className="h-4 w-4 mr-2" /> Ver detalles
                    </Button>
                    {enrolledModuleIds.includes(cls.id) ? (
                      <Button size="sm" variant="secondary" disabled>
                        <CheckCircle2 className="h-4 w-4 mr-2" /> Matriculado
                      </Button>
                    ) : (
                      <Button size="sm" onClick={() => handleEnrollClick(cls)}>Matricularse</Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Deseas matricularte en esta clase?</AlertDialogTitle>
            <AlertDialogDescription>
              Estás a punto de inscribirte en el módulo <strong>{selectedClass?.title}</strong> dictado por Prof. {selectedClass?.teacher_name}. Podrás acceder a su contenido inmediatamente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isEnrolling}>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={(e) => {
              e.preventDefault()
              handleConfirmEnroll()
            }} disabled={isEnrolling}>
              {isEnrolling && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Confirmar Matrícula
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
