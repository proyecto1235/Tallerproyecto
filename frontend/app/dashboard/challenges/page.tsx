"use client"

import { useState, useEffect } from "react"
import { ChallengeCard, ChallengeCardProps } from "@/components/dashboard/challenge-card"
import { Target, Zap, Flame, Trophy, Loader2 } from "lucide-react"
import { toast } from "sonner"

export default function ChallengesPage() {
  const [userStars, setUserStars] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [challenges, setChallenges] = useState<ChallengeCardProps[]>([])
  useEffect(() => {
    const fetchChallenges = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/challenges", {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          const mapped = data.challenges.map((c: any) => ({
            id: c.id.toString(),
            title: c.title,
            description: c.description,
            difficulty: c.difficulty === 1 ? "Fácil" : c.difficulty === 2 ? "Medio" : "Difícil",
            reward: c.points,
            status: "active",
            type: "daily",
            timeRemaining: `Autor: ${c.author_name}`
          }))
          setChallenges(mapped)
        }
      } catch (error) {
        console.error("Error fetching challenges", error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchChallenges()
  }, [])

  const handleTryChallenge = (id: string) => {
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

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
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
          Retos Disponibles
        </h2>
        {challenges.length === 0 ? (
          <p className="text-muted-foreground text-center py-10">No hay retos disponibles en este momento.</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {challenges.map(c => <ChallengeCard key={c.id} {...c} onClick={() => handleTryChallenge(c.id)} />)}
          </div>
        )}
      </section>
    </div>
  )
}
