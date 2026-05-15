"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, Shield, CheckCircle2, XCircle, Eye, FileText, BookOpen } from "lucide-react"
import { toast } from "sonner"

const statusLabels: Record<string, string> = {
  pending_review: "Pendiente de Revisión",
  pending_deletion: "Pendiente de Eliminación",
  draft: "Borrador",
  approved: "Aprobado",
  rejected: "Rechazado",
}

const statusColors: Record<string, string> = {
  pending_review: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
  pending_deletion: "bg-red-500/10 text-red-600 border-red-500/20",
  draft: "bg-gray-500/10 text-gray-600 border-gray-500/20",
  approved: "bg-green-500/10 text-green-600 border-green-500/20",
  rejected: "bg-red-500/10 text-red-600 border-red-500/20",
}

export default function ContentReviewPage() {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedModule, setSelectedModule] = useState<any>(null)
  const [moduleLoading, setModuleLoading] = useState(false)

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/admin/content-review", { credentials: 'include' })
      const data = await res.json()
      if (data.success) setItems(data.items)
    } catch (e) {
      console.error("Error fetching content review items", e)
    } finally {
      setLoading(false)
    }
  }

  const handleViewModule = async (moduleId: number) => {
    setModuleLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/admin/modules/${moduleId}`, { credentials: 'include' })
      const data = await res.json()
      if (data.success) setSelectedModule(data.module)
    } catch (e) {
      toast.error("Error al cargar módulo")
    } finally {
      setModuleLoading(false)
    }
  }

  const handleApprove = async (moduleId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/admin/modules/${moduleId}/approve`, {
        method: "POST", credentials: 'include'
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Módulo aprobado y publicado")
        setItems(prev => prev.filter(i => i.id !== moduleId))
        setSelectedModule(null)
      }
    } catch (e) {
      toast.error("Error al aprobar")
    }
  }

  const handleReject = async (moduleId: number) => {
    const feedback = prompt("Razón del rechazo (opcional):")
    try {
      const res = await fetch(`http://localhost:8000/api/admin/modules/${moduleId}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({ feedback: feedback || "" })
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Módulo rechazado")
        setItems(prev => prev.filter(i => i.id !== moduleId))
        setSelectedModule(null)
      }
    } catch (e) {
      toast.error("Error al rechazar")
    }
  }

  const handleApproveDeletion = async (moduleId: number) => {
    if (!confirm("¿Estás seguro de eliminar este módulo definitivamente?")) return
    try {
      const res = await fetch(`http://localhost:8000/api/admin/modules/${moduleId}/approve-deletion`, {
        method: "POST", credentials: 'include'
      })
      const data = await res.json()
      if (data.success) {
        toast.success("Módulo eliminado")
        setItems(prev => prev.filter(i => i.id !== moduleId))
        setSelectedModule(null)
      }
    } catch (e) {
      toast.error("Error")
    }
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Revisión de Contenido</h1>
        <p className="text-muted-foreground">Gestiona las solicitudes de publicación y eliminación de módulos.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Contenido Pendiente
              </CardTitle>
              <CardDescription>Módulos que requieren revisión o aprobación.</CardDescription>
            </CardHeader>
            <CardContent>
              {items.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No hay contenido pendiente de revisión.</p>
              ) : (
                <div className="space-y-3">
                  {items.map((item) => (
                    <Card key={item.id} className="border-muted cursor-pointer hover:border-primary/30 transition-colors" onClick={() => handleViewModule(item.id)}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge className={statusColors[item.status] || "bg-gray-500/10"} variant="outline">
                                {statusLabels[item.status] || item.status}
                              </Badge>
                              <span className="text-xs text-muted-foreground">por {item.teacher_name}</span>
                            </div>
                            <h3 className="font-bold">{item.title}</h3>
                            {item.description && <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{item.description}</p>}
                          </div>
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-primary" />
                Módulos Globales
              </CardTitle>
              <CardDescription>Edita directamente el contenido de los módulos globales.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" onClick={async () => {
                try {
                  const res = await fetch("http://localhost:8000/api/admin/modules", { credentials: 'include' })
                  const data = await res.json()
                  if (data.success) {
                    const globalMods = data.modules.filter((m: any) => m.is_global)
                    if (globalMods.length > 0) handleViewModule(globalMods[0].id)
                  }
                } catch (e) {
                  toast.error("Error al cargar módulos globales")
                }
              }}>
                Ver Módulos Globales
              </Button>
            </CardContent>
          </Card>
        </div>

        <div>
          {moduleLoading ? (
            <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin" /></div>
          ) : selectedModule ? (
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-primary" />
                      {selectedModule.title}
                    </CardTitle>
                    <CardDescription>
                      por {selectedModule.teacher_name} · {selectedModule.lessons?.length || 0} lecciones · {selectedModule.exercises?.length || 0} ejercicios
                    </CardDescription>
                  </div>
                  <Badge className={statusColors[selectedModule.status]} variant="outline">
                    {statusLabels[selectedModule.status] || selectedModule.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {selectedModule.description && (
                  <div>
                    <h4 className="text-sm font-bold text-muted-foreground mb-1">Descripción</h4>
                    <p className="text-sm">{selectedModule.description}</p>
                  </div>
                )}

                {selectedModule.theory_content && (
                  <div>
                    <h4 className="text-sm font-bold text-muted-foreground mb-1">Contenido teórico</h4>
                    <pre className="text-xs font-mono bg-muted p-3 rounded-lg max-h-40 overflow-y-auto whitespace-pre-wrap">{selectedModule.theory_content.substring(0, 500)}...</pre>
                  </div>
                )}

                {selectedModule.exercises && selectedModule.exercises.length > 0 && (
                  <div>
                    <h4 className="text-sm font-bold text-muted-foreground mb-2">Ejercicios</h4>
                    <div className="space-y-2">
                      {selectedModule.exercises.map((ex: any) => (
                        <div key={ex.id} className="flex items-center justify-between text-sm bg-muted/30 p-2 rounded-lg">
                          <span>{ex.title}</span>
                          <span className="text-xs text-muted-foreground">Dificultad: {ex.difficulty}/5 · {ex.points} pts</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedModule.status === "pending_review" && (
                  <div className="flex gap-3 pt-4 border-t">
                    <Button className="bg-green-600 hover:bg-green-700 flex-1" onClick={() => handleApprove(selectedModule.id)}>
                      <CheckCircle2 className="w-4 h-4 mr-2" /> Aprobar
                    </Button>
                    <Button variant="destructive" className="flex-1" onClick={() => handleReject(selectedModule.id)}>
                      <XCircle className="w-4 h-4 mr-2" /> Rechazar
                    </Button>
                  </div>
                )}

                {selectedModule.status === "pending_deletion" && (
                  <div className="flex gap-3 pt-4 border-t">
                    <Button variant="destructive" onClick={() => handleApproveDeletion(selectedModule.id)}>
                      <CheckCircle2 className="w-4 h-4 mr-2" /> Aprobar Eliminación
                    </Button>
                  </div>
                )}

                {selectedModule.is_global && selectedModule.status === "approved" && (
                  <div className="pt-4 border-t">
                    <Button variant="outline" className="w-full" onClick={() => {
                      const content = prompt("Editar descripción del módulo:", selectedModule.description || "")
                      if (content) {
                        fetch(`http://localhost:8000/api/admin/modules/${selectedModule.id}/content`, {
                          method: "PUT",
                          headers: { "Content-Type": "application/json" },
                          credentials: 'include',
                          body: JSON.stringify({ description: content })
                        }).then(r => r.json()).then(d => {
                          if (d.success) toast.success("Contenido actualizado")
                        })
                      }
                    }}>
                      Editar Contenido
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                <Shield className="w-12 h-12 mb-4 opacity-30" />
                <p>Selecciona un módulo para revisar</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}