"use client"

import { useState } from "react"
import { ChallengeCard, ChallengeCardProps } from "@/components/dashboard/challenge-card"
import { Target, Zap, Flame, Trophy } from "lucide-react"
import { toast } from "sonner"

export default function ChallengesPage() {
  const [userStars, setUserStars] = useState(1240)
  
  const [dailyChallenges, setDailyChallenges] = useState<ChallengeCardProps[]>([
    {
      id: "c1",
      title: "Cazador de Errores",
      description: "Encuentra y corrige 3 errores de sintaxis en el código de prueba.",
      difficulty: "Fácil",
      reward: 10,
      status: "active",
      type: "daily",
      timeRemaining: "14h 23m"
    },
    {
      id: "c2",
      title: "Velocista de Variables",
      description: "Crea 5 variables de diferentes tipos en menos de 2 minutos.",
      difficulty: "Medio",
      reward: 20,
      status: "completed",
      type: "daily"
    }
  ])

  const [weeklyChallenges, setWeeklyChallenges] = useState<ChallengeCardProps[]>([
    {
      id: "cw1",
      title: "Maestro del Bucle",
      description: "Usa un bucle For para imprimir los números pares del 1 al 100.",
      difficulty: "Medio",
      reward: 50,
      status: "active",
      type: "weekly",
      timeRemaining: "3 días"
    },
    {
      id: "cw2",
      title: "Calculadora Básica",
      description: "Crea un programa que sume, reste, multiplique y divida dos números introducidos por el usuario.",
      difficulty: "Difícil",
      reward: 100,
      status: "active",
      type: "weekly",
      timeRemaining: "5 días"
    }
  ])

  const [specialChallenges, setSpecialChallenges] = useState<ChallengeCardProps[]>([
    {
      id: "cs1",
      title: "Desafío del Jefe: El Laberinto",
      description: "Escribe las instrucciones condicionales exactas para que el robot salga del laberinto sin chocar.",
      difficulty: "Jefe Final",
      reward: 500,
      status: "active",
      type: "special",
      timeRemaining: "Evento Especial"
    }
  ])

  const handleTryChallenge = (id: string, type: "daily" | "weekly" | "special") => {
    // Determine which setter to use
    const setChallenges = type === "daily" ? setDailyChallenges : type === "weekly" ? setWeeklyChallenges : setSpecialChallenges
    
    // Set to running
    setChallenges(prev => prev.map(c => c.id === id ? { ...c, status: "running" } : c))
    toast.info("Iniciando entorno del reto...")

    // Simulate completion after delay
    setTimeout(() => {
      setChallenges(prev => prev.map(c => {
        if (c.id === id) {
          setUserStars(stars => stars + c.reward)
          toast.success(`¡Reto completado! Has ganado ${c.reward} estrellas.`)
          return { ...c, status: "completed" }
        }
        return c
      }))
    }, 2000)
  }

  return (
    <div className="space-y-10 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-primary/5 p-6 rounded-2xl border border-primary/20">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center gap-3">
            <Target className="w-8 h-8 text-primary" />
            Centro de Retos
          </h1>
          <p className="text-muted-foreground mt-2 max-w-xl">
            Pon a prueba tus habilidades de programación con desafíos contrarreloj. 
            ¡Gana estrellas extra y sube en la clasificación global!
          </p>
        </div>
        <div className="flex items-center gap-4 bg-card p-4 rounded-xl border neo-shadow">
          <div className="text-center">
            <p className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Tus Estrellas</p>
            <p className="text-3xl font-black text-yellow-500">{userStars.toLocaleString()}</p>
          </div>
        </div>
      </div>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 border-b pb-2">
          <Zap className="w-6 h-6 text-yellow-500" />
          Retos Diarios
        </h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {dailyChallenges.map(c => <ChallengeCard key={c.id} {...c} onClick={() => handleTryChallenge(c.id, "daily")} />)}
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 border-b pb-2">
          <Flame className="w-6 h-6 text-orange-500" />
          Retos Semanales
        </h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {weeklyChallenges.map(c => <ChallengeCard key={c.id} {...c} onClick={() => handleTryChallenge(c.id, "weekly")} />)}
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 border-b pb-2">
          <Trophy className="w-6 h-6 text-purple-500" />
          Eventos Especiales
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          {specialChallenges.map(c => <ChallengeCard key={c.id} {...c} onClick={() => handleTryChallenge(c.id, "special")} />)}
        </div>
      </section>
    </div>
  )
}
