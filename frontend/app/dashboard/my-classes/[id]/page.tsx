"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Loader2, ArrowLeft, Plus, BookOpen, Code, Pencil, Trash, ChevronRight, GripVertical, FileText } from "lucide-react"
import { toast } from "sonner"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"

const STORAGE_KEY = "robolearn_teacher_classes"

interface ClassModule {
  id: string
  title: string
  description: string
  theory_content: string
  order: number
  exercise_count: number
}

interface TeacherClass {
  id: string
  title: string
  description: string
  category: string
  difficulty: string
  is_published: boolean
  modules: any[]
  student_count: number
}

export default function ClassDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [cls, setCls] = useState<TeacherClass | null>(null)
  const [modules, setModules] = useState<ClassModule[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModule, setShowCreateModule] = useState(false)
  const [newModule, setNewModule] = useState({ title: "", description: "" })

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const all: TeacherClass[] = JSON.parse(saved)
      const found = all.find(c => c.id === params.id)
      if (found) {
        setCls(found)
        setModules((found.modules || []).map((m: any, i: number) => ({
          ...m,
          exercise_count: m.exercises?.length || 0,
          order: m.order || i + 1
        })))
      }
    }
    setLoading(false)
  }, [params.id])

  const saveModules = (updated: ClassModule[]) => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const all: TeacherClass[] = JSON.parse(saved)
      const idx = all.findIndex(c => c.id === params.id)
      if (idx >= 0) {
        all[idx].modules = updated
        localStorage.setItem(STORAGE_KEY, JSON.stringify(all))
        setModules(updated)
      }
    }
  }

  const handleAddModule = () => {
    if (!newModule.title.trim()) {
      toast.error("El título es obligatorio")
      return
    }
    const mod: ClassModule = {
      id: Math.random().toString(36).substring(2, 10),
      title: newModule.title,
      description: newModule.description,
      theory_content: `# ${newModule.title}\n\nEscribe aquí el contenido teórico...`,
      order: modules.length + 1,
      exercise_count: 0
    }
    saveModules([...modules, mod])
    setNewModule({ title: "", description: "" })
    setShowCreateModule(false)
    toast.success("Módulo creado")
  }

  const handleDeleteModule = (id: string) => {
    if (!confirm("¿Eliminar este módulo?")) return
    saveModules(modules.filter(m => m.id !== id).map((m, i) => ({ ...m, order: i + 1 })))
    toast.success("Módulo eliminado")
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
            <p className="text-muted-foreground">{cls.category} · {cls.difficulty} · {cls.student_count} estudiantes</p>
          </div>
        </div>
      </div>

      {cls.description && (
        <Card>
          <CardContent className="p-4 text-sm text-muted-foreground">{cls.description}</CardContent>
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
            <Button onClick={handleAddModule}>Crear Módulo</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}