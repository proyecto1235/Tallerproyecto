"use client"

import { useState, useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { toast } from "sonner"
import { Settings2, User, Bell, Shield, Palette, Loader2, CheckCircle2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const profileFormSchema = z.object({
  username: z.string().min(3, "El nombre debe tener al menos 3 caracteres."),
  email: z.string().email("Correo electrónico no válido."),
  bio: z.string().max(160, "La biografía no puede tener más de 160 caracteres.").optional(),
})

const PREDEFINED_AVATARS = [
  "https://api.dicebear.com/7.x/bottts/svg?seed=CoderNinja",
  "https://api.dicebear.com/7.x/bottts/svg?seed=RoboMaster",
  "https://api.dicebear.com/7.x/bottts/svg?seed=Byte",
  "https://api.dicebear.com/7.x/bottts/svg?seed=Pixel",
  "https://api.dicebear.com/7.x/bottts/svg?seed=Gizmo",
  "https://api.dicebear.com/7.x/bottts/svg?seed=Spark",
  "https://api.dicebear.com/7.x/bottts/svg?seed=Cyber",
  "https://api.dicebear.com/7.x/bottts/svg?seed=Nexus",
]

export default function SettingsPage() {
  const [savedProfile, setSavedProfile] = useState({
    username: "",
    email: "",
    bio: "",
    avatar_url: ""
  })
  
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isAvatarModalOpen, setIsAvatarModalOpen] = useState(false)
  const [selectedAvatar, setSelectedAvatar] = useState("")

  // Estado para la sección de Seguridad
  const [securityForm, setSecurityForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: ""
  })

  // Estado para Notificaciones
  const [notifications, setNotifications] = useState({
    newChallenges: true,
    studyReminders: true,
    teacherAnnouncements: true
  })

  const form = useForm<z.infer<typeof profileFormSchema>>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      username: "",
      email: "",
      bio: "",
    },
  })

  // Fetch initial profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/users/profile", {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          const profileData = {
            username: data.user.full_name || "",
            email: data.user.email || "",
            bio: data.user.bio || "",
            avatar_url: data.user.avatar_url || `https://api.dicebear.com/7.x/bottts/svg?seed=${data.user.full_name}`
          }
          setSavedProfile(profileData)
          setSelectedAvatar(profileData.avatar_url)
          form.reset({
            username: profileData.username,
            email: profileData.email,
            bio: profileData.bio,
          })
        } else {
          toast.error("No se pudo cargar el perfil.")
        }
      } catch (error) {
        console.error("Error fetching profile:", error)
        toast.error("Error de conexión al cargar el perfil.")
      } finally {
        setIsLoading(false)
      }
    }
    fetchProfile()
  }, [form])

  async function onSubmit(data: z.infer<typeof profileFormSchema>) {
    setIsSaving(true)
    try {
      const res = await fetch("http://localhost:8000/api/users/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({
          full_name: data.username,
          email: data.email,
          bio: data.bio,
          avatar_url: selectedAvatar
        })
      })
      const result = await res.json()
      
      if (result.success) {
        setSavedProfile({
          username: data.username,
          email: data.email,
          bio: data.bio || "",
          avatar_url: selectedAvatar
        })
        toast.success("Perfil actualizado correctamente")
      } else {
        toast.error(result.error || "No se pudo guardar el perfil.")
      }
    } catch (error) {
      console.error("Error updating profile:", error)
      toast.error("Error de conexión al guardar el perfil.")
    } finally {
      setIsSaving(false)
    }
  }

  const handleAvatarSelect = (url: string) => {
    setSelectedAvatar(url)
    setIsAvatarModalOpen(false)
  }

  const handleSecuritySubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!securityForm.currentPassword || !securityForm.newPassword || !securityForm.confirmPassword) {
      toast.error("Por favor completa todos los campos de contraseña.")
      return
    }
    if (securityForm.newPassword !== securityForm.confirmPassword) {
      toast.error("Las contraseñas nuevas no coinciden.")
      return
    }
    if (securityForm.newPassword.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres.")
      return
    }
    
    // Simular guardado
    toast.success("Contraseña actualizada con éxito")
    setSecurityForm({ currentPassword: "", newPassword: "", confirmPassword: "" })
  }

  const handleNotificationsSubmit = () => {
    toast.success("Preferencias de notificaciones guardadas")
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center gap-3">
          <Settings2 className="w-8 h-8 text-primary" />
          Ajustes
        </h1>
        <p className="text-muted-foreground text-lg">
          Configura tu perfil, preferencias y notificaciones de Robolearn.
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="bg-card border w-full justify-start h-auto p-1 flex-wrap neo-shadow gap-1">
          <TabsTrigger value="profile" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-2.5">
            <User className="w-4 h-4" /> Perfil
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-2.5">
            <Bell className="w-4 h-4" /> Notificaciones
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-2.5">
            <Shield className="w-4 h-4" /> Seguridad
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-2.5">
            <Palette className="w-4 h-4" /> Apariencia
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <Card className="neo-shadow border-primary/20">
            <CardHeader>
              <CardTitle>Perfil Público de {savedProfile.username}</CardTitle>
              <CardDescription>
                Esta es la información que verán otros estudiantes y tus profesores.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 mb-8">
                <Avatar className="w-24 h-24 border-4 border-background shadow-md">
                  <AvatarImage src={selectedAvatar} />
                  <AvatarFallback>{savedProfile.username.substring(0, 2).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div className="space-y-2 text-center sm:text-left mt-2 sm:mt-0">
                  <Button variant="outline" size="sm" onClick={() => setIsAvatarModalOpen(true)}>
                    Cambiar Avatar
                  </Button>
                  <p className="text-xs text-muted-foreground">Selecciona uno de los avatares disponibles.</p>
                </div>
              </div>

              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <FormField
                    control={form.control}
                    name="username"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Nombre de Usuario</FormLabel>
                        <FormControl>
                          <Input placeholder="CoderNinja" {...field} />
                        </FormControl>
                        <FormDescription>
                          Tu nombre público en la plataforma.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Correo Electrónico</FormLabel>
                        <FormControl>
                          <Input placeholder="tu@correo.com" {...field} />
                        </FormControl>
                        <FormDescription>
                          Utilizado para notificaciones y recuperación de cuenta.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="bio"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Biografía</FormLabel>
                        <FormControl>
                          <Input placeholder="Cuéntanos sobre ti..." {...field} />
                        </FormControl>
                        <FormDescription>
                          Una breve descripción sobre lo que te gusta aprender.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <div className="flex justify-end pt-4 border-t gap-4">
                    <Button 
                      type="button" 
                      variant="ghost" 
                      onClick={() => {
                        form.reset({
                          username: savedProfile.username,
                          email: savedProfile.email,
                          bio: savedProfile.bio,
                        })
                        setSelectedAvatar(savedProfile.avatar_url)
                      }}
                      disabled={isSaving}
                    >
                      Cancelar
                    </Button>
                    <Button type="submit" className="font-bold" disabled={isSaving}>
                      {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                      {isSaving ? "Guardando..." : "Guardar Cambios"}
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card className="neo-shadow border-primary/20">
            <CardHeader>
              <CardTitle>Preferencias de Notificaciones</CardTitle>
              <CardDescription>
                Decide qué alertas quieres recibir en tu correo o en la plataforma.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <h4 className="font-bold">Nuevos Retos</h4>
                    <p className="text-sm text-muted-foreground">Recibe alertas cuando se publique un reto semanal.</p>
                  </div>
                  <Switch 
                    checked={notifications.newChallenges} 
                    onCheckedChange={(val) => setNotifications(prev => ({...prev, newChallenges: val}))} 
                  />
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <h4 className="font-bold">Recordatorios de Estudio</h4>
                    <p className="text-sm text-muted-foreground">Te avisamos si estás a punto de perder tu racha.</p>
                  </div>
                  <Switch 
                    checked={notifications.studyReminders} 
                    onCheckedChange={(val) => setNotifications(prev => ({...prev, studyReminders: val}))} 
                  />
                </div>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <h4 className="font-bold">Anuncios del Profesor</h4>
                    <p className="text-sm text-muted-foreground">Mensajes importantes sobre tus clases.</p>
                  </div>
                  <Switch 
                    checked={notifications.teacherAnnouncements} 
                    onCheckedChange={(val) => setNotifications(prev => ({...prev, teacherAnnouncements: val}))} 
                  />
                </div>
              </div>
              <div className="flex justify-end pt-4 border-t gap-4">
                <Button type="button" variant="ghost" onClick={() => toast.info("Cambios descartados")}>Cancelar</Button>
                <Button type="button" className="font-bold" onClick={handleNotificationsSubmit}>Guardar Preferencias</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security">
          <Card className="neo-shadow border-primary/20">
            <CardHeader>
              <CardTitle>Seguridad de la Cuenta</CardTitle>
              <CardDescription>
                Gestiona tu contraseña y protege tu cuenta.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSecuritySubmit} className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Contraseña Actual</label>
                    <Input 
                      type="password" 
                      value={securityForm.currentPassword}
                      onChange={(e) => setSecurityForm(prev => ({...prev, currentPassword: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Nueva Contraseña</label>
                    <Input 
                      type="password" 
                      value={securityForm.newPassword}
                      onChange={(e) => setSecurityForm(prev => ({...prev, newPassword: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Confirmar Nueva Contraseña</label>
                    <Input 
                      type="password" 
                      value={securityForm.confirmPassword}
                      onChange={(e) => setSecurityForm(prev => ({...prev, confirmPassword: e.target.value}))}
                    />
                  </div>
                </div>
                <div className="flex justify-end pt-4 border-t gap-4">
                  <Button type="button" variant="ghost" onClick={() => setSecurityForm({currentPassword: "", newPassword: "", confirmPassword: ""})}>Cancelar</Button>
                  <Button type="submit" className="font-bold">Actualizar Contraseña</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance">
          <Card className="neo-shadow border-primary/20">
            <CardHeader>
              <CardTitle>Apariencia</CardTitle>
              <CardDescription>
                Personaliza cómo se ve el dashboard.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-1 p-4 border-2 border-primary rounded-xl cursor-pointer bg-background hover:bg-muted/50 transition-colors">
                  <div className="w-full h-24 bg-slate-950 rounded-md mb-2 p-2 flex flex-col gap-2">
                    <div className="w-1/2 h-2 bg-slate-800 rounded-full" />
                    <div className="w-full h-full bg-slate-900 rounded border border-slate-800" />
                  </div>
                  <p className="text-center font-bold text-sm">Tema Oscuro</p>
                  <p className="text-center text-xs text-muted-foreground mt-1">Modo hacker (Activo)</p>
                </div>
                <div className="flex-1 p-4 border-2 border-transparent rounded-xl cursor-pointer bg-background hover:bg-muted/50 transition-colors opacity-50 grayscale">
                  <div className="w-full h-24 bg-white rounded-md mb-2 p-2 flex flex-col gap-2 shadow-inner border">
                    <div className="w-1/2 h-2 bg-slate-200 rounded-full" />
                    <div className="w-full h-full bg-slate-50 rounded border border-slate-200" />
                  </div>
                  <p className="text-center font-bold text-sm">Tema Claro</p>
                  <p className="text-center text-xs text-muted-foreground mt-1">Muy brillante (Próximamente)</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Selector de Avatar */}
      <Dialog open={isAvatarModalOpen} onOpenChange={setIsAvatarModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Elige tu Avatar</DialogTitle>
            <DialogDescription>
              Selecciona tu robot favorito para representarte en RoboLearn.
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-4 gap-4 py-4">
            {PREDEFINED_AVATARS.map((url, idx) => (
              <div 
                key={idx} 
                onClick={() => handleAvatarSelect(url)}
                className={`relative cursor-pointer rounded-lg p-2 border-2 transition-all hover:scale-105 ${selectedAvatar === url ? 'border-primary bg-primary/10' : 'border-transparent bg-secondary'}`}
              >
                <img src={url} alt={`Avatar ${idx}`} className="w-full h-auto aspect-square object-contain" />
                {selectedAvatar === url && (
                  <div className="absolute -top-2 -right-2 bg-primary text-primary-foreground rounded-full p-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-end pt-2">
            <Button variant="ghost" onClick={() => setIsAvatarModalOpen(false)}>Cerrar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
