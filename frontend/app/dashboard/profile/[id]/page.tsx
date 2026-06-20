"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Loader2, Copy, Check, Trophy, BookOpen, Star, Flame, GraduationCap, Presentation, Target } from "lucide-react"
import { toast } from "sonner"
import Link from "next/link"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ProfileData {
  full_name: string
  email: string
  bio: string
  avatar_url: string
  role: string
  points: number
  streak_days: number
  achievements: { id: number; name: string; icon: string }[]
  classes: { id: number; title: string; progress?: number; module_count?: number; student_count?: number }[]
}

export default function ProfilePage() {
  const params = useParams()
  const router = useRouter()
  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true)
      let identifier = (params.id as string).trim()

      const numericId = parseInt(identifier, 10)

      // Try as public_id (UUID) first
      if (!isNaN(numericId) || identifier.includes("-")) {
        try {
          const endpoint = identifier.includes("-")
            ? `${API_URL}/users/by-public-id/${identifier}`
            : `${API_URL}/users/${numericId}`
          const res = await fetch(endpoint, { credentials: "include" })
          const data = await res.json()
          if (data.success) {
            const u = data.user
            let achievements: any[] = []
            try {
              const achRes = await fetch(`${API_URL}/achievements?user_id=${u.id}`, { credentials: "include" })
              const achData = await achRes.json()
              if (achData.success) {
                achievements = (achData.achievements || [])
                  .filter((a: any) => !a.is_locked)
                  .map((a: any) => ({ id: a.id, name: a.name, icon: a.icon }))
              }
            } catch (_) {}

            let profileClasses: any[] = []
            try {
              const clsRes = await fetch(`${API_URL}/users/${u.id}/classes`, { credentials: "include" })
              const clsData = await clsRes.json()
              if (clsData.success) {
                profileClasses = (clsData.classes || []).map((c: any) => ({
                  id: c.id,
                  title: c.title,
                  progress: c.progress || 0,
                  module_count: c.module_count || 0,
                  student_count: c.student_count || 0,
                }))
              }
            } catch (_) {}

            setProfile({
              full_name: u.full_name,
              email: u.email,
              bio: u.bio || "",
              avatar_url: u.avatar_url || `https://api.dicebear.com/7.x/bottts/svg?seed=${u.full_name}`,
              role: u.role,
              points: u.points || 0,
              streak_days: u.streak_days || 0,
              achievements,
              classes: profileClasses
            })
            setLoading(false)
            return
          }
        } catch (_) {}
      }

      // Fallback: try searching by name
      try {
        const res = await fetch(`${API_URL}/users/search?q=${encodeURIComponent(identifier)}`, { credentials: "include" })
        const data = await res.json()
        if (data.success && data.users.length > 0) {
          const found = data.users[0]
          if (found.public_id) {
            router.replace(`/dashboard/profile/${found.public_id}`)
          } else {
            router.replace(`/dashboard/profile/${found.id}`)
          }
          return
        }
      } catch (_) {}
      setLoading(false)
    }
    fetchProfile()
  }, [params.id, router])

  const copyProfileLink = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    toast.success("Enlace del perfil copiado al portapapeles")
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (!profile) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <p className="text-muted-foreground">Usuario no encontrado</p>
        <Button variant="outline" onClick={() => window.history.back()}>Volver</Button>
      </div>
    )
  }

  const initials = profile.full_name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)
  const isStudent = profile.role === "student"
  const isTeacher = profile.role === "teacher"

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-10">

      {/* Header Section */}
      <Card className="border-primary/20">
        <CardContent className="p-6 md:p-8">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
            <Avatar className="w-24 h-24 md:w-32 md:h-32 border-4 border-background shadow-lg">
              <AvatarImage src={profile.avatar_url} />
              <AvatarFallback className="text-2xl">{initials}</AvatarFallback>
            </Avatar>
            <div className="flex-1 text-center md:text-left space-y-3">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">{profile.full_name}</h1>
                <Badge variant="secondary" className="mt-1">
                  {isTeacher ? "Docente" : isStudent ? "Estudiante" : "Administrador"}
                </Badge>
              </div>
              <div className="flex items-center justify-center md:justify-start gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-yellow-500" />
                  <span className="font-medium">{profile.points} pts</span>
                </div>
                <div className="flex items-center gap-1">
                  <Flame className="w-4 h-4 text-orange-500" />
                  <span className="font-medium">{profile.streak_days} días</span>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={copyProfileLink}>
                {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
                {copied ? "Copiado" : "Copiar enlace del perfil"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Presentation / Bio Section */}
      <Card className="border-primary/10">
        <CardContent className="p-6">
          {isStudent && (
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <Target className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Sobre mí</h3>
                <p className="text-muted-foreground">
                  {profile.bio || `Estudiante apasionado por la programación. Actualmente con ${profile.points} puntos y una racha de ${profile.streak_days} días.`}
                </p>
              </div>
            </div>
          )}
          {isTeacher && profile.bio && (
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <Presentation className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-1">Biografía</h3>
                <p className="text-muted-foreground whitespace-pre-wrap">{profile.bio}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Student: Active Courses */}
      {isStudent && profile.classes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-primary" />
              Cursos Activos
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {profile.classes.map((cls) => (
              <div key={cls.id} className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                   onClick={() => router.push(`/dashboard/classes/${cls.id}`)}>
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-green-500/10 text-green-500">
                    <GraduationCap className="w-5 h-5" />
                  </div>
                  <span className="font-medium">{cls.title}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground">{cls.progress}%</span>
                  <Progress value={cls.progress} className="w-20 h-2" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Teacher: Courses they teach */}
      {isTeacher && profile.classes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-primary" />
              Clases que Imparte
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.classes.map((cls) => (
              <div key={cls.id} className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-3">
                  <BookOpen className="w-5 h-5 text-primary shrink-0" />
                  <span className="font-medium">{cls.title}</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  {(cls.module_count ?? 0) > 0 && <span>{cls.module_count ?? 0} módulos</span>}
                  {(cls.student_count ?? 0) > 0 && <span>{cls.student_count ?? 0} estudiantes</span>}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Achievements (only for students) */}
      {isStudent && profile.achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              Logros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {profile.achievements.map((a) => (
                <div key={a.id} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-muted border border-yellow-500/20">
                  <span className="text-lg">{a.icon}</span>
                  <span className="text-sm font-medium">{a.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
