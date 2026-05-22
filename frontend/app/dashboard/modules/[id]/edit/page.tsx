"use client"

import { useState, useEffect, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, ArrowLeft, Save, Eye, Edit3, Plus, Trash, Code, BookOpen } from "lucide-react"
import CodeMirror from '@uiw/react-codemirror'
import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
import { languages } from '@codemirror/language-data'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { toast } from "sonner"
import { MarkdownContent } from "@/components/ui/markdown-content"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Lesson {
  id: number
  title: string
  theory: string
  order: number
  exercises: Exercise[]
}

interface Exercise {
  id: number
  title: string
  description: string
  instructions: string
  difficulty: number
  points: number
  solution_output: string | null
  solution_type: string
  order: number
}

export default function AdminModuleEditPage() {
  const params = useParams()
  const router = useRouter()
  const moduleId = params.id as string

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [difficulty, setDifficulty] = useState("Principiante")
  const [theoryContent, setTheoryContent] = useState("")
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [activeTab, setActiveTab] = useState("module")
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null)
  const [showLessonDialog, setShowLessonDialog] = useState(false)
  const [editingLesson, setEditingLesson] = useState<Partial<Lesson> | null>(null)
  const [showExerciseDialog, setShowExerciseDialog] = useState(false)
  const [editingExercise, setEditingExercise] = useState<Partial<Exercise> | null>(null)

  useEffect(() => {
    loadModule()
  }, [moduleId])

  async function loadModule() {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/modules/${moduleId}`, { credentials: "include" })
      const data = await res.json()
      if (data.success && data.module) {
        const m = data.module
        setTitle(m.title || "")
        setDescription(m.description || "")
        setDifficulty(m.difficulty || "Principiante")
        setTheoryContent(m.theory_content || "")
        setLessons(m.lessons || [])
      } else {
        toast.error("Módulo no encontrado")
      }
    } catch (_) {
      toast.error("Error al cargar módulo")
    }
    setLoading(false)
  }

  async function handleSave() {
    setSaving(true)
    try {
      const res = await fetch(`${API_URL}/modules/${moduleId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ title, description, difficulty })
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Módulo actualizado")
      } else {
        toast.error(data.error || "Error al actualizar")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
    setSaving(false)
  }

  async function handleSaveTheory() {
    setSaving(true)
    try {
      const res = await fetch(`${API_URL}/modules/${moduleId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ theory_content: theoryContent })
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Contenido guardado")
      } else {
        toast.error(data.error || "Error al guardar")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
    setSaving(false)
  }

  function openNewLesson() {
    setEditingLesson({ title: "", theory: "# Nueva Lección\n\n", order: lessons.length })
    setShowLessonDialog(true)
  }

  function openEditLesson(lesson: Lesson) {
    setEditingLesson({ ...lesson })
    setShowLessonDialog(true)
  }

  async function saveLesson() {
    if (!editingLesson?.title?.trim()) { toast.error("El título es obligatorio"); return }
    const isNew = !editingLesson.id
    const url = isNew
      ? `${API_URL}/modules/${moduleId}/lessons`
      : `${API_URL}/modules/${moduleId}/lessons/${editingLesson.id}`
    try {
      const res = await fetch(url, {
        method: isNew ? "POST" : "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          title: editingLesson.title,
          theory_content: editingLesson.theory,
          order: editingLesson.order ?? lessons.length
        })
      })
      const data = await res.json()
      if (data.success) {
        toast.success(isNew ? "Lección creada" : "Lección actualizada")
        setShowLessonDialog(false)
        setEditingLesson(null)
        const modRes = await fetch(`${API_URL}/modules/${moduleId}`, { credentials: "include" })
        const modData = await modRes.json()
        if (modData.success) setLessons(modData.module.lessons || [])
      } else {
        toast.error(data.error || "Error al guardar")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
  }

  async function deleteLesson(id: number) {
    if (!confirm("¿Eliminar esta lección y todos sus ejercicios?")) return
    try {
      const res = await fetch(`${API_URL}/modules/${moduleId}/lessons/${id}`, {
        method: "DELETE", credentials: "include"
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Lección eliminada")
        setLessons(lessons.filter(l => l.id !== id))
      } else {
        toast.error(data.error || "Error al eliminar")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
  }

  function openNewExercise(lesson: Lesson) {
    setSelectedLesson(lesson)
    setEditingExercise({
      title: "", description: "", instructions: "# Escribe tu código aquí\n\n",
      difficulty: 1, points: 10, solution_output: null, solution_type: "output"
    })
    setShowExerciseDialog(true)
  }

  function openEditExercise(lesson: Lesson, ex: Exercise) {
    setSelectedLesson(lesson)
    setEditingExercise({ ...ex })
    setShowExerciseDialog(true)
  }

  async function saveExercise() {
    if (!selectedLesson || !editingExercise?.title?.trim()) { toast.error("El título es obligatorio"); return }
    const isNew = !editingExercise.id
    const url = isNew
      ? `${API_URL}/modules/${moduleId}/exercises`
      : `${API_URL}/modules/${moduleId}/exercises/${editingExercise.id}`
    try {
      const res = await fetch(url, {
        method: isNew ? "POST" : "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          lesson_id: selectedLesson.id,
          title: editingExercise.title,
          description: editingExercise.description,
          instructions: editingExercise.instructions,
          difficulty: editingExercise.difficulty,
          points: editingExercise.points,
          solution_output: editingExercise.solution_output,
          solution_type: editingExercise.solution_type
        })
      })
      const data = await res.json()
      if (data.success) {
        toast.success(isNew ? "Ejercicio creado" : "Ejercicio actualizado")
        setShowExerciseDialog(false)
        setEditingExercise(null)
        const modRes = await fetch(`${API_URL}/modules/${moduleId}`, { credentials: "include" })
        const modData = await modRes.json()
        if (modData.success) setLessons(modData.module.lessons || [])
      } else {
        toast.error(data.error || "Error al guardar")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
  }

  async function deleteExercise(lessonId: number, exerciseId: number) {
    if (!confirm("¿Eliminar este ejercicio?")) return
    try {
      const res = await fetch(`${API_URL}/modules/${moduleId}/exercises/${exerciseId}`, {
        method: "DELETE", credentials: "include"
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Ejercicio eliminado")
        const modRes = await fetch(`${API_URL}/modules/${moduleId}`, { credentials: "include" })
        const modData = await modRes.json()
        if (modData.success) setLessons(modData.module.lessons || [])
      } else {
        toast.error(data.error || "Error al eliminar")
      }
    } catch (_) {
      toast.error("Error de conexión")
    }
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.push("/dashboard/modules")}>
          <ArrowLeft className="w-4 h-4 mr-2" /> Volver
        </Button>
        <div className="flex gap-2">
          <Button onClick={handleSaveTheory} disabled={saving} variant="outline">
            {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
            Guardar Contenido
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="module"><Edit3 className="w-4 h-4 mr-2" />Módulo</TabsTrigger>
          <TabsTrigger value="lessons"><BookOpen className="w-4 h-4 mr-2" />Lecciones y Ejercicios</TabsTrigger>
        </TabsList>

        <TabsContent value="module" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Editar Módulo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Título</Label>
                <Input value={title} onChange={e => setTitle(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Descripción</Label>
                <Textarea value={description} onChange={e => setDescription(e.target.value)} rows={2} />
              </div>
              <div className="space-y-2">
                <Label>Dificultad</Label>
                <select
                  value={difficulty}
                  onChange={e => setDifficulty(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                >
                  <option value="Principiante">Principiante</option>
                  <option value="Intermedio">Intermedio</option>
                  <option value="Avanzado">Avanzado</option>
                </select>
              </div>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Guardar Módulo
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-primary" />
                Contenido Teórico (Markdown)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="editor">
                <TabsList className="mb-4">
                  <TabsTrigger value="editor"><Edit3 className="w-4 h-4 mr-2" />Editor</TabsTrigger>
                  <TabsTrigger value="preview"><Eye className="w-4 h-4 mr-2" />Vista Previa</TabsTrigger>
                </TabsList>
                <TabsContent value="editor">
                  <div className="border border-border rounded-md overflow-hidden">
                    <CodeMirror
                      value={theoryContent}
                      height="600px"
                      theme={oneDark}
                      extensions={[markdown({ base: markdownLanguage, codeLanguages: languages })]}
                      onChange={v => setTheoryContent(v)}
                    />
                  </div>
                </TabsContent>
                <TabsContent value="preview">
                  <div className="border border-border rounded-md p-6 min-h-[300px] bg-card/80">
                    <MarkdownContent content={theoryContent} />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="lessons" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">Lecciones ({lessons.length})</h2>
            <Button onClick={openNewLesson} size="sm"><Plus className="w-4 h-4 mr-2" />Nueva Lección</Button>
          </div>

          {lessons.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground border-2 border-dashed rounded-xl">
              <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="font-medium mb-1">No hay lecciones aún</p>
              <p className="text-sm mb-4">Crea la primera lección de este módulo</p>
              <Button onClick={openNewLesson} variant="outline"><Plus className="w-4 h-4 mr-2" />Crear Lección</Button>
            </div>
          ) : (
            <div className="space-y-4">
              {lessons.map((lesson) => (
                <Card key={lesson.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary font-bold text-sm">
                          {lesson.order + 1}
                        </span>
                        <CardTitle className="text-lg">{lesson.title}</CardTitle>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => openEditLesson(lesson)}>
                          <Edit3 className="w-3 h-3 mr-1" /> Editar
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => deleteLesson(lesson.id)}>
                          <Trash className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm text-muted-foreground">{lesson.exercises.length} ejercicios</span>
                      <Button size="sm" variant="outline" onClick={() => openNewExercise(lesson)}>
                        <Plus className="w-3 h-3 mr-1" /> Añadir Ejercicio
                      </Button>
                    </div>
                    {lesson.exercises.length > 0 && (
                      <div className="space-y-2">
                        {lesson.exercises.map((ex) => (
                          <div key={ex.id} className="flex items-center justify-between p-2 rounded border border-border">
                            <div className="flex items-center gap-2">
                              <Code className="w-4 h-4 text-muted-foreground" />
                              <span className="text-sm">{ex.title}</span>
                              <span className="text-xs text-muted-foreground">{ex.points} pts · D: {ex.difficulty}/5</span>
                            </div>
                            <div className="flex gap-1">
                              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openEditExercise(lesson, ex)}>
                                <Edit3 className="w-3 h-3" />
                              </Button>
                              <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive" onClick={() => deleteExercise(lesson.id, ex.id)}>
                                <Trash className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      <Dialog open={showLessonDialog} onOpenChange={(o) => { setShowLessonDialog(o); if (!o) setEditingLesson(null) }}>
        <DialogContent className="sm:max-w-3xl max-h-[85vh]">
          <DialogHeader>
            <DialogTitle>{editingLesson?.id ? "Editar Lección" : "Nueva Lección"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 overflow-y-auto pr-1 max-h-[calc(85vh-120px)]">
            <div className="space-y-2">
              <Label>Título</Label>
              <Input value={editingLesson?.title || ""} onChange={e => setEditingLesson(p => ({ ...p!, title: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>Contenido (Markdown)</Label>
              <div className="border rounded-md overflow-hidden">
                <CodeMirror
                  value={editingLesson?.theory || ""}
                  height="250px"
                  theme={oneDark}
                  extensions={[markdown({ base: markdownLanguage, codeLanguages: languages })]}
                  onChange={v => setEditingLesson(p => ({ ...p!, theory: v }))}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowLessonDialog(false); setEditingLesson(null) }}>Cancelar</Button>
            <Button onClick={saveLesson}>Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showExerciseDialog} onOpenChange={(o) => { setShowExerciseDialog(o); if (!o) setEditingExercise(null) }}>
        <DialogContent className="sm:max-w-2xl max-h-[85vh]">
          <DialogHeader>
            <DialogTitle>{editingExercise?.id ? "Editar Ejercicio" : "Nuevo Ejercicio"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 overflow-y-auto pr-1 max-h-[calc(85vh-120px)]">
            <div className="space-y-2">
              <Label>Título</Label>
              <Input value={editingExercise?.title || ""} onChange={e => setEditingExercise(p => ({ ...p!, title: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea value={editingExercise?.description || ""} onChange={e => setEditingExercise(p => ({ ...p!, description: e.target.value }))} rows={2} />
            </div>
            <div className="space-y-2">
              <Label>Código inicial</Label>
              <div className="border rounded-md overflow-hidden">
                <CodeMirror
                  value={editingExercise?.instructions || ""}
                  height="180px"
                  theme={oneDark}
                  extensions={[python()]}
                  onChange={v => setEditingExercise(p => ({ ...p!, instructions: v }))}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Dificultad (1-5)</Label>
                <Select value={String(editingExercise?.difficulty || 1)} onValueChange={v => setEditingExercise(p => ({ ...p!, difficulty: parseInt(v) }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5].map(d => <SelectItem key={d} value={String(d)}>{d} - {d <= 2 ? 'Fácil' : d <= 3 ? 'Media' : 'Difícil'}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Puntos</Label>
                <Input type="number" value={editingExercise?.points || 10} onChange={e => setEditingExercise(p => ({ ...p!, points: parseInt(e.target.value) || 0 }))} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowExerciseDialog(false); setEditingExercise(null) }}>Cancelar</Button>
            <Button onClick={saveExercise}>Guardar Ejercicio</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
