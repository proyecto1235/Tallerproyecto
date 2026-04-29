"use client"

import { useState } from "react"
import { AchievementBadge, AchievementBadgeProps } from "@/components/dashboard/achievement-badge"
import { Trophy, Star, Shield, Flame, TrendingUp, Medal } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"

export default function AchievementsPage() {
  const [filter, setFilter] = useState<"all" | "unlocked" | "locked">("all")
  
  
  const achievements: AchievementBadgeProps[] = [
    {
      id: "a1",
      title: "Primer Código",
      description: "Escribiste tu primera línea de código en Robolearn.",
      icon: "star",
      date: "Hace 1 semana",
      rarity: "common",
      isLocked: false
    },
    {
      id: "a2",
      title: "Racha de 7 días",
      description: "Estudiaste 7 días seguidos sin fallar.",
      icon: "flame",
      date: "Ayer",
      rarity: "epic",
      isLocked: false
    },
    {
      id: "a3",
      title: "Cazador de Bugs",
      description: "Encontraste y corregiste 10 errores en tus ejercicios.",
      icon: "target",
      date: "Hace 3 días",
      rarity: "rare",
      isLocked: false
    },
    {
      id: "a4",
      title: "Cinturón Blanco",
      description: "Completaste el Módulo 1 de Fundamentos.",
      icon: "medal",
      date: "Hace 2 semanas",
      rarity: "common",
      isLocked: false
    },
    {
      id: "a5",
      title: "Experto en Variables",
      description: "Obtuviste puntuación perfecta en todos los ejercicios de variables.",
      icon: "zap",
      rarity: "rare",
      isLocked: true
    },
    {
      id: "a6",
      title: "Maestro del Laberinto",
      description: "Superaste el reto especial del laberinto en tiempo récord.",
      icon: "trophy",
      rarity: "legendary",
      isLocked: true
    },
    {
      id: "a7",
      title: "Defensor del Código",
      description: "Ayudaste a otro estudiante en el foro de dudas.",
      icon: "shield",
      rarity: "rare",
      isLocked: true
    },
    {
      id: "a8",
      title: "Cinturón Amarillo",
      description: "Completaste el Módulo 2 de Variables.",
      icon: "medal",
      rarity: "common",
      isLocked: true
    }
  ]

  const unlocked = achievements.filter(a => !a.isLocked).length
  const total = achievements.length
  
  const filteredAchievements = achievements.filter(a => {
    if (filter === "unlocked") return !a.isLocked
    if (filter === "locked") return a.isLocked
    return true
  })

  // Mock player stats
  const level = 5
  const currentXP = 2450
  const nextLevelXP = 3000
  const progressPercent = (currentXP / nextLevelXP) * 100

  return (
    <div className="space-y-10 max-w-6xl mx-auto pb-10">
      
      {/* Player Card Header */}
      <div className="bg-card border rounded-3xl p-8 neo-shadow relative overflow-hidden flex flex-col md:flex-row gap-8 items-center justify-between">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
        
        <div className="flex items-center gap-6 z-10">
          <div className="relative">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg border-4 border-background">
              <span className="text-4xl font-black text-white">{level}</span>
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
            <span className="text-primary">{currentXP} / {nextLevelXP} XP</span>
          </div>
          <Progress value={progressPercent} className="h-3" />
          <p className="text-xs text-muted-foreground text-center mt-3">
            ¡Solo {nextLevelXP - currentXP} XP para alcanzar el Nivel {level + 1}!
          </p>
        </div>
      </div>

      {/* Stats Summary Row */}
      <div className="grid gap-6 grid-cols-2 md:grid-cols-4">
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-yellow-500/10 rounded-full text-yellow-500"><Trophy className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Logros</p>
          <p className="text-2xl font-black">{unlocked}/{total}</p>
        </div>
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-orange-500/10 rounded-full text-orange-500"><Flame className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Racha Actual</p>
          <p className="text-2xl font-black">7 Días</p>
        </div>
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-green-500/10 rounded-full text-green-500"><Star className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Estrellas Totales</p>
          <p className="text-2xl font-black">1,240</p>
        </div>
        <div className="bg-card border rounded-2xl p-4 flex flex-col items-center justify-center text-center gap-2 neo-shadow">
          <div className="p-3 bg-blue-500/10 rounded-full text-blue-500"><TrendingUp className="w-6 h-6" /></div>
          <p className="text-sm font-bold text-muted-foreground">Posición Global</p>
          <p className="text-2xl font-black">#45</p>
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
            >
              Todas
            </Button>
            <Button 
              variant={filter === "unlocked" ? "default" : "outline"} 
              size="sm" 
              onClick={() => setFilter("unlocked")}
              className="rounded-full"
            >
              Desbloqueadas
            </Button>
            <Button 
              variant={filter === "locked" ? "default" : "outline"} 
              size="sm" 
              onClick={() => setFilter("locked")}
              className="rounded-full"
            >
              Bloqueadas
            </Button>
          </div>
        </div>
        
        <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {filteredAchievements.map(a => <AchievementBadge key={a.id} {...a} />)}
        </div>
      </section>
    </div>
  )
}
