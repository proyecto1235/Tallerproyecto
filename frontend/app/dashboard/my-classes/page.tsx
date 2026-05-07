"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Loader2, Plus, BookOpen, Users, Pencil, Trash, Globe, Lock, ChevronRight, GraduationCap } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { toast } from "sonner"

const STORAGE_KEY = "robolearn_teacher_classes"

interface TeacherClass {
  id: string
  title: string
  description: string
  category: string
  difficulty: string
  is_published: boolean
  modules: ClassModule[]
  student_count: number
  created_at: string
}

interface ClassModule {
  id: string
  title: string
  description: string
  theory_content: string
  order: number
  exercises: ClassExercise[]
}

interface ClassExercise {
  id: string
  title: string
  description: string
  instructions: string
  exercise_type: "coding"
  difficulty: number
  points: number
}

const DEMO_CLASSES: TeacherClass[] = [
  {
    id: "tc-1", title: "Desarrollo Web con Python", description: "Aprende a crear aplicaciones web usando Django y Flask. Desde HTML básico hasta APIs REST.",
    category: "Desarrollo Web", difficulty: "Intermedio", is_published: true,
    modules: [
      { id: "tcm-1", title: "Introducción a HTML", description: "Estructura básica de páginas web", theory_content: "# HTML Básico", order: 1, exercises: [] },
      { id: "tcm-2", title: "Flask: Tu Primer Servidor", description: "Crea un servidor web con Flask", theory_content: "# Flask", order: 2, exercises: [] }
    ],
    student_count: 12, created_at: "2024-01-15"
  },
  {
    id: "tc-2", title: "Robótica Educativa", description: "Construye y programa robots con Python y Arduino.",
    category: "Robótica", difficulty: "Avanzado", is_published: false,
    modules: [
      { id: "tcm-3", title: "Motores y Actuadores", description: "Controla motores DC y servos", theory_content: "# Motores", order: 1, exercises: [] }
    ],
    student_count: 8, created_at: "2024-02-20"
  },
  {
    id: "tc-3", title: "Introducción a la IA", description: "Conceptos básicos de inteligencia artificial con Python.",
    category: "Inteligencia Artificial", difficulty: "Avanzado", is_published: true,
    modules: [], student_count: 5, created_at: "2024-03-10"
  },
]

function generateId() {
  return Math.random().toString(36).substring(2, 10)
}

