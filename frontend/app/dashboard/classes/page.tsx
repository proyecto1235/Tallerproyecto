"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Users,
  Search,
  UserPlus,
  BookOpen,
  Clock,
  LogOut,
  CheckCircle,
} from "lucide-react"

const enrolledClasses = [
  {
    id: 1,
    name: "Python Basico - Grupo A",
    teacher: "Prof. Maria Garcia",
    students: 25,
    status: "approved",
    joinedAt: "10 Ene 2024",
  },
  {
    id: 2,
    name: "Robotica Introductoria",
    teacher: "Prof. Carlos Lopez",
    students: 18,
    status: "pending",
    joinedAt: "20 Ene 2024",
  },
]

const availableClasses = [
  {
    id: 3,
    name: "Python Avanzado",
    teacher: "Prof. Ana Martinez",
    students: 12,
    maxStudents: 20,
    code: "PYT-ADV",
  },
  {
    id: 4,
    name: "Algoritmos y Estructuras",
    teacher: "Prof. Juan Perez",
    students: 8,
    maxStudents: 15,
    code: "ALG-001",
  },
]

export default function ClassesPage() {
  const [classCode, setClassCode] = useState("")
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">Mis Clases</h1>
        <p className="text-muted-foreground">Gestiona tus inscripciones a clases</p>
      </div>

      {/* Join with code */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <UserPlus className="h-5 w-5 text-primary" />
            Unirse con codigo
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Ingresa el codigo de la clase"
              value={classCode}
              onChange={(e) => setClassCode(e.target.value)}
              className="max-w-xs"
            />
            <Button disabled={!classCode}>Unirse</Button>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Pide el codigo a tu docente para unirte a su clase
          </p>
        </CardContent>
      </Card>

      {/* Enrolled classes */}
      <Card>
        <CardHeader>
          <CardTitle>Clases Inscritas</CardTitle>
        </CardHeader>
        <CardContent>
          {enrolledClasses.length === 0 ? (
            <div className="py-8 text-center">
              <Users className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p className="mt-2 text-muted-foreground">No estas inscrito en ninguna clase</p>
            </div>
          ) : (
            <div className="space-y-4">
              {enrolledClasses.map((cls) => (
                <div
                  key={cls.id}
                  className="flex flex-col gap-4 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-center gap-4">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className="bg-primary/10 text-primary">
                        {cls.name[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-foreground">{cls.name}</h3>
                        {cls.status === "pending" && (
                          <span className="rounded-full bg-yellow-500/10 px-2 py-0.5 text-xs font-medium text-yellow-600">
                            <Clock className="mr-1 inline h-3 w-3" />
                            Pendiente
                          </span>
                        )}
                        {cls.status === "approved" && (
                          <span className="rounded-full bg-accent/10 px-2 py-0.5 text-xs font-medium text-accent">
                            <CheckCircle className="mr-1 inline h-3 w-3" />
                            Activo
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{cls.teacher}</p>
                      <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {cls.students} estudiantes
                        </span>
                        <span>Inscrito: {cls.joinedAt}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {cls.status === "approved" && (
                      <Button variant="outline" size="sm">
                        <BookOpen className="mr-2 h-4 w-4" />
                        Ver clase
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive">
                      <LogOut className="mr-2 h-4 w-4" />
                      Salir
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Browse classes */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Explorar Clases</CardTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar clases..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-48"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            {availableClasses.map((cls) => (
              <div key={cls.id} className="rounded-lg border p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-foreground">{cls.name}</h3>
                    <p className="text-sm text-muted-foreground">{cls.teacher}</p>
                  </div>
                  <span className="rounded bg-muted px-2 py-1 font-mono text-xs">
                    {cls.code}
                  </span>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {cls.students}/{cls.maxStudents} estudiantes
                  </span>
                  <Button size="sm">Solicitar unirse</Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
