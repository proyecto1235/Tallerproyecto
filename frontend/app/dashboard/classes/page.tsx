"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, BookOpen, Users, Clock, Loader2, CheckCircle2, XCircle, Hourglass, ChevronRight, GraduationCap } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/use-auth"
import { toast } from "sonner"

const ENROLLMENTS_KEY = "robolearn_enrollments"
const STORAGE_KEY = "robolearn_teacher_classes"

interface AvailableClass {
  id: string
  title: string
  description: string
  teacher_name: string
  category: string
  difficulty: string
}

interface Enrollment {
  classId: string
  studentId: number
  status: "pending" | "approved" | "rejected"
  enrolledAt: string
}

const AVAILABLE_CLASSES: AvailableClass[] = [
  { id: "tc-1", title: "Desarrollo Web con Python", description: "Aprende a crear aplicaciones web usando Django y Flask.", teacher_name: "Professor García", category: "Desarrollo Web", difficulty: "Intermedio" },
  { id: "tc-2", title: "Robótica Educativa", description: "Construye y programa robots con Python y Arduino.", teacher_name: "Professor García", category: "Robótica", difficulty: "Avanzado" },
  { id: "tc-3", title: "Introducción a la IA", description: "Conceptos básicos de inteligencia artificial con Python.", teacher_name: "Professor García", category: "Inteligencia Artificial", difficulty: "Avanzado" },
]

export default function ClassesPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [availableClasses, setAvailableClasses] = useState<AvailableClass[]>([])
  const [enrolledClasses, setEnrolledClasses] = useState<AvailableClass[]>([])
  const [enrollments, setEnrollments] = useState<Enrollment[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem(ENROLLMENTS_KEY)
    const enrollData: Enrollment[] = saved ? JSON.parse(saved) : []
    setEnrollments(enrollData)

    const approved = enrollData.filter(e => e.status === "approved")
    const approvedIds = approved.map(e => e.classId)

    const savedClasses = localStorage.getItem(STORAGE_KEY)
    const allClasses: AvailableClass[] = savedClasses
      ? JSON.parse(savedClasses).filter((c: any) => c.is_published).map((c: any) => ({
          id: c.id, title: c.title, description: c.description,
          teacher_name: user?.fullName || "Docente",
          category: c.category, difficulty: c.difficulty
        }))
      : AVAILABLE_CLASSES

    setEnrolledClasses(allClasses.filter(c => approvedIds.includes(c.id)))
    setAvailableClasses(allClasses)
    setIsLoading(false)
  }, [user])

  const getEnrollment = (classId: string) => enrollments.find(e => e.classId === classId)

  const handleEnroll = (cls: AvailableClass) => {
    const existing = getEnrollment(cls.id)
    if (existing) {
      if (existing.status === "pending") {
        toast.info("Ya tienes una solicitud pendiente para esta clase")
      } else if (existing.status === "approved") {
        toast.info("Ya estás matriculado en esta clase")
      } else {
        toast.error("Tu solicitud fue rechazada anteriormente")
      }
      return
    }

    const newEnrollment: Enrollment = {
      classId: cls.id,
      studentId: user?.id || 0,
      status: "pending",
      enrolledAt: new Date().toISOString()
    }
    const updated = [...enrollments, newEnrollment]
    setEnrollments(updated)
    localStorage.setItem(ENROLLMENTS_KEY, JSON.stringify(updated))
    toast.success("Solicitud enviada. Espera la aprobación del docente.")
  }

  const filteredAvailable = availableClasses.filter(c =>
    !enrolledClasses.find(e => e.id === c.id) &&
    getEnrollment(c.id)?.status !== "rejected" &&
    (c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     c.teacher_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
     c.category.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">Mis Clases</h1>
        <p className="text-muted-foreground">Explora clases creadas por docentes y solicita matricularte</p>
      </div>

      {enrolledClasses.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-500" />
            Mis cursos activos
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
            {enrolledClasses.map(cls => (
              <Card key={cls.id} className="border-primary/20 bg-primary/5">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-medium text-muted-foreground">{cls.category}</span>
                      <CardTitle className="text-lg mt-1">{cls.title}</CardTitle>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{cls.description}</p>
                  <Button size="sm" className="w-full group" onClick={() => router.push(`/dashboard/classes/${cls.id}`)}>
                    Ir a clase <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {enrollments.filter(e => e.status === "pending").length > 0 && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-500">
              <Hourglass className="w-5 h-5" />
              Solicitudes Pendientes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {enrollments.filter(e => e.status === "pending").map(e => {
                const cls = availableClasses.find(c => c.id === e.classId)
                if (!cls) return null
                return (
                  <div key={e.classId} className="flex items-center justify-between p-3 rounded-lg border border-amber-500/20">
                    <div>
                      <p className="font-medium text-sm">{cls.title}</p>
                      <p className="text-xs text-muted-foreground">Docente: {cls.teacher_name}</p>
                    </div>
                    <span className="text-xs font-medium text-amber-500 bg-amber-500/10 px-2 py-1 rounded-full flex items-center gap-1">
                      <Hourglass className="w-3 h-3" /> Pendiente
                    </span>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Explorar Clases</CardTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar por clase, docente o categoría..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-9 w-64"
            />
          </div>
        </CardHeader>
        <CardContent>
          {filteredAvailable.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <GraduationCap className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No se encontraron clases disponibles</p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {filteredAvailable.map(cls => {
                const enrollment = getEnrollment(cls.id)
                return (
                  <div key={cls.id} className="rounded-lg border p-4 flex flex-col justify-between hover:shadow-md transition-shadow">
                    <div>
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-muted-foreground">{cls.category}</span>
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                              cls.difficulty === "Principiante" ? "border-emerald-500/20 text-emerald-500 bg-emerald-500/10" :
                              cls.difficulty === "Intermedio" ? "border-amber-500/20 text-amber-500 bg-amber-500/10" :
                              "border-purple-500/20 text-purple-500 bg-purple-500/10"
                            }`}>{cls.difficulty}</span>
                          </div>
                          <h3 className="font-semibold text-foreground">{cls.title}</h3>
                          <p className="text-xs text-muted-foreground">Prof. {cls.teacher_name}</p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-3">{cls.description}</p>
                    </div>
                    <div className="flex items-center justify-between">
                      <Button size="sm" variant="outline" onClick={() => router.push(`/dashboard/modules/${cls.id}`)}>
                        <BookOpen className="h-4 w-4 mr-2" />Ver detalles
                      </Button>
                      {enrollment?.status === "pending" ? (
                        <Button size="sm" variant="secondary" disabled>
                          <Hourglass className="h-4 w-4 mr-2" /> Pendiente
                        </Button>
                      ) : enrollment?.status === "approved" ? (
                        <Button size="sm" variant="secondary" disabled>
                          <CheckCircle2 className="h-4 w-4 mr-2" /> Matriculado
                        </Button>
                      ) : (
                        <Button size="sm" onClick={() => handleEnroll(cls)}>
                          Solicitar Matrícula
                        </Button>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}