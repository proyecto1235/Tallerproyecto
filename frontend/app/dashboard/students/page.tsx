"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "sonner"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Search, Loader2, User, BookOpen, Clock, Activity, AlertTriangle, CheckCircle2, XCircle, UserPlus } from "lucide-react"

export default function StudentsPage() {
  const [activeTab, setActiveTab] = useState("students")
  const [students, setStudents] = useState<any[]>([])
  const [pendingRequests, setPendingRequests] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [moduleFilter, setModuleFilter] = useState("all")

  const [selectedStudent, setSelectedStudent] = useState<any | null>(null)
  const [studentDetails, setStudentDetails] = useState<any | null>(null)
  const [isDetailsLoading, setIsDetailsLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [studentsRes, pendingRes] = await Promise.all([
          fetch("http://localhost:8000/api/teacher/students", { credentials: 'include' }),
          fetch("http://localhost:8000/api/teacher/pending-enrollments", { credentials: 'include' })
        ])
        const studentsData = await studentsRes.json()
        const pendingData = await pendingRes.json()
        if (studentsData.success) setStudents(studentsData.students)
        if (pendingData.success) setPendingRequests(pendingData.requests)
      } catch (error) {
        console.error("Error fetching data:", error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  const modules = Array.from(new Set(students.map(s => s.module_title)))

  const filteredStudents = students.filter(s => {
    const matchesSearch = s.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          s.email?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesModule = moduleFilter === "all" || s.module_title === moduleFilter
    return matchesSearch && matchesModule
  })

  const getInitials = (name: string) => name?.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() || "?"

  const openStudentDetails = async (studentId: number) => {
    if (!studentId) return
    setSelectedStudent(studentId)
    setIsModalOpen(true)
    setIsDetailsLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/teacher/students/${studentId}`, { credentials: 'include' })
      const data = await res.json()
      if (data.success) setStudentDetails(data.student)
    } catch (error) {
      console.error("Error fetching student details:", error)
    } finally {
      setIsDetailsLoading(false)
    }
  }

  const handleApprove = async (req: any) => {
    try {
      const res = await fetch("http://localhost:8000/api/teacher/enrollments/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({ enrollment_id: req.id })
      })
      const data = await res.json()
      if (data.success) {
        toast.success(`Matrícula de ${req.student_name} aprobada`)
        setPendingRequests(prev => prev.filter(r => r.id !== req.id))
      } else {
        toast.error("Error: " + data.detail)
      }
    } catch (e) {
      toast.error("Error de conexión")
    }
  }

  const handleReject = async (req: any) => {
    try {
      const res = await fetch("http://localhost:8000/api/teacher/enrollments/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({ enrollment_id: req.id })
      })
      const data = await res.json()
      if (data.success) {
        toast.success(`Matrícula de ${req.student_name} rechazada`)
        setPendingRequests(prev => prev.filter(r => r.id !== req.id))
      }
    } catch (e) {
      toast.error("Error de conexión")
    }
  }

  const handleUnenroll = async (studentId: number, moduleId: number, moduleTitle: string) => {
    if (!confirm(`¿Estás seguro de que deseas desmatricular al estudiante de "${moduleTitle}"?`)) return
    try {
      const res = await fetch(`http://localhost:8000/api/classes/${moduleId}/unenroll/${studentId}`, {
        method: "POST", credentials: 'include'
      })
      const data = await res.json()
      if (data.success) {
        toast.success(`Estudiante desmatriculado de ${moduleTitle}`)
        setStudentDetails((prev: any) => ({
          ...prev,
          modules: prev.modules.filter((m: any) => m.id !== moduleId)
        }))
      }
    } catch (e) {
      toast.error("Error de conexión")
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Estudiantes</h1>
        <p className="text-muted-foreground">Gestiona matrículas y supervisa el progreso de tus alumnos.</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="students" className="flex items-center gap-2">
            <User className="w-4 h-4" /> Mis Estudiantes
          </TabsTrigger>
          <TabsTrigger value="requests" className="flex items-center gap-2 relative">
            <UserPlus className="w-4 h-4" /> Solicitudes
            {pendingRequests.length > 0 && (
              <span className="ml-1 bg-primary text-primary-foreground text-xs rounded-full px-2 py-0.5 font-bold">
                {pendingRequests.length}
              </span>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="students" className="space-y-4 mt-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Buscar por nombre o correo..." className="pl-9" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
            <div className="w-full sm:w-64">
              <Select value={moduleFilter} onValueChange={setModuleFilter}>
                <SelectTrigger><SelectValue placeholder="Filtrar por curso" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los cursos</SelectItem>
                  {modules.map(mod => <SelectItem key={mod} value={mod}>{mod}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
              ) : filteredStudents.length === 0 ? (
                <div className="flex justify-center items-center h-64 text-muted-foreground">No se encontraron estudiantes.</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Estudiante</TableHead>
                      <TableHead>Curso</TableHead>
                      <TableHead>Progreso</TableHead>
                      <TableHead>Última Actividad</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead className="text-right">Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredStudents.map((student, idx) => (
                      <TableRow key={idx}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-9 w-9"><AvatarFallback>{getInitials(student.full_name)}</AvatarFallback></Avatar>
                            <div className="flex flex-col">
                              <span className="font-medium">{student.full_name}</span>
                              <span className="text-xs text-muted-foreground">{student.email}</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell><span className="truncate max-w-[150px] inline-block" title={student.module_title}>{student.module_title}</span></TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={student.progress} className="w-16 h-2" />
                            <span className="text-xs">{student.progress}%</span>
                          </div>
                        </TableCell>
                        <TableCell><span className="text-xs text-muted-foreground">{student.last_activity ? new Date(student.last_activity).toLocaleDateString() : 'N/A'}</span></TableCell>
                        <TableCell>
                          <Badge variant={student.status === 'Activo' ? 'default' : student.status === 'Completado' ? 'secondary' : 'destructive'}
                            className={student.status === 'Activo' ? 'bg-green-500/10 text-green-500 hover:bg-green-500/20' : ''}>
                            {student.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm" onClick={() => openStudentDetails(student.id)}>Ver Detalle</Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requests" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <UserPlus className="w-4 h-4 text-primary" />
                Solicitudes de Matrícula Pendientes
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {pendingRequests.length === 0 ? (
                <div className="flex justify-center items-center h-48 text-muted-foreground">No hay solicitudes pendientes.</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Estudiante</TableHead>
                      <TableHead>Curso</TableHead>
                      <TableHead>Solicitado</TableHead>
                      <TableHead className="text-right">Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingRequests.map((req) => (
                      <TableRow key={req.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-9 w-9"><AvatarFallback>{getInitials(req.student_name)}</AvatarFallback></Avatar>
                            <div className="flex flex-col">
                              <span className="font-medium">{req.student_name}</span>
                              <span className="text-xs text-muted-foreground">{req.student_email}</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{req.class_title}</TableCell>
                        <TableCell><span className="text-xs text-muted-foreground">{new Date(req.enrolled_at).toLocaleDateString()}</span></TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Button size="sm" variant="default" className="bg-green-600 hover:bg-green-700" onClick={() => handleApprove(req)}>
                              <CheckCircle2 className="w-4 h-4 mr-1" /> Aprobar
                            </Button>
                            <Button size="sm" variant="destructive" onClick={() => handleReject(req)}>
                              <XCircle className="w-4 h-4 mr-1" /> Rechazar
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-xl">
          {isDetailsLoading ? (
            <div className="flex justify-center items-center h-48">
              <div className="sr-only"><DialogTitle>Cargando</DialogTitle><DialogDescription>Espera...</DialogDescription></div>
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : studentDetails ? (
            <>
              <DialogHeader>
                <div className="flex items-center gap-4">
                  <Avatar className="h-16 w-16"><AvatarFallback className="text-xl">{getInitials(studentDetails.full_name)}</AvatarFallback></Avatar>
                  <div>
                    <DialogTitle className="text-xl">{studentDetails.full_name}</DialogTitle>
                    <DialogDescription>{studentDetails.email}</DialogDescription>
                  </div>
                </div>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4 my-4">
                <div className="rounded-lg border p-3 flex flex-col justify-center items-center bg-card">
                  <span className="text-sm text-muted-foreground flex items-center gap-1"><BookOpen className="w-4 h-4"/> Módulos</span>
                  <span className="text-2xl font-bold">{studentDetails.modules?.length || 0}</span>
                </div>
                <div className="rounded-lg border p-3 flex flex-col justify-center items-center bg-card">
                  <span className="text-sm text-muted-foreground flex items-center gap-1"><Activity className="w-4 h-4 text-orange-500"/> Racha</span>
                  <span className="text-2xl font-bold">{studentDetails.streak_days || 0} días</span>
                </div>
              </div>
              <div className="space-y-4 mt-2">
                <h4 className="font-semibold text-sm">Progreso por Módulo</h4>
                {studentDetails.modules?.map((mod: any) => (
                  <div key={mod.id} className="rounded-lg border p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-sm">{mod.title}</span>
                      <Badge variant="outline" className="text-[10px]">{mod.status}</Badge>
                    </div>
                    <div className="flex items-center gap-3">
                      <Progress value={mod.progress} className="h-2 flex-1" />
                      <span className="text-xs font-bold text-primary">{mod.progress}%</span>
                    </div>
                    <div className="mt-2 text-xs text-muted-foreground flex justify-between">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Última act: {mod.last_activity ? new Date(mod.last_activity).toLocaleDateString() : 'N/A'}</span>
                      {mod.progress < 30 && mod.status === 'active' && <span className="text-red-500 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> En riesgo</span>}
                    </div>
                    <div className="mt-4 pt-3 border-t border-border flex justify-end">
                      <Button variant="destructive" size="sm" onClick={() => handleUnenroll(studentDetails.id, mod.id, mod.title)}>Desmatricular</Button>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <div className="sr-only"><DialogTitle>Error</DialogTitle><DialogDescription>Error al cargar</DialogDescription></div>
              Error al cargar datos del estudiante.
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}