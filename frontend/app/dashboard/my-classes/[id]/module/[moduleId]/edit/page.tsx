"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, ArrowLeft, Save, Plus, Trash, Code, Eye, Edit3, GripVertical, Play } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import CodeMirror from '@uiw/react-codemirror'
import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
import { languages } from '@codemirror/language-data'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { toast } from "sonner"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { InlineExercise } from "@/components/interactive/InlineExercise"

const STORAGE_KEY = "robolearn_teacher_classes"

interface ClassExercise {
  id: string
  title: string
  description: string
  instructions: string
  exercise_type: "coding"
  difficulty: number
  points: number
}

interface ClassModuleData {
  id: string
  title: string
  description: string
  theory_content: string
  order: number
  exercises: ClassExercise[]
}

export default function ModuleEditPage() {
  const params = useParams()
  const router = useRouter()
  const classId = params.id as string
  const moduleId = params.moduleId as string

  const [mod, setMod] = useState<ClassModuleData | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [content, setContent] = useState("")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [exercises, setExercises] = useState<ClassExercise[]>([])
  const [showAddExercise, setShowAddExercise] = useState(false)
  const [editingExercise, setEditingExercise] = useState<ClassExercise | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const all = JSON.parse(saved)
      const cls = all.find((c: any) => c.id === classId)
      if (cls) {
        const found = (cls.modules || []).find((m: any) => m.id === moduleId)
        if (found) {
          setMod(found)
          setTitle(found.title)
          setDescription(found.description || "")
          setContent(found.theory_content || `# ${found.title}\n\nEscribe aquí el contenido...`)
          setExercises(found.exercises || [])
        }
      }
    }
    setLoading(false)
  }, [classId, moduleId])

  const saveModule = () => {
    setSaving(true)
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const all = JSON.parse(saved)
      const clsIdx = all.findIndex((c: any) => c.id === classId)
      if (clsIdx >= 0) {
        const modIdx = all[clsIdx].modules.findIndex((m: any) => m.id === moduleId)
        if (modIdx >= 0) {
          all[clsIdx].modules[modIdx] = {
            ...all[clsIdx].modules[modIdx],
            title,
            description,
            theory_content: content,
            exercises
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(all))
          toast.success("Módulo guardado")
        }
      }
    }
    setSaving(false)
  }

  const addExercise = () => {
    const newEx: ClassExercise = {
      id: Math.random().toString(36).substring(2, 10),
      title: "",
      description: "",
      instructions: "# Escribe tu código aquí\n\n",
      exercise_type: "coding",
      difficulty: 1,
      points: 10
    }
    setEditingExercise(newEx)
    setShowAddExercise(true)
  }

  const saveExercise = () => {
    if (!editingExercise?.title.trim()) {
      toast.error("El título del ejercicio es obligatorio")
      return
    }
    if (editingExercise.id && exercises.find(e => e.id === editingExercise.id)) {
      setExercises(exercises.map(e => e.id === editingExercise.id ? editingExercise : e))
    } else {
      setExercises([...exercises, { ...editingExercise, id: Math.random().toString(36).substring(2, 10) }])
    }
    setShowAddExercise(false)
    setEditingExercise(null)
    toast.success("Ejercicio guardado")
  }

  const deleteExercise = (id: string) => {
    if (!confirm("¿Eliminar este ejercicio?")) return
    setExercises(exercises.filter(e => e.id !== id))
    toast.success("Ejercicio eliminado")
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (!mod) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <h2 className="text-2xl font-bold">Módulo no encontrado</h2>
        <Button onClick={() => router.push(`/dashboard/my-classes/${classId}`)} variant="outline"><ArrowLeft className="w-4 h-4 mr-2" />Volver</Button>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.push(`/dashboard/my-classes/${classId}`)}>
          <ArrowLeft className="w-4 h-4 mr-2" />Volver a la clase
        </Button>
        <Button onClick={saveModule} disabled={saving}>
          {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
          Guardar Módulo
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Información del Módulo</CardTitle>
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
                      value={content}
                      height="500px"
                      theme={oneDark}
                      extensions={[markdown({ base: markdownLanguage, codeLanguages: languages })]}
                      onChange={v => setContent(v)}
                    />
                  </div>
                </TabsContent>
                <TabsContent value="preview">
                  <div className="prose prose-invert max-w-none border border-border rounded-md p-6 min-h-[300px] bg-card/80">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Code className="w-5 h-5 text-primary" />
                Ejercicios ({exercises.length})
              </CardTitle>
              <Button size="sm" onClick={addExercise}><Plus className="h-4 w-4 mr-1" />Añadir</Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {exercises.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">No hay ejercicios aún</p>
              ) : (
                exercises.map((ex, i) => (
                  <div key={ex.id} className="border border-border rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium truncate flex-1">{ex.title || `Ejercicio ${i + 1}`}</span>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => { setEditingExercise({ ...ex }); setShowAddExercise(true) }}>
                          <Edit3 className="w-3 h-3" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive" onClick={() => deleteExercise(ex.id)}>
                          <Trash className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground flex gap-2">
                      <span>{ex.points} pts</span>
                      <span>· Dificultad: {ex.difficulty}/5</span>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {exercises.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="w-5 h-5 text-green-500" />
                  Vista Previa del Ejercicio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <InlineExercise exercise={exercises[0]} />
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <Dialog open={showAddExercise} onOpenChange={(o) => { setShowAddExercise(o); if (!o) setEditingExercise(null) }}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingExercise?.id && exercises.find(e => e.id === editingExercise.id) ? "Editar Ejercicio" : "Nuevo Ejercicio"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Título del ejercicio</Label>
              <Input value={editingExercise?.title || ""} onChange={e => setEditingExercise(p => ({ ...p!, title: e.target.value }))} placeholder="Ej: Variables en acción" />
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea value={editingExercise?.description || ""} onChange={e => setEditingExercise(p => ({ ...p!, description: e.target.value }))} rows={2} />
            </div>
            <div className="space-y-2">
              <Label>Código inicial del ejercicio</Label>
              <div className="border rounded-md overflow-hidden">
                <CodeMirror
                  value={editingExercise?.instructions || ""}
                  height="200px"
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
            <Button variant="outline" onClick={() => { setShowAddExercise(false); setEditingExercise(null) }}>Cancelar</Button>
            <Button onClick={saveExercise}>Guardar Ejercicio</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}