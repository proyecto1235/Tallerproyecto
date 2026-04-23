"use client"

import { useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { Settings as SettingsIcon, Save, Loader2 } from "lucide-react"

export default function SettingsPage() {
  const { user, login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    fullName: user?.fullName || "",
    email: user?.email || "",
    password: ""
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target
    setFormData(prev => ({ ...prev, [id]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const res = await fetch("http://localhost:8000/api/users/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify(formData)
      })

      const data = await res.json()

      if (res.ok) {
        toast.success("Perfil actualizado correctamente")
        // No we don't update login here, but ideally we refresh context or re-fetch profile.
      } else {
        toast.error(data.detail || "Error al actualizar perfil")
      }
    } catch (error) {
      toast.error("Error de conexión")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <SettingsIcon className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ajustes</h1>
          <p className="text-muted-foreground">Configura tu perfil y preferencias de cuenta</p>
        </div>
      </div>

      <Card className="max-w-2xl neo-shadow border-primary/20 bg-card/80 backdrop-blur">
        <CardHeader>
          <CardTitle>Perfil Personal</CardTitle>
          <CardDescription>Actualiza tu información personal. Solo cambia tu contraseña si es necesario.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fullName">Nombre Completo</Label>
              <Input 
                id="fullName" 
                value={formData.fullName} 
                onChange={handleChange} 
                placeholder="Tu nombre" 
                required 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico</Label>
              <Input 
                id="email" 
                type="email" 
                value={formData.email} 
                onChange={handleChange} 
                placeholder="tu@robolearn.com" 
                required 
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Nueva Contraseña (opcional)</Label>
              <Input 
                id="password" 
                type="password" 
                value={formData.password} 
                onChange={handleChange} 
                placeholder="Déjalo en blanco para no cambiarla" 
              />
            </div>
            
            <Button type="submit" disabled={isLoading} className="w-full sm:w-auto">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Guardar Cambios
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
