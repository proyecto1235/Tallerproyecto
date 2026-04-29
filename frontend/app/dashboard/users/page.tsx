"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Search, Loader2, Edit, Eye, Trash2, ShieldAlert } from "lucide-react"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"

const MOCK_USERS = [
  { id: 1, full_name: "Ana García", email: "ana@estudiante.com", role: "student", points: 150, status: "activo", registered_at: "2024-01-15" },
  { id: 2, full_name: "Carlos Profe", email: "carlos@profe.com", role: "teacher", points: 0, status: "activo", registered_at: "2024-01-10" },
  { id: 3, full_name: "Luis Rodríguez", email: "luis@estudiante.com", role: "student", points: 420, status: "inactivo", registered_at: "2024-02-05" },
  { id: 4, full_name: "Marta Sánchez", email: "marta@estudiante.com", role: "student", points: 890, status: "activo", registered_at: "2024-03-12" },
]

export default function UsersPage() {
  const { user } = useAuth()
  const [users, setUsers] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  
  // Modales
  const [selectedUser, setSelectedUser] = useState<any | null>(null)
  const [viewModalOpen, setViewModalOpen] = useState(false)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  
  const [editForm, setEditForm] = useState({ full_name: "", email: "", status: "", role: "" })

  const fetchUsers = async () => {
    setIsLoading(true)
    try {
      const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/$/, "")
      const res = await fetch(`${API_URL}/admin/users`, { 
        credentials: 'include' 
      })
      if (!res.ok) throw new Error("Backend no responde")
      const data = await res.json()
      if (data.success && data.users) {
        setUsers(data.users.filter((u: any) => u.role !== "admin"))
      } else {
        throw new Error("Estructura de datos inválida")
      }
    } catch (error) {
      console.info("Usando MOCK_USERS porque el backend no está disponible.")
      setUsers(MOCK_USERS)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleRoleChange = (userId: number, newRole: string) => {
    setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u))
    toast.success("Rol actualizado correctamente")
  }

  const handleDelete = () => {
    if (selectedUser) {
      setUsers(users.filter(u => u.id !== selectedUser.id))
      toast.success("Usuario eliminado correctamente")
      setDeleteModalOpen(false)
    }
  }

  const handleSaveEdit = () => {
    if (selectedUser) {
      setUsers(users.map(u => u.id === selectedUser.id ? { ...u, ...editForm } : u))
      toast.success("Usuario actualizado correctamente")
      setEditModalOpen(false)
    }
  }

  const openEditModal = (u: any) => {
    setSelectedUser(u)
    setEditForm({ full_name: u.full_name, email: u.email, status: u.status || "activo", role: u.role })
    setEditModalOpen(true)
  }

  const openViewModal = (u: any) => {
    setSelectedUser(u)
    setViewModalOpen(true)
  }

  const openDeleteModal = (u: any) => {
    setSelectedUser(u)
    setDeleteModalOpen(true)
  }

  const filteredUsers = users.filter(u => 
    u.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
    u.email?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const roleLabels: Record<string, string> = {
    student: "Estudiante",
    teacher: "Profesor",
    admin: "Administrador"
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Gestión de Usuarios</h1>
        <p className="text-muted-foreground text-lg">Administra las cuentas de estudiantes y profesores en la plataforma.</p>
      </div>

      <Card className="neo-shadow border-primary/20">
        <CardHeader className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <CardTitle>Usuarios Registrados</CardTitle>
          <div className="relative w-full md:w-auto">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar por nombre o email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-full md:w-80"
            />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="rounded-md border overflow-hidden">
              <Table>
                <TableHeader className="bg-muted/50">
                  <TableRow>
                    <TableHead>Nombre y Correo</TableHead>
                    <TableHead>Rol</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((u) => (
                    <TableRow key={u.id} className="hover:bg-muted/50">
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-semibold">{u.full_name}</span>
                          <span className="text-sm text-muted-foreground">{u.email}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={u.role === "teacher" ? "default" : "secondary"}>
                          {roleLabels[u.role] || u.role}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={u.status === "inactivo" ? "destructive" : "outline"} className="capitalize">
                          {u.status || "Activo"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="icon" onClick={() => openViewModal(u)} title="Ver detalles">
                            <Eye className="h-4 w-4 text-blue-500" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => openEditModal(u)} title="Editar usuario">
                            <Edit className="h-4 w-4 text-orange-500" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => openDeleteModal(u)} disabled={u.id === user?.id} title="Eliminar usuario">
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {filteredUsers.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                        No se encontraron usuarios que coincidan con la búsqueda.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal Ver Detalle */}
      <Dialog open={viewModalOpen} onOpenChange={setViewModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Detalles del Usuario</DialogTitle>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground">Nombre Completo</h4>
                  <p className="font-medium">{selectedUser.full_name}</p>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground">Correo Electrónico</h4>
                  <p className="font-medium">{selectedUser.email}</p>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground">Rol</h4>
                  <p className="font-medium capitalize">{roleLabels[selectedUser.role] || selectedUser.role}</p>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground">Puntos / Nivel</h4>
                  <p className="font-medium">{selectedUser.points || 0} pts</p>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground">Estado</h4>
                  <Badge variant={selectedUser.status === "inactivo" ? "destructive" : "default"} className="mt-1 capitalize">
                    {selectedUser.status || "Activo"}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-muted-foreground">Fecha de Registro</h4>
                  <p className="font-medium">{selectedUser.registered_at || "Reciente"}</p>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Modal Editar */}
      <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Usuario</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Nombre Completo</Label>
              <Input value={editForm.full_name} onChange={e => setEditForm({...editForm, full_name: e.target.value})} />
            </div>
            <div className="space-y-2">
              <Label>Correo Electrónico</Label>
              <Input type="email" value={editForm.email} onChange={e => setEditForm({...editForm, email: e.target.value})} />
            </div>
            <div className="space-y-2">
              <Label>Rol en la plataforma</Label>
              <Select value={editForm.role} onValueChange={v => setEditForm({...editForm, role: v})}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="student">Estudiante</SelectItem>
                  <SelectItem value="teacher">Profesor</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Estado de la cuenta</Label>
              <Select value={editForm.status} onValueChange={v => setEditForm({...editForm, status: v})}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="activo">Activo</SelectItem>
                  <SelectItem value="inactivo">Inactivo / Bloqueado</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setEditModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleSaveEdit}>Guardar Cambios</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Eliminar */}
      <Dialog open={deleteModalOpen} onOpenChange={setDeleteModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <ShieldAlert className="h-5 w-5" />
              Confirmar Eliminación
            </DialogTitle>
            <DialogDescription>
              ¿Estás seguro de que deseas eliminar permanentemente al usuario <strong className="text-foreground">{selectedUser?.full_name}</strong>? Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-4">
            <Button variant="ghost" onClick={() => setDeleteModalOpen(false)}>Cancelar</Button>
            <Button variant="destructive" onClick={handleDelete}>Sí, eliminar usuario</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
