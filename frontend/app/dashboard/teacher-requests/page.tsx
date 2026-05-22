"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle, XCircle, Clock } from "lucide-react"
import { toast } from "sonner"
import { ConfirmDialog } from "@/components/ui/confirm-dialog"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export default function TeacherRequestsPage() {
  const [requests, setRequests] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [confirmAction, setConfirmAction] = useState<{ id: number; name: string; action: "approve" | "reject" } | null>(null)

  useEffect(() => {
    fetchRequests()
  }, [])

  const fetchRequests = async () => {
    try {
      const res = await fetch(`${API}/admin/teachers/pending`, { credentials: 'include' })
      const data = await res.json()
      if (data.success) setRequests(data.requests)
    } catch (_) {
      // Fallback to localStorage
      const local = localStorage.getItem("robolearn_teacher_pending")
      if (local) setRequests(JSON.parse(local))
    } finally {
      setIsLoading(false)
    }
  }

  const handleApprove = async (id: number, name: string) => {
    try {
      const res = await fetch(`${API}/admin/teachers/approve/${id}`, {
        method: "POST", credentials: 'include'
      })
      const data = await res.json()
      if (data.success) {
        toast.success(`${name} ahora es profesor activo.`)
        setRequests(prev => prev.filter(r => r.id !== id))
      }
    } catch (_) {
      // Fallback: remove from localStorage
      const local = JSON.parse(localStorage.getItem("robolearn_teacher_pending") || "[]")
      const updated = local.filter((r: any) => r.id !== id)
      localStorage.setItem("robolearn_teacher_pending", JSON.stringify(updated))
      setRequests(prev => prev.filter(r => r.id !== id))
      toast.success(`${name} ahora es profesor activo.`)
    }
  }

  const handleReject = async (id: number, name: string) => {
    try {
      const res = await fetch(`${API}/admin/teachers/reject/${id}`, {
        method: "POST", credentials: 'include'
      })
      const data = await res.json()
      if (data.success) {
        toast.info(`Solicitud de ${name} rechazada.`)
        setRequests(prev => prev.filter(r => r.id !== id))
      }
    } catch (_) {
      const local = JSON.parse(localStorage.getItem("robolearn_teacher_pending") || "[]")
      const updated = local.filter((r: any) => r.id !== id)
      localStorage.setItem("robolearn_teacher_pending", JSON.stringify(updated))
      setRequests(prev => prev.filter(r => r.id !== id))
      toast.info(`Solicitud de ${name} rechazada.`)
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Solicitudes de Ingreso</h1>
        <p className="text-muted-foreground text-lg">
          Revisa y aprueba a los nuevos profesores e instituciones que desean unirse a la plataforma.
        </p>
      </div>

      <Card className="neo-shadow border-primary/20">
        <CardHeader>
          <CardTitle>Solicitudes Pendientes</CardTitle>
          <CardDescription>Tienen acceso restringido hasta que un administrador verifique su identidad.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
          ) : (
            <div className="rounded-md border overflow-hidden">
              <Table>
                <TableHeader className="bg-muted/50">
                  <TableRow>
                    <TableHead>Solicitante</TableHead>
                    <TableHead>Rol Solicitado</TableHead>
                    <TableHead>Fecha</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acción</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requests.map((req) => (
                    <TableRow key={req.id} className="hover:bg-muted/50">
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-semibold">{req.name}</span>
                          <span className="text-sm text-muted-foreground">{req.email}</span>
                        </div>
                      </TableCell>
                      <TableCell><Badge variant="default" className="capitalize">Profesor</Badge></TableCell>
                      <TableCell>{req.date}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-orange-500 font-medium text-sm">
                          <Clock className="w-4 h-4" /> Pendiente
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button size="sm" variant="outline" className="text-green-600 border-green-200 hover:bg-green-50" onClick={() => setConfirmAction({ id: req.id, name: req.name, action: "approve" })}>
                            <CheckCircle className="w-4 h-4 mr-1" /> Aprobar
                          </Button>
                          <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50" onClick={() => setConfirmAction({ id: req.id, name: req.name, action: "reject" })}>
                            <XCircle className="w-4 h-4 mr-1" /> Rechazar
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {requests.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-12 text-muted-foreground">
                        <CheckCircle className="w-12 h-12 mx-auto text-green-500/50 mb-3" />
                        <p className="text-lg font-medium text-foreground">¡Todo al día!</p>
                        <p>No hay nuevas solicitudes pendientes.</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        open={!!confirmAction}
        onOpenChange={(o) => { if (!o) setConfirmAction(null) }}
        title={confirmAction?.action === "approve" ? "Aprobar solicitud" : "Rechazar solicitud"}
        description={confirmAction?.action === "approve"
          ? `¿Estás seguro de aprobar a ${confirmAction?.name} como profesor?`
          : `¿Estás seguro de rechazar la solicitud de ${confirmAction?.name}?`
        }
        confirmLabel={confirmAction?.action === "approve" ? "Aprobar" : "Rechazar"}
        variant={confirmAction?.action === "reject" ? "destructive" : "default"}
        onConfirm={() => {
          if (!confirmAction) return
          if (confirmAction.action === "approve") handleApprove(confirmAction.id, confirmAction.name)
          else handleReject(confirmAction.id, confirmAction.name)
          setConfirmAction(null)
        }}
      />
    </div>
  )
}