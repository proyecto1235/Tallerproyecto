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
import { Trophy, ArrowLeft, Loader2 } from "lucide-react"

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        ...formData,
        deadline: formData.deadline || null,
        max_attempts: formData.max_attempts || 0
      }

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/challenges`, {
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

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
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
                <Input id="title" required value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })} placeholder="Ej. Cazador de Errores" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="deadline">Fecha Límite</Label>
                <Input id="deadline" type="datetime-local" value={formData.deadline} onChange={e => setFormData({ ...formData, deadline: e.target.value })} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descripción / Instrucciones</Label>
              <Textarea id="description" required rows={4} value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} placeholder="Explica qué debe hacer el estudiante..." />
            </div>

            <div className="space-y-2">
              <Label htmlFor="instructions">Instrucciones detalladas para el editor</Label>
              <Textarea id="instructions" rows={3} value={formData.instructions} onChange={e => setFormData({ ...formData, instructions: e.target.value })} placeholder="# Escribe el código base inicial aquí\n# o deja instrucciones para el estudiante" className="font-mono text-sm" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="difficulty">Dificultad (1-5)</Label>
                <Input id="difficulty" type="number" min="1" max="5" required value={formData.difficulty} onChange={e => setFormData({ ...formData, difficulty: parseInt(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="points">Puntos (Estrellas)</Label>
                <Input id="points" type="number" min="10" required value={formData.points} onChange={e => setFormData({ ...formData, points: parseInt(e.target.value) })} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Tipo de Validación</Label>
                <Select value={formData.solution_type} onValueChange={v => setFormData({ ...formData, solution_type: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="output">Comparar Output</SelectItem>
                    <SelectItem value="test">Tests Unitarios</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="max_attempts">Intentos máximos (0 = ilimitado)</Label>
                <Input id="max_attempts" type="number" min="0" value={formData.max_attempts} onChange={e => setFormData({ ...formData, max_attempts: parseInt(e.target.value) })} />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="base_code">Código base para el estudiante</Label>
              <Textarea id="base_code" rows={5} className="font-mono text-sm" value={formData.base_code} onChange={e => setFormData({ ...formData, base_code: e.target.value })} placeholder="# Código que verá el estudiante al iniciar el reto" />
            </div>

            {formData.solution_type === "output" ? (
              <div className="space-y-2">
                <Label htmlFor="solution_output">Output esperado</Label>
                <Textarea id="solution_output" rows={4} className="font-mono text-sm" value={formData.solution_output} onChange={e => setFormData({ ...formData, solution_output: e.target.value })} placeholder="Escribe el output exacto que debe producir el código correcto" />
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="test_code">Código de test</Label>
                <Textarea id="test_code" rows={6} className="font-mono text-sm" value={formData.test_code} onChange={e => setFormData({ ...formData, test_code: e.target.value })} placeholder="# Código de test que validará la solución del estudiante\n# Se ejecutará después del código del estudiante" />
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="solution_code">Código de solución (visible después de la fecha límite)</Label>
              <Textarea id="solution_code" rows={6} className="font-mono text-sm" value={formData.solution_code} onChange={e => setFormData({ ...formData, solution_code: e.target.value })} placeholder="# Solución completa del reto" />
            </div>

            <div className="flex items-center gap-4">
              <Label htmlFor="is_published">Publicar inmediatamente:</Label>
              <input type="checkbox" id="is_published" checked={formData.is_published} onChange={e => setFormData({ ...formData, is_published: e.target.checked })} className="h-4 w-4" />
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