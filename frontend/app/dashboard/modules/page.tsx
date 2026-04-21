"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import {
  PlayCircle,
  Box,
  GitBranch,
  Repeat,
  Puzzle,
  List,
  Cpu,
  Lock,
  CheckCircle,
  ArrowRight,
} from "lucide-react"
import Link from "next/link"

const modules = [
  {
    id: 1,
    title: "Introduccion a Python",
    description: "Aprende los fundamentos de Python desde cero",
    icon: PlayCircle,
    lessons: 3,
    completedLessons: 3,
    status: "completed",
  },
  {
    id: 2,
    title: "Variables y Tipos de Datos",
    description: "Descubre como almacenar y manipular informacion",
    icon: Box,
    lessons: 3,
    completedLessons: 2,
    status: "in-progress",
  },
  {
    id: 3,
    title: "Estructuras de Control",
    description: "Aprende a tomar decisiones con if, elif y else",
    icon: GitBranch,
    lessons: 2,
    completedLessons: 0,
    status: "locked",
  },
  {
    id: 4,
    title: "Bucles y Repeticiones",
    description: "Domina for y while para repetir acciones",
    icon: Repeat,
    lessons: 2,
    completedLessons: 0,
    status: "locked",
  },
  {
    id: 5,
    title: "Funciones",
    description: "Crea bloques de codigo reutilizables",
    icon: Puzzle,
    lessons: 3,
    completedLessons: 0,
    status: "locked",
  },
  {
    id: 6,
    title: "Listas y Colecciones",
    description: "Organiza datos en estructuras mas complejas",
    icon: List,
    lessons: 3,
    completedLessons: 0,
    status: "locked",
  },
  {
    id: 7,
    title: "Robotica Basica",
    description: "Introduccion a la programacion de robots",
    icon: Cpu,
    lessons: 4,
    completedLessons: 0,
    status: "locked",
  },
]

export default function ModulesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">
          Modulos de Aprendizaje
        </h1>
        <p className="text-muted-foreground">
          Avanza por el arbol de conocimiento a tu propio ritmo
        </p>
      </div>

      {/* Progress overview */}
      <Card>
        <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Progreso total</p>
            <p className="text-2xl font-bold text-foreground">5 de 20 lecciones</p>
          </div>
          <div className="w-full sm:w-64">
            <Progress value={25} className="h-3" />
          </div>
        </CardContent>
      </Card>

      {/* Modules grid */}
      <div className="relative">
        {/* Connection line for desktop */}
        <div className="absolute left-1/2 top-0 hidden h-full w-0.5 -translate-x-1/2 bg-border lg:block" />
        
        <div className="space-y-4">
          {modules.map((module, index) => {
            const Icon = module.icon
            const isCompleted = module.status === "completed"
            const isLocked = module.status === "locked"
            const isInProgress = module.status === "in-progress"
            const progress = Math.round((module.completedLessons / module.lessons) * 100)

            return (
              <div
                key={module.id}
                className={`relative ${index % 2 === 0 ? "lg:pr-[52%]" : "lg:pl-[52%]"}`}
              >
                {/* Connection dot */}
                <div
                  className={`absolute left-1/2 top-6 hidden h-4 w-4 -translate-x-1/2 rounded-full border-4 lg:block ${
                    isCompleted
                      ? "border-accent bg-accent"
                      : isInProgress
                        ? "border-primary bg-primary"
                        : "border-muted bg-muted"
                  }`}
                />

                <Card
                  className={`transition-all ${
                    isLocked
                      ? "opacity-60"
                      : "hover:shadow-md"
                  } ${isInProgress ? "ring-2 ring-primary" : ""}`}
                >
                  <CardContent className="p-4">
                    <div className="flex gap-4">
                      <div
                        className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-xl ${
                          isCompleted
                            ? "bg-accent/10 text-accent"
                            : isInProgress
                              ? "bg-primary/10 text-primary"
                              : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {isLocked ? (
                          <Lock className="h-6 w-6" />
                        ) : isCompleted ? (
                          <CheckCircle className="h-6 w-6" />
                        ) : (
                          <Icon className="h-6 w-6" />
                        )}
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h3 className="font-semibold text-foreground">{module.title}</h3>
                            <p className="text-sm text-muted-foreground">{module.description}</p>
                          </div>
                          {isInProgress && (
                            <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                              En progreso
                            </span>
                          )}
                          {isCompleted && (
                            <span className="shrink-0 rounded-full bg-accent/10 px-2 py-0.5 text-xs font-medium text-accent">
                              Completado
                            </span>
                          )}
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-muted-foreground">
                              {module.completedLessons}/{module.lessons} lecciones
                            </span>
                            {!isLocked && (
                              <Progress value={progress} className="h-2 w-24" />
                            )}
                          </div>
                          {!isLocked && (
                            <Button size="sm" variant={isCompleted ? "outline" : "default"} asChild>
                              <Link href={`/dashboard/modules/${module.id}`}>
                                {isCompleted ? "Repasar" : "Continuar"}
                                <ArrowRight className="ml-1 h-4 w-4" />
                              </Link>
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
