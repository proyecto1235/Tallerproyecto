"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import type { User } from "@/hooks/use-auth"
import {
  BookOpen,
  Trophy,
  Flame,
  Star,
  Target,
  ArrowRight,
  CheckCircle,
  Clock,
  Zap,
} from "lucide-react"
import Link from "next/link"
import { InteractiveExercise } from "@/components/interactive/InteractiveExercise"

interface StudentDashboardProps {
  user: User
}

export function StudentDashboard({ user }: StudentDashboardProps) {
  // Mock data for demonstration
  const progress = {
    completedLessons: 8,
    totalLessons: 24,
    currentModule: "Variables y Tipos de Datos",
    nextLesson: "Numeros enteros y decimales",
  }

  const weeklyChallenge = {
    title: "Maestro de Variables",
    description: "Completa 5 ejercicios de variables",
    progress: 3,
    total: 5,
    reward: 50,
    endsIn: "3 dias",
  }

  const recentAchievements = [
    { name: "Primer Paso", icon: "footprints", earnedAt: "Hace 2 dias" },
    { name: "Racha de 7 dias", icon: "flame", earnedAt: "Ayer" },
  ]

  const recommendations = [
    { type: "lesson", title: "Continua con: Numeros enteros", module: "Variables" },
    { type: "exercise", title: "Practica: Crear variables", difficulty: "Facil" },
    { type: "challenge", title: "Reto: Maestro de Variables", reward: "50 pts" },
  ]

  const progressPercent = Math.round((progress.completedLessons / progress.totalLessons) * 100)

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground md:text-3xl">
            Hola, {user.fullName.split(" ")[0]}!
          </h1>
          <p className="text-muted-foreground">Continua tu aventura de aprendizaje</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 rounded-lg bg-yellow-500/10 px-3 py-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <span className="font-semibold text-yellow-600">{user.points} pts</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg bg-orange-500/10 px-3 py-2">
            <Flame className="h-5 w-5 text-orange-500" />
            <span className="font-semibold text-orange-600">{user.streakDays} dias</span>
          </div>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <BookOpen className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Lecciones</p>
              <p className="text-2xl font-bold text-foreground">
                {progress.completedLessons}/{progress.totalLessons}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <CheckCircle className="h-6 w-6 text-accent" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Ejercicios</p>
              <p className="text-2xl font-bold text-foreground">23</p>
            </div>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-500/10">
              <Trophy className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Logros</p>
              <p className="text-2xl font-bold text-foreground">5</p>
            </div>
          </CardContent>
        </Card>
        <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <Target className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Retos</p>
              <p className="text-2xl font-bold text-foreground">2</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Interactive Code Editor Demo */}
      <div className="py-4">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-primary" />
          Desafío Rápido: ¡Haz saltar al robot!
        </h2>
        <InteractiveExercise />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main progress */}
        <div className="lg:col-span-2 space-y-6">
          {/* Current progress card */}
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                Tu progreso
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Progreso general</span>
                  <span className="font-medium text-foreground">{progressPercent}%</span>
                </div>
                <Progress value={progressPercent} className="h-3" />
              </div>
              <div className="rounded-lg border bg-muted/30 p-4">
                <p className="text-sm text-muted-foreground">Modulo actual</p>
                <p className="text-lg font-semibold text-foreground">{progress.currentModule}</p>
                <p className="mt-2 text-sm text-muted-foreground">
                  Siguiente leccion: {progress.nextLesson}
                </p>
                <Button className="mt-4" asChild>
                  <Link href="/dashboard/modules">
                    Continuar aprendiendo
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Weekly challenge */}
          <Card className="neo-shadow-primary border-primary bg-primary/10 backdrop-blur">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-primary" />
                Reto Semanal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-1">
                  <h3 className="font-semibold text-foreground">{weeklyChallenge.title}</h3>
                  <p className="text-sm text-muted-foreground">{weeklyChallenge.description}</p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    Termina en {weeklyChallenge.endsIn}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-primary">
                      {weeklyChallenge.progress}/{weeklyChallenge.total}
                    </p>
                    <p className="text-xs text-muted-foreground">completados</p>
                  </div>
                  <div className="text-center rounded-lg bg-yellow-500/10 px-3 py-2">
                    <p className="text-lg font-bold text-yellow-600">+{weeklyChallenge.reward}</p>
                    <p className="text-xs text-muted-foreground">puntos</p>
                  </div>
                </div>
              </div>
              <Progress
                value={(weeklyChallenge.progress / weeklyChallenge.total) * 100}
                className="mt-4 h-2"
              />
            </CardContent>
          </Card>
        </div>

        {/* Sidebar content */}
        <div className="space-y-6">
          {/* Recommendations */}
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-base">Recomendaciones</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/50"
                >
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                      rec.type === "lesson"
                        ? "bg-primary/10 text-primary"
                        : rec.type === "exercise"
                          ? "bg-accent/10 text-accent"
                          : "bg-yellow-500/10 text-yellow-600"
                    }`}
                  >
                    {rec.type === "lesson" ? (
                      <BookOpen className="h-4 w-4" />
                    ) : rec.type === "exercise" ? (
                      <Zap className="h-4 w-4" />
                    ) : (
                      <Trophy className="h-4 w-4" />
                    )}
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <p className="truncate text-sm font-medium text-foreground">{rec.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {rec.type === "lesson" ? rec.module : rec.type === "exercise" ? rec.difficulty : rec.reward}
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Recent achievements */}
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-base">Logros Recientes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentAchievements.map((achievement, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500/10">
                    <Star className="h-5 w-5 text-yellow-500" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">{achievement.name}</p>
                    <p className="text-xs text-muted-foreground">{achievement.earnedAt}</p>
                  </div>
                </div>
              ))}
              <Button variant="ghost" size="sm" className="w-full" asChild>
                <Link href="/dashboard/achievements">Ver todos los logros</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
