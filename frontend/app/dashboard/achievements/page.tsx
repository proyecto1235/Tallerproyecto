"use client"

import { useState, useEffect } from "react"
import { AchievementBadge, AchievementBadgeProps } from "@/components/dashboard/achievement-badge"
import { Trophy, Star, Shield, Flame, TrendingUp, Medal, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"

const iconMap: Record<string, "trophy" | "star" | "shield" | "medal" | "zap" | "award" | "target" | "flame"> = {
  trophy: "trophy", star: "star", shield: "shield", medal: "medal",
  zap: "zap", award: "award", target: "target", flame: "flame"
}

export default function AchievementsPage() {
  const [filter, setFilter] = useState<"all" | "unlocked" | "locked">("all")
  const [achievements, setAchievements] = useState<AchievementBadgeProps[]>([])
  const [loading, setLoading] = useState(true)
  const [userPoints, setUserPoints] = useState(0)
  const [streakDays, setStreakDays] = useState(0)

  useEffect(() => {
    const fetchAchievements = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/achievements", { credentials: 'include' })
        const data = await res.json()
        if (data.success) {
          const mapped: AchievementBadgeProps[] = data.achievements.map((a: any) => ({
            id: a.id.toString(),
            title: a.name,
            description: a.description,
            icon: iconMap[a.icon] || "medal",
            date: a.earned_at ? new Date(a.earned_at).toLocaleDateString() : undefined,
            isLocked: a.is_locked,
            rarity: a.points >= 80 ? "legendary" : a.points >= 50 ? "epic" : a.points >= 30 ? "rare" : "common"
          }))
          setAchievements(mapped)
        }
      } catch (_) {
        // Fallback
      }
      setLoading(false)
    }
    
    const fetchUser = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/users/profile", { credentials: 'include' })
        const data = await res.json()
        if (data.success) {
          setUserPoints(data.user.points || 0)
          setStreakDays(data.user.streak_days || 0)
        }
      } catch (_) {}
    }
    
    fetchAchievements()
    fetchUser()
  }, [])

  const unlocked = achievements.filter(a => !a.isLocked).length
  const total = achievements.length

  const filteredAchievements = achievements.filter(a => {
    if (filter === "unlocked") return !a.isLocked
    if (filter === "locked") return a.isLocked
    return true
  })

  const nextLevelXP = 3000
  const progressPercent = Math.min((userPoints / nextLevelXP) * 100, 100)

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  return (
    <div className="space-y-10 max-w-6xl mx-auto pb-10">
      <div className="bg-card border rounded-3xl p-8 neo-shadow relative overflow-hidden flex flex-col md:flex-row gap-8 items-center justify-between">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />

        <div className="flex items-center gap-6 z-10">
          <div className="relative">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg border-4 border-background">
              <span className="text-4xl font-black text-white">{Math.floor(userPoints / 500) + 1}</span>
            </div>
            <div className="absolute -bottom-2 -translate-x-1/2 left-1/2 bg-background border px-3 py-1 rounded-full text-xs font-bold shadow-sm whitespace-nowrap">
              Nivel de Coder
            </div>
          </div>

          <div>
            <h1 className="text-3xl font-bold tracking-tight">Sala de Trofeos</h1>
            <p className="text-muted-foreground mt-1">Sigue aprendiendo para subir de nivel y ganar más recompensas.</p>
          </div>
        </div>

        <div className="w-full md:w-1/3 z-10 bg-background/50 p-4 rounded-xl border backdrop-blur-sm">
          <div className="flex justify-between text-sm font-bold mb-2">
            <span>XP Actual</span>
            <span className="text-primary">{userPoints} / {nextLevelXP} XP</span>
          </div>
          <Progress value={progressPercent} className="h-3" />
          <p className="text-xs text-muted-foreground text-center mt-3">
            {nextLevelXP - userPoints > 0 ? `¡Solo ${nextLevelXP - userPoints} XP para el siguiente nivel!` : "¡Nivel máximo alcanzado!"}
          </p>
        </div>
      </div>

      <div className="grid gap-6 grid-cols-2 md:grid-cols-4">
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-yellow-500/10 rounded-full text-yellow-500"><Trophy className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Logros</p>
          <p className="text-2xl font-black">{unlocked}/{total}</p>
        </div>
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-orange-500/10 rounded-full text-orange-500"><Flame className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Racha Actual</p>
          <p className="text-2xl font-black">{streakDays} Días</p>
        </div>
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-green-500/10 rounded-full text-green-500"><Star className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Puntos Totales</p>
          <p className="text-2xl font-black">{userPoints.toLocaleString()}</p>
        </div>
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-blue-500/10 rounded-full text-blue-500"><TrendingUp className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Tasa de Logros</p>
          <p className="text-2xl font-black">{total > 0 ? Math.round((unlocked / total) * 100) : 0}%</p>
        </div>
      </div>

      <section>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 border-b pb-4 gap-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Medal className="w-6 h-6 text-primary" />
            Tus Insignias
          </h2>
          <div className="flex items-center gap-2">
            <Button
              variant={filter === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("all")}
              className="rounded-full"
            >Todas</Button>
            <Button
              variant={filter === "unlocked" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("unlocked")}
              className="rounded-full"
            >Desbloqueadas</Button>
            <Button
              variant={filter === "locked" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter("locked")}
              className="rounded-full"
            >Bloqueadas</Button>
          </div>
        </div>

        {achievements.length === 0 ? (
          <p className="text-center text-muted-foreground py-10">No hay logros disponibles. ¡Completa módulos y ejercicios para ganarlos!</p>
        ) : (
          <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {filteredAchievements.map(a => <AchievementBadge key={a.id} {...a} />)}
          </div>
        )}
      </section>
    </div>
  )
}