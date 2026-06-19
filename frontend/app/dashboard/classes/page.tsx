"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, BookOpen, Users, Clock, Loader2, CheckCircle2, XCircle, Hourglass, ChevronRight, GraduationCap } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/use-auth"
import { toast } from "sonner"
import API from "@/lib/api"

export default function ClassesPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [availableClasses, setAvailableClasses] = useState<any[]>([])
  const [enrolledClasses, setEnrolledClasses] = useState<any[]>([])
  const [pendingRequests, setPendingRequests] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [requestingId, setRequestingId] = useState<number | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setIsLoading(true)
    try {
      const [allRes, enrolledRes] = await Promise.all([
        fetch(`${API}/classes`, { credentials: "include" }),
        fetch(`${API}/classes/enrolled`, { credentials: "include" })
      ])
      const allData = await allRes.json()
      const enrolledData = await enrolledRes.json()

      if (allData.success) setAvailableClasses(allData.classes || [])
      if (enrolledData.success) {
        const classes = enrolledData.classes || []
        setEnrolledClasses(classes.filter((c: any) => c.enrollment_status === "approved"))
        setPendingRequests(classes.filter((c: any) => c.enrollment_status === "pending"))
      }
    } catch (err) {
      console.error("Error loading classes:", err)
    }
    setIsLoading(false)
  }

  const requestingRef = useRef<number | null>(null)
  const isEnrolled = (classId: number) => enrolledClasses.some(c => c.id === classId)
  const isPending = (classId: number) => pendingRequests.some(c => c.id === classId)
  const hasAction = (classId: number) => isEnrolled(classId) || isPending(classId)

  const handleEnroll = async (classId: number) => {
    if (isEnrolled(classId) || isPending(classId) || requestingRef.current !== null) return
    requestingRef.current = classId
    setRequestingId(classId)
    try {
      const res = await fetch(`${API}/classes/${classId}/enroll`, {
        method: "POST",
        credentials: "include"
      })
      const data = await res.json()
      if (data.success) {
        const enrolledClass = availableClasses.find(c => c.id === classId)
        if (enrolledClass) {
          setPendingRequests(prev => [...prev, { ...enrolledClass, enrollment_status: "pending" }])
        }
        toast.success("Solicitud enviada. Espera la aprobación del docente.")
      } else {
        toast.error(data.detail || data.error || "Error al solicitar matrícula")
        // Sync with server even on error so UI reflects current state
        await refreshEnrollments()
        setRequestingId(null)
        requestingRef.current = null
        return
      }
    } catch (err) {
      console.error("Error al matricular:", err)
      toast.error("Error de conexión")
    }
    setRequestingId(null)
    requestingRef.current = null
  }
  
  async function refreshEnrollments() {
    try {
      const res = await fetch(`${API}/classes/enrolled`, { credentials: "include" })
      const data = await res.json()
      if (data.success) {
        const classes = data.classes || []
        setEnrolledClasses(classes.filter((c: any) => c.enrollment_status === "approved"))
        setPendingRequests(classes.filter((c: any) => c.enrollment_status === "pending"))
      }
    } catch (err) {
      console.error("Error refreshing enrollments:", err)
    }
  }

  const filteredClasses = availableClasses.filter(c =>
    !hasAction(c.id) && (
      c.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  )

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <GraduationCap className="w-7 h-7 text-primary" />
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Mis Clases</h1>
        </div>
        <p className="text-muted-foreground">Explora las clases disponibles y matricúlate para aprender con docentes.</p>
      </div>

      {/* Pending Requests */}
      {pendingRequests.length > 0 && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-500 text-base">
              <Hourglass className="w-5 h-5" />
              Solicitudes Pendientes ({pendingRequests.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {pendingRequests.map((cls) => (
              <div key={cls.id} className="flex items-center justify-between p-3 rounded-lg border border-amber-500/20">
                <div>
                  <p className="font-medium">{cls.title}</p>
                  <p className="text-xs text-muted-foreground">Esperando aprobación del docente</p>
                </div>
                <span className="flex items-center gap-1 text-sm text-amber-500">
                  <Hourglass className="w-4 h-4" /> Pendiente
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Enrolled Classes */}
      {enrolledClasses.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <BookOpen className="w-5 h-5 text-primary" />
              Clases Activas ({enrolledClasses.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {enrolledClasses.map((cls) => (
              <div
                key={cls.id}
                className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => router.push(`/dashboard/classes/${cls.id}`)}
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-green-500/10 text-green-500">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium">{cls.title}</p>
                    <p className="text-xs text-muted-foreground">{cls.category} · {cls.difficulty}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); router.push(`/dashboard/classes/${cls.id}`) }}>
                    <BookOpen className="w-4 h-4 mr-1" /> Ver contenido
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Available Classes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Clases Disponibles</h2>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar clases..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {filteredClasses.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground border-2 border-dashed rounded-xl">
            <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No hay clases disponibles</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredClasses.map((cls) => (
              <Card key={cls.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-5">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                    <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary">{cls.category}</span>
                    <span>{cls.difficulty}</span>
                  </div>
                  <h3 className="font-bold text-lg mb-1">{cls.title}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{cls.description}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4">
                    <Users className="w-3.5 h-3.5" />
                    <span>{cls.teacher_name || "Docente"}</span>
                  </div>
                  <Button
                    className="w-full"
                    variant={isEnrolled(cls.id) ? "outline" : "default"}
                    disabled={isPending(cls.id) || requestingId === cls.id}
                    onClick={() => isEnrolled(cls.id) ? router.push(`/dashboard/classes/${cls.id}`) : handleEnroll(cls.id)}
                  >
                    {isEnrolled(cls.id) ? (
                      <>Ir a la clase <ChevronRight className="w-4 h-4 ml-1" /></>
                    ) : isPending(cls.id) ? (
                      <><Hourglass className="w-4 h-4 mr-1" /> Esperando aprobación</>
                    ) : requestingId === cls.id ? (
                      <><Loader2 className="w-4 h-4 mr-1 animate-spin" /> Enviando...</>
                    ) : (
                      "Solicitar Matrícula"
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
