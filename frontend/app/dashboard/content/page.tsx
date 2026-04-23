"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, Plus, Save, BookOpen, Trash } from "lucide-react"
import CodeMirror from '@uiw/react-codemirror'
import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
import { languages } from '@codemirror/language-data'
import { oneDark } from '@codemirror/theme-one-dark'
import { toast } from "sonner"

export default function ContentPage() {
  const { user } = useAuth()
  const [modules, setModules] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  
  const [editingModule, setEditingModule] = useState<any>(null)

  const fetchModules = async () => {
    setIsLoading(true)
    try {
      const res = await fetch("http://localhost:8000/api/modules", {
        credentials: 'include'
      })
      const data = await res.json()
      if (data.success) {
        // En una implementación real, filtraríamos por teacher_id.
        // Como el backend lista todos los publicados, usaremos esto para demostración.
        setModules(data.modules.filter((m: any) => m.teacher_id === user?.id))
      }
    } catch (error) {
      console.error("Error al obtener módulos", error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchModules()
  }, [user])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const url = editingModule.id 
        ? `http://localhost:8000/api/modules/${editingModule.id}`
        : `http://localhost:8000/api/modules`
        
      const method = editingModule.id ? "PUT" : "POST"
      
      const payload = {
        title: editingModule.title,
        description: editingModule.description,
        order: editingModule.order || 0,
        is_published: true // Autopublicar para esta demo
      }

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify(payload)
      })

      const data = await res.json()
      if (data.success) {
        toast.success(editingModule.id ? "Módulo actualizado" : "Módulo creado")
        setEditingModule(null)
        fetchModules()
      } else {
        toast.error(data.detail || "Error al guardar")
      }
    } catch (error) {
      toast.error("Error de red")
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm("¿Solicitar eliminación de este módulo?")) return
    try {
      const res = await fetch(`http://localhost:8000/api/modules/${id}`, { 
        method: "DELETE",
        credentials: 'include'
      })
      if (res.ok) {
        toast.success("Solicitud de eliminación enviada al admin")
        fetchModules()
      }
    } catch (error) {
      toast.error("Error al solicitar eliminación")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestión de Contenido</h1>
          <p className="text-muted-foreground">Crea y edita el material para tus clases usando Markdown</p>
        </div>
        {!editingModule && (
          <Button onClick={() => setEditingModule({ title: "Nuevo Módulo", description: "# Escribe aquí el contenido..." })}>
            <Plus className="h-4 w-4 mr-2" />
            Crear Módulo
          </Button>
        )}
      </div>

      {editingModule ? (
        <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Editor de Módulo</CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setEditingModule(null)}>Cancelar</Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Guardar
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Título de la Clase / Módulo</Label>
              <Input 
                value={editingModule.title} 
                onChange={(e) => setEditingModule({...editingModule, title: e.target.value})} 
              />
            </div>
            <div className="space-y-2">
              <Label>Contenido (Markdown soportado)</Label>
              <div className="border border-border rounded-md overflow-hidden">
                <CodeMirror
                  value={editingModule.description}
                  height="400px"
                  theme={oneDark}
                  extensions={[markdown({ base: markdownLanguage, codeLanguages: languages })]}
                  onChange={(val) => setEditingModule({...editingModule, description: val})}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
            ) : modules.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No tienes módulos creados. ¡Crea el primero!</div>
            ) : (
              <div className="divide-y divide-border">
                {modules.map((m: any) => (
                  <div key={m.id} className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-primary/10 text-primary rounded-lg">
                        <BookOpen className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{m.title}</h3>
                        <p className="text-sm text-muted-foreground truncate max-w-md">Estado: {m.status}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setEditingModule(m)}>
                        Editar
                      </Button>
                      <Button variant="destructive" size="sm" onClick={() => handleDelete(m.id)}>
                        <Trash className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
