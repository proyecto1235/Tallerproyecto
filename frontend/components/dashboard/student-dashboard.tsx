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
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"

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
    { type: "lesson", title: "Continua con: Numeros enteros", module: "Variables", link: "/dashboard/modules" },
    { type: "exercise", title: "Practica: Crear variables", difficulty: "Facil", link: "/dashboard/exercises" },
    { type: "challenge", title: "Reto: Maestro de Variables", reward: "50 pts", link: "/dashboard/challenges" },
  ]

  const weeklyActivityData = [
    { day: "Lun", puntos: 120 },
    { day: "Mar", puntos: 250 },
    { day: "Mié", puntos: 180 },
    { day: "Jue", puntos: 300 },
    { day: "Vie", puntos: 210 },
    { day: "Sáb", puntos: 400 },
    { day: "Dom", puntos: 150 },
  ]

  const skillsData = [
    { name: "Lógica", value: 45, color: "#8b5cf6" }, // purple
    { name: "Sintaxis", value: 25, color: "#3b82f6" }, // blue
    { name: "Creatividad", value: 30, color: "#10b981" }, // green
  ]

  const recentActivityFeed = [
    { type: "exercise", title: "Bucle For completado", time: "Hace 2 horas", points: 15 },
    { type: "module", title: "Variables nivel 1 iniciado", time: "Hace 5 horas", points: 0 },
    { type: "achievement", title: "¡Racha de 3 días!", time: "Ayer", points: 50 },
  ]

  const progressPercent = Math.round((progress.completedLessons / progress.totalLessons) * 100)

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground md:text-3xl">
            Hola, {(user?.fullName || "Usuario").split(" ")[0]}!
          </h1>
          <p className="text-muted-foreground">Continua tu aventura de aprendizaje</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 rounded-lg bg-yellow-500/10 px-3 py-2">
            <Star className="h-5 w-5 text-yellow-500" />
            <span className="font-semibold text-yellow-600">{user?.points || 0} pts</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg bg-orange-500/10 px-3 py-2">
            <Flame className="h-5 w-5 text-orange-500" />
            <span className="font-semibold text-orange-600">{user?.streakDays || 0} dias</span>
          </div>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link href="/dashboard/modules" className="block">
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur hover:border-primary/50 transition-colors cursor-pointer h-full">
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
        </Link>
        
        <Link href="/dashboard/exercises" className="block">
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur hover:border-accent/50 transition-colors cursor-pointer h-full">
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
        </Link>

        <Link href="/dashboard/achievements" className="block">
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur hover:border-yellow-500/50 transition-colors cursor-pointer h-full">
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
        </Link>

        <Link href="/dashboard/challenges" className="block">
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur hover:border-blue-500/50 transition-colors cursor-pointer h-full">
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
        </Link>
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
          {/* Main Progress and Charts Area */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Zap className="h-5 w-5 text-primary" />
                  Progreso Actual
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progreso general</span>
                    <span className="font-medium text-foreground">{progressPercent}%</span>
                  </div>
                  <Progress value={progressPercent} className="h-4 rounded-full bg-primary/20" />
                </div>
                <div className="rounded-xl border bg-muted/30 p-5">
                  <p className="text-sm font-bold text-primary mb-1">MÓDULO ACTUAL</p>
                  <p className="text-xl font-bold text-foreground mb-2">{progress.currentModule}</p>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                    <BookOpen className="h-4 w-4" />
                    Siguiente: {progress.nextLesson}
                  </div>
                  <Button className="w-full font-bold shadow-md hover:shadow-lg transition-all" asChild>
                    <Link href="/dashboard/modules">
                      Continuar Aprendiendo
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Target className="h-5 w-5 text-accent" />
                  Habilidades
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center">
                <div className="h-[180px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={skillsData}
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {skillsData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-center gap-4 mt-2 w-full">
                  {skillsData.map((skill) => (
                    <div key={skill.name} className="flex items-center gap-1.5">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: skill.color }} />
                      <span className="text-xs font-medium">{skill.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Activity Chart */}
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Flame className="h-5 w-5 text-orange-500" />
                Actividad Semanal (Puntos)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[250px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyActivityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted-foreground)/0.2)" />
                    <XAxis 
                      dataKey="day" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} 
                      dy={10}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                    />
                    <RechartsTooltip 
                      cursor={{ fill: 'hsl(var(--muted)/0.4)' }}
                      contentStyle={{ borderRadius: '8px', border: 'none', backgroundColor: 'hsl(var(--card))', color: 'hsl(var(--foreground))', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Bar 
                      dataKey="puntos" 
                      radius={[4, 4, 0, 0]} 
                      fill="hsl(var(--primary))" 
                      barSize={32}
                    >
                      {weeklyActivityData.map((entry, index) => {
                        const colors = ["#10b981", "#3b82f6", "#8b5cf6", "#10b981", "#3b82f6", "#8b5cf6", "#10b981"]
                        return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                      })}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
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
                <Link
                  key={index}
                  href={rec.link}
                  className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/50 group cursor-pointer"
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
                    <p className="truncate text-sm font-medium text-foreground group-hover:text-primary transition-colors">{rec.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {rec.type === "lesson" ? rec.module : rec.type === "exercise" ? rec.difficulty : rec.reward}
                    </p>
                  </div>
                </Link>
              ))}
            </CardContent>
          </Card>

          {/* Activity Feed */}
          <Card className="neo-shadow border-primary/20 bg-card/80 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-5 w-5 text-muted-foreground" />
                Actividad Reciente
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivityFeed.map((activity, i) => (
                  <div key={i} className="flex gap-3 relative">
                    {/* Line connection */}
                    {i !== recentActivityFeed.length - 1 && (
                      <div className="absolute left-[15px] top-8 bottom-[-16px] w-[2px] bg-border" />
                    )}
                    <div className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-background ${
                      activity.type === 'exercise' ? 'bg-blue-500 text-white' :
                      activity.type === 'achievement' ? 'bg-yellow-500 text-white' :
                      'bg-green-500 text-white'
                    }`}>
                      {activity.type === 'exercise' ? <Zap className="h-4 w-4" /> :
                       activity.type === 'achievement' ? <Trophy className="h-4 w-4" /> :
                       <BookOpen className="h-4 w-4" />}
                    </div>
                    <div className="flex flex-col pb-2">
                      <span className="text-sm font-semibold leading-none">{activity.title}</span>
                      <span className="text-xs text-muted-foreground mt-1">{activity.time}</span>
                      {activity.points > 0 && (
                        <span className="text-xs font-bold text-yellow-600 mt-1 flex items-center gap-1">
                          <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                          +{activity.points} pts
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
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
