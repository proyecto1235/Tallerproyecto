"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "sonner"
import dynamic from "next/dynamic"
import { python } from "@codemirror/lang-python"
import { Trophy, ArrowLeft, Loader2, Code } from "lucide-react"
import API from "@/lib/api"

const CodeEditor = dynamic(
  () => import("@uiw/react-codemirror").then(mod => ({ default: mod.default })),
  { ssr: false }
)

export default function CreateChallengePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    instructions: "",
    difficulty: 1,
    points: 100,
    base_code: "",
    solution_code: "",
    solution_type: "output",
    solution_output: "",
    test_code: "",
    deadline: "",
    is_published: true,
    max_attempts: 0
  })

  const updateField = (field: string, value: any) => setFormData(prev => ({ ...prev, [field]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        ...formData,
        deadline: formData.deadline || null,
        max_attempts: formData.max_attempts || 0
      }

      const res = await fetch(`${API}/challenges`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload)
      })

      const data = await res.json()
      if (data.success) {
        toast.success("Reto creado exitosamente")
        router.push("/dashboard/challenges")
      } else {
        toast.error("Error: " + (data.detail || data.error))
      }
    } catch (error) {
      toast.error("Error de red")
    } finally {
      setLoading(false)
    }
  }

  const editorTheme: React.CSSProperties = { backgroundColor: "#1e1e1e", color: "#d4d4d4" }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => router.back()} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Volver
        </Button>
      </div>

      <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Trophy className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-2xl">Crear Nuevo Reto</CardTitle>
              <CardDescription>Plantea un desafío de programación con código base, solución y fecha límite.</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Título del Reto</Label>
                <Input id="title" required value={formData.title} onChange={e => updateField("title", e.target.value)} placeholder="Ej. Cazador de Errores" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="deadline">Fecha Límite</Label>
                <Input id="deadline" type="datetime-local" value={formData.deadline} onChange={e => updateField("deadline", e.target.value)} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descripción / Instrucciones</Label>
              <Textarea id="description" required rows={4} value={formData.description} onChange={e => updateField("description", e.target.value)} placeholder="Explica qué debe hacer el estudiante..." />
            </div>

            <div className="space-y-2">
              <Label htmlFor="instrucciones">Instrucciones detalladas (se muestran en el editor del estudiante)</Label>
              <div className="rounded-lg overflow-hidden border border-border">
                {typeof window !== "undefined" && (
                  <CodeEditor
                    value={formData.instructions}
                    height="120px"
                    theme="dark"
                    extensions={[python()]}
                    onChange={v => updateField("instructions", v)}
                    style={editorTheme}
                  />
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="difficulty">Dificultad (1-5)</Label>
                <Input id="difficulty" type="number" min="1" max="5" required value={formData.difficulty} onChange={e => updateField("difficulty", parseInt(e.target.value))} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="points">Puntos (Estrellas)</Label>
                <Input id="points" type="number" min="10" required value={formData.points} onChange={e => updateField("points", parseInt(e.target.value))} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Tipo de Validación</Label>
                <Select value={formData.solution_type} onValueChange={v => updateField("solution_type", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="output">Comparar Output</SelectItem>
                    <SelectItem value="test">Tests Unitarios</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_attempts">Intentos máximos (0 = ilimitado)</Label>
                <Input id="max_attempts" type="number" min="0" value={formData.max_attempts} onChange={e => updateField("max_attempts", parseInt(e.target.value))} />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2"><Code className="w-4 h-4" /> Código base para el estudiante</Label>
              <div className="rounded-lg overflow-hidden border border-border">
                {typeof window !== "undefined" && (
                  <CodeEditor
                    value={formData.base_code}
                    height="150px"
                    theme="dark"
                    extensions={[python()]}
                    onChange={v => updateField("base_code", v)}
                    style={editorTheme}
                  />
                )}
              </div>
            </div>

            {formData.solution_type === "output" ? (
              <div className="space-y-2">
                <Label className="flex items-center gap-2"><Code className="w-4 h-4" /> Output esperado</Label>
                <div className="rounded-lg overflow-hidden border border-border">
                  {typeof window !== "undefined" && (
                    <CodeEditor
                      value={formData.solution_output}
                      height="120px"
                      theme="dark"
                      extensions={[python()]}
                      onChange={v => updateField("solution_output", v)}
                      style={editorTheme}
                    />
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <Label className="flex items-center gap-2"><Code className="w-4 h-4" /> Código de test</Label>
                <div className="rounded-lg overflow-hidden border border-border">
                  {typeof window !== "undefined" && (
                    <CodeEditor
                      value={formData.test_code}
                      height="180px"
                      theme="dark"
                      extensions={[python()]}
                      onChange={v => updateField("test_code", v)}
                      style={editorTheme}
                    />
                  )}
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label className="flex items-center gap-2"><Code className="w-4 h-4" /> Código de solución (visible después de la fecha límite)</Label>
              <div className="rounded-lg overflow-hidden border border-border">
                {typeof window !== "undefined" && (
                  <CodeEditor
                    value={formData.solution_code}
                    height="180px"
                    theme="dark"
                    extensions={[python()]}
                    onChange={v => updateField("solution_code", v)}
                    style={editorTheme}
                  />
                )}
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Label htmlFor="is_published">Publicar inmediatamente:</Label>
              <input type="checkbox" id="is_published" checked={formData.is_published} onChange={e => updateField("is_published", e.target.checked)} className="h-4 w-4" />
            </div>

            <Button type="submit" disabled={loading} className="w-full">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Creando..." : "Crear Reto"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
