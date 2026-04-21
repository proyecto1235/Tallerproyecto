"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import {
  Star,
  Trophy,
  Flame,
  BookOpen,
  Code,
  Users,
  Zap,
  Award,
  Crown,
  Target,
  Compass,
  CheckCircle,
} from "lucide-react"

const achievements = [
  {
    id: 1,
    name: "Primer Paso",
    description: "Completa tu primera leccion",
    icon: Target,
    points: 10,
    earned: true,
    earnedAt: "15 Ene 2024",
  },
  {
    id: 2,
    name: "Explorador",
    description: "Completa 5 lecciones",
    icon: Compass,
    points: 25,
    earned: true,
    earnedAt: "20 Ene 2024",
  },
  {
    id: 3,
    name: "Estudiante Dedicado",
    description: "Completa 20 lecciones",
    icon: BookOpen,
    points: 50,
    earned: false,
    progress: { current: 8, total: 20 },
  },
  {
    id: 4,
    name: "Racha de 7 dias",
    description: "Manten una racha de 7 dias",
    icon: Flame,
    points: 30,
    earned: true,
    earnedAt: "22 Ene 2024",
  },
  {
    id: 5,
    name: "Racha de 30 dias",
    description: "Manten una racha de 30 dias",
    icon: Flame,
    points: 100,
    earned: false,
    progress: { current: 12, total: 30 },
  },
  {
    id: 6,
    name: "Primer Ejercicio",
    description: "Resuelve tu primer ejercicio correctamente",
    icon: CheckCircle,
    points: 10,
    earned: true,
    earnedAt: "16 Ene 2024",
  },
  {
    id: 7,
    name: "Solucionador",
    description: "Resuelve 10 ejercicios correctamente",
    icon: Zap,
    points: 30,
    earned: true,
    earnedAt: "25 Ene 2024",
  },
  {
    id: 8,
    name: "Experto",
    description: "Resuelve 50 ejercicios correctamente",
    icon: Award,
    points: 75,
    earned: false,
    progress: { current: 23, total: 50 },
  },
  {
    id: 9,
    name: "Retador",
    description: "Completa tu primer reto semanal",
    icon: Trophy,
    points: 50,
    earned: false,
    progress: { current: 3, total: 5 },
  },
  {
    id: 10,
    name: "Campeon",
    description: "Gana 5 retos semanales",
    icon: Crown,
    points: 150,
    earned: false,
    progress: { current: 0, total: 5 },
  },
  {
    id: 11,
    name: "Colaborador",
    description: "Unete a tu primera clase",
    icon: Users,
    points: 15,
    earned: false,
  },
  {
    id: 12,
    name: "Principiante Python",
    description: "Completa el modulo de introduccion a Python",
    icon: Code,
    points: 40,
    earned: true,
    earnedAt: "18 Ene 2024",
  },
]

export default function AchievementsPage() {
  const earnedAchievements = achievements.filter((a) => a.earned)
  const totalPoints = earnedAchievements.reduce((sum, a) => sum + a.points, 0)
  const totalPossiblePoints = achievements.reduce((sum, a) => sum + a.points, 0)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">Logros</h1>
        <p className="text-muted-foreground">Desbloquea logros y gana recompensas</p>
      </div>

      {/* Summary */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-500/10">
              <Trophy className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Logros Obtenidos</p>
              <p className="text-2xl font-bold text-foreground">
                {earnedAchievements.length}/{achievements.length}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Star className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Puntos por Logros</p>
              <p className="text-2xl font-bold text-foreground">{totalPoints}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Progreso Total</p>
            <div className="mt-2 flex items-center gap-2">
              <Progress value={(totalPoints / totalPossiblePoints) * 100} className="h-3 flex-1" />
              <span className="text-sm font-medium text-foreground">
                {Math.round((totalPoints / totalPossiblePoints) * 100)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Earned achievements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            Logros Obtenidos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {earnedAchievements.map((achievement) => {
              const Icon = achievement.icon
              return (
                <div
                  key={achievement.id}
                  className="flex items-center gap-3 rounded-lg border bg-yellow-500/5 p-4"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-yellow-500/10">
                    <Icon className="h-6 w-6 text-yellow-500" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-foreground">{achievement.name}</p>
                    <p className="text-xs text-muted-foreground">{achievement.earnedAt}</p>
                    <p className="text-xs font-medium text-yellow-600">+{achievement.points} pts</p>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Locked achievements */}
      <Card>
        <CardHeader>
          <CardTitle>Logros por Desbloquear</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {achievements
              .filter((a) => !a.earned)
              .map((achievement) => {
                const Icon = achievement.icon
                const hasProgress = achievement.progress
                const progressPercent = hasProgress
                  ? (achievement.progress!.current / achievement.progress!.total) * 100
                  : 0

                return (
                  <div
                    key={achievement.id}
                    className="flex flex-col gap-3 rounded-lg border p-4 opacity-75"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
                        <Icon className="h-6 w-6 text-muted-foreground" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-foreground">{achievement.name}</p>
                        <p className="text-xs text-muted-foreground">{achievement.description}</p>
                      </div>
                    </div>
                    {hasProgress && (
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground">
                            {achievement.progress!.current}/{achievement.progress!.total}
                          </span>
                          <span className="font-medium text-primary">+{achievement.points} pts</span>
                        </div>
                        <Progress value={progressPercent} className="h-2" />
                      </div>
                    )}
                    {!hasProgress && (
                      <p className="text-xs font-medium text-muted-foreground">
                        Recompensa: +{achievement.points} pts
                      </p>
                    )}
                  </div>
                )
              })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
