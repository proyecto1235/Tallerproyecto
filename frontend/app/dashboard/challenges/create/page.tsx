"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { Trophy, ArrowLeft, Loader2 } from "lucide-react"

export default function CreateChallengePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    instructions: "# Escribe tu código aquí\n",
    difficulty: 1,
    points: 100
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/challenges`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData)
      })

      const data = await res.json()
      if (data.success) {
        toast.success("Reto creado exitosamente")
        router.push("/dashboard/challenges")
      } else {
        toast.error("Error: " + data.error)
      }
    } catch (error) {
      toast.error("Error de red")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
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
              <CardDescription>Plantea un desafío de programación para los estudiantes.</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Título del Reto</Label>
              <Input
                id="title"
                required
                value={formData.title}
                onChange={e => setFormData({ ...formData, title: e.target.value })}
                placeholder="Ej. Cazador de Errores: Variables"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Descripción / Instrucciones</Label>
              <Textarea
                id="description"
                required
                rows={4}
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                placeholder="Explica qué debe hacer el estudiante..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="difficulty">Dificultad (1-3)</Label>
                <Input
                  id="difficulty"
                  type="number"
                  min="1"
                  max="3"
                  required
                  value={formData.difficulty}
                  onChange={e => setFormData({ ...formData, difficulty: parseInt(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="points">Puntos (Estrellas)</Label>
                <Input
                  id="points"
                  type="number"
                  min="10"
                  required
                  value={formData.points}
                  onChange={e => setFormData({ ...formData, points: parseInt(e.target.value) })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="instructions">Código base (Opcional)</Label>
              <Textarea
                id="instructions"
                rows={6}
                className="font-mono text-sm"
                value={formData.instructions}
                onChange={e => setFormData({ ...formData, instructions: e.target.value })}
              />
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