export default function MyClassesPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [classes, setClasses] = useState<TeacherClass[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [editingClass, setEditingClass] = useState<Partial<TeacherClass> | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      setClasses(JSON.parse(saved))
    } else {
      setClasses(DEMO_CLASSES)
    }
    setLoading(false)
  }, [])

  const saveClasses = (updated: TeacherClass[]) => {
    setClasses(updated)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
  }

  const handleCreate = () => {
    setEditingClass({
      title: "", description: "", category: "Desarrollo Web", difficulty: "Principiante", is_published: false
    })
    setShowCreate(true)
  }

  const handleSave = () => {
    if (!editingClass?.title?.trim()) {
      toast.error("El título es obligatorio")
      return
    }
    const now = new Date().toISOString()
    if (editingClass.id) {
      const updated = classes.map(c => c.id === editingClass.id ? { ...c, ...editingClass } as TeacherClass : c)
      saveClasses(updated)
      toast.success("Clase actualizada")
    } else {
      const newClass: TeacherClass = {
        id: generateId(),
        title: editingClass.title,
        description: editingClass.description || "",
        category: editingClass.category || "General",
        difficulty: editingClass.difficulty || "Principiante",
        is_published: editingClass.is_published || false,
        modules: [],
        student_count: 0,
        created_at: now
      }
      saveClasses([newClass, ...classes])
      toast.success("Clase creada")
    }
    setShowCreate(false)
    setEditingClass(null)
  }

  const handleDelete = (id: string) => {
    if (!confirm("¿Eliminar esta clase?")) return
    saveClasses(classes.filter(c => c.id !== id))
    toast.success("Clase eliminada")
  }

  const togglePublish = (id: string) => {
    saveClasses(classes.map(c => c.id === id ? { ...c, is_published: !c.is_published } : c))
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  const totalStudents = classes.reduce((s, c) => s + c.student_count, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Mis Clases</h1>
          <p className="text-muted-foreground">Gestiona tus clases y crea contenido educativo</p>
        </div>
        <Button onClick={handleCreate}><Plus className="h-4 w-4 mr-2" />Crear Clase</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-primary/10 p-3 rounded-lg text-primary"><BookOpen className="w-6 h-6" /></div>
            <div><p className="text-sm text-muted-foreground">Tus Clases</p><p className="text-2xl font-bold">{classes.length}</p></div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-green-500/10 p-3 rounded-lg text-green-500"><Globe className="w-6 h-6" /></div>
            <div><p className="text-sm text-muted-foreground">Publicadas</p><p className="text-2xl font-bold">{classes.filter(c => c.is_published).length}</p></div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="bg-amber-500/10 p-3 rounded-lg text-amber-500"><Users className="w-6 h-6" /></div>
            <div><p className="text-sm text-muted-foreground">Estudiantes</p><p className="text-2xl font-bold">{totalStudents}</p></div>
          </CardContent>
        </Card>
      </div>

      {classes.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground">
          <GraduationCap className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <h3 className="text-lg font-medium mb-1">No tienes clases creadas</h3>
          <p className="mb-4">Crea tu primera clase para empezar</p>
          <Button onClick={handleCreate}><Plus className="h-4 w-4 mr-2" />Crear Clase</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {classes.map(cls => (
            <Card key={cls.id} className="relative overflow-hidden hover:shadow-lg transition-shadow">
              <div className={`absolute top-0 left-0 w-1 h-full ${cls.is_published ? 'bg-green-500' : 'bg-amber-500'}`} />
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{cls.category}</span>
                    <CardTitle className="text-lg mt-1">{cls.title}</CardTitle>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => togglePublish(cls.id)} className="shrink-0">
                    {cls.is_published ? <Globe className="w-4 h-4 text-green-500" /> : <Lock className="w-4 h-4 text-amber-500" />}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{cls.description}</p>
                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
                  <span className="flex items-center gap-1"><BookOpen className="w-3 h-3" /> {cls.modules.length} módulos</span>
                  <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {cls.student_count} estudiantes</span>
                  <span>{cls.difficulty}</span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" className="flex-1 group" onClick={() => router.push(`/dashboard/my-classes/${cls.id}`)}>
                    Gestionar <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => { setEditingClass(cls); setShowCreate(true); }}>
                    <Pencil className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(cls.id)}>
                    <Trash className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={showCreate} onOpenChange={(o) => { setShowCreate(o); if (!o) setEditingClass(null) }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingClass?.id ? "Editar Clase" : "Crear Nueva Clase"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Título de la clase</Label>
              <Input value={editingClass?.title || ""} onChange={e => setEditingClass(p => ({ ...p, title: e.target.value }))} placeholder="Ej: Desarrollo Web con Python" />
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea value={editingClass?.description || ""} onChange={e => setEditingClass(p => ({ ...p, description: e.target.value }))} placeholder="Describe el contenido de la clase..." rows={3} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Categoría</Label>
                <Select value={editingClass?.category || "Desarrollo Web"} onValueChange={v => setEditingClass(p => ({ ...p, category: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {["Desarrollo Web", "Robótica", "Inteligencia Artificial", "Ciencia de Datos", "Videojuegos", "Bases de Datos", "Ciberseguridad", "General"].map(c => (
                      <SelectItem key={c} value={c}>{c}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Dificultad</Label>
                <Select value={editingClass?.difficulty || "Principiante"} onValueChange={v => setEditingClass(p => ({ ...p, difficulty: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {["Principiante", "Intermedio", "Avanzado"].map(d => (
                      <SelectItem key={d} value={d}>{d}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowCreate(false); setEditingClass(null) }}>Cancelar</Button>
            <Button onClick={handleSave}>{editingClass?.id ? "Guardar Cambios" : "Crear Clase"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}