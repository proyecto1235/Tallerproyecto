"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Loader2, ArrowLeft, Plus, BookOpen, Code, Pencil, Trash, FileText, UserCheck, UserX, Check, X } from "lucide-react"
import { toast } from "sonner"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"
import { ConfirmDialog } from "@/components/ui/confirm-dialog"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ClassModule {
  id: string
  title: string
  description: string
  theory_content: string
  order: number
  exercise_count: number
}

interface EnrollmentRequest {
  id: number
  student_id: number
  student_name: string
  student_email: string
  status: string
  enrolled_at: string
}

export default function ClassDetailPage() {
  const params = useParams()
  const router = useRouter()
  const classId = parseInt(params.id as string, 10)

  const [cls, setCls] = useState<any>(null)
  const [modules, setModules] = useState<ClassModule[]>([])
  const [requests, setRequests] = useState<EnrollmentRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModule, setShowCreateModule] = useState(false)
  const [newModule, setNewModule] = useState({ title: "", description: "" })
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

  useEffect(() => {
    if (!classId) return
    loadData()
  }, [classId])

  async function loadData() {
    setLoading(true)
    try {
      const [classRes, reqRes] = await Promise.all([
        fetch(`${API}/classes/${classId}`, { credentials: "include" }),
        fetch(`${API}/classes/${classId}/requests`, { credentials: "include" })
      ])
      const classData = await classRes.json()
      if (classData.success) {
        setCls(classData.class)
        setModules((classData.class.modules || []).map((m: any, i: number) => ({
          id: m.id?.toString() || String(i),
          title: m.title,
          description: m.description || "",
          theory_content: m.theory_content || "",
          order: m.order || i + 1,
          exercise_count: m.exercises?.length || 0
        })))
      }
      const reqData = await reqRes.json()
      if (reqData.success) {
        setRequests(reqData.requests || [])
      }
    } catch (_) {
      // Fallback to localStorage
      const saved = localStorage.getItem("robolearn_teacher_classes")
      if (saved) {
        const all = JSON.parse(saved)
        const found = all.find((c: any) => c.id === params.id)
        if (found) {
          setCls(found)
          setModules((found.modules || []).map((m: any, i: number) => ({
            ...m,
            exercise_count: m.exercises?.length || 0,
            order: m.order || i + 1
          })))
        }
      }
    }
    setLoading(false)
  }

  async function handleEnrollAction(studentId: number, action: "approve" | "reject") {
    try {
      const res = await fetch(`${API}/classes/${classId}/${action}/${studentId}`, {
        method: "POST",
        credentials: "include"
      })
      const data = await res.json()
      if (data.success) {
        toast.success(action === "approve" ? "Matrícula aprobada" : "Matrícula rechazada")
        setRequests(prev => prev.filter(r => r.student_id !== studentId))
      } else {
        toast.error(data.error || "Error al procesar solicitud")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
  }

  const handleDeleteModule = (id: string) => {
    setConfirmDelete(id)
  }

  const confirmDeleteModule = async () => {
    if (!confirmDelete) return
    try {
      const res = await fetch(`${API}/classes/${classId}/modules/${confirmDelete}`, {
        method: "DELETE", credentials: "include"
      })
      const data = await res.json()
      if (data.success) {
        const updated = modules.filter(m => m.id !== confirmDelete).map((m, i) => ({ ...m, order: i + 1 }))
        setModules(updated)
        toast.success("Módulo eliminado")
      } else {
        toast.error(data.error || "Error al eliminar módulo")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
    setConfirmDelete(null)
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (!cls) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <h2 className="text-2xl font-bold">Clase no encontrada</h2>
        <Button onClick={() => router.push('/dashboard/my-classes')} variant="outline"><ArrowLeft className="w-4 h-4 mr-2" />Volver</Button>
      </div>
    )
  }

  const pendingRequests = requests.filter(r => r.status === "pending")

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <Button variant="ghost" onClick={() => router.push('/dashboard/my-classes')}>
        <ArrowLeft className="w-4 h-4 mr-2" />Mis Clases
      </Button>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
            <BookOpen className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{cls.title}</h1>
            <p className="text-muted-foreground">{cls.category} · {cls.difficulty}</p>
          </div>
        </div>
      </div>

      {cls.description && (
        <Card>
          <CardContent className="p-4 text-sm text-muted-foreground">{cls.description}</CardContent>
        </Card>
      )}

      {/* Enrollment Requests */}
      {pendingRequests.length > 0 && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-500">
              <UserCheck className="w-5 h-5" />
              Solicitudes de Matrícula ({pendingRequests.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {pendingRequests.map((req) => (
              <div key={req.id} className="flex items-center justify-between p-3 rounded-lg border border-amber-500/20 bg-card">
                <div>
                  <p className="font-medium">{req.student_name}</p>
                  <p className="text-sm text-muted-foreground">{req.student_email}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleEnrollAction(req.student_id, "approve")}>
                    <Check className="w-4 h-4 mr-1" /> Aprobar
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => handleEnrollAction(req.student_id, "reject")}>
                    <X className="w-4 h-4 mr-1" /> Rechazar
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary" />
          Módulos de la Clase ({modules.length})
        </h2>
        <Button onClick={() => setShowCreateModule(true)} size="sm">
          <Plus className="h-4 w-4 mr-2" />Añadir Módulo
        </Button>
      </div>

      {modules.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground border-2 border-dashed rounded-xl">
          <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="font-medium mb-1">No hay módulos aún</p>
          <p className="text-sm mb-4">Crea el primer módulo de tu clase</p>
          <Button onClick={() => setShowCreateModule(true)} variant="outline"><Plus className="h-4 w-4 mr-2" />Crear Módulo</Button>
        </div>
      ) : (
        <div className="space-y-3">
          {modules.map((mod, index) => (
            <Card key={mod.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                    {mod.order}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{mod.title}</h3>
                    <p className="text-xs text-muted-foreground">{mod.description || "Sin descripción"} · {mod.exercise_count} ejercicios</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={() => router.push(`/dashboard/my-classes/${params.id}/module/${mod.id}/edit`)}>
                    <Pencil className="w-4 h-4 mr-1" /> Editar
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => handleDeleteModule(mod.id)}>
                    <Trash className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={showCreateModule} onOpenChange={setShowCreateModule}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nuevo Módulo</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Título del módulo</Label>
              <Input value={newModule.title} onChange={e => setNewModule(p => ({ ...p, title: e.target.value }))} placeholder="Ej: Introducción a Flask" />
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea value={newModule.description} onChange={e => setNewModule(p => ({ ...p, description: e.target.value }))} placeholder="Breve descripción del módulo" rows={2} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateModule(false)}>Cancelar</Button>
            <Button onClick={async () => {
              if (!newModule.title.trim()) { toast.error("El título es obligatorio"); return }
              try {
                const res = await fetch(`${API}/classes/${classId}/modules`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  credentials: "include",
                  body: JSON.stringify({
                    title: newModule.title,
                    description: newModule.description,
                    theory_content: `# ${newModule.title}\n\nEscribe aquí el contenido teórico...`,
                    order: modules.length + 1
                  })
                })
                const data = await res.json()
                if (data.success) {
                  const mod: ClassModule = {
                    id: String(data.module_id),
                    title: newModule.title,
                    description: newModule.description,
                    theory_content: `# ${newModule.title}\n\nEscribe aquí el contenido teórico...`,
                    order: modules.length + 1,
                    exercise_count: 0
                  }
                  setModules([...modules, mod])
                  toast.success("Módulo creado")
                } else {
                  toast.error(data.error || "Error al crear módulo")
                }
              } catch (_) {
                toast.error("Error de conexión")
              }
              setNewModule({ title: "", description: "" })
              setShowCreateModule(false)
            }}>Crear Módulo</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!confirmDelete}
        onOpenChange={(o) => { if (!o) setConfirmDelete(null) }}
        title="Eliminar módulo"
        description="¿Estás seguro de eliminar este módulo? Esta acción no se puede deshacer."
        confirmLabel="Eliminar"
        onConfirm={confirmDeleteModule}
        variant="destructive"
      />
    </div>
  )
}
