"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Search, BookOpen, Clock, Loader2 } from "lucide-react"

export default function ClassesPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [availableClasses, setAvailableClasses] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Fetch classes dynamically
  useEffect(() => {
    const fetchClasses = async () => {
      setIsLoading(true)
      try {
        const res = await fetch(`http://localhost:8000/api/modules/search?q=${searchQuery}`, {
          credentials: 'include'
        })
        const data = await res.json()
        if (data.success) {
          setAvailableClasses(data.results)
        }
      } catch (error) {
        console.error("Error fetching classes:", error)
      } finally {
        setIsLoading(false)
      }
    }

    const delayDebounceFn = setTimeout(() => {
      fetchClasses()
    }, 300)

    return () => clearTimeout(delayDebounceFn)
  }, [searchQuery])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">Mis Clases</h1>
        <p className="text-muted-foreground">Explora y únete a nuevas clases (módulos)</p>
      </div>

      {/* Browse classes */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Explorar Clases</CardTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar por clase o docente..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-64"
            />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : availableClasses.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No se encontraron clases
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {availableClasses.map((cls) => (
                <div key={cls.id} className="rounded-lg border p-4 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-foreground">{cls.title}</h3>
                      <p className="text-sm text-muted-foreground">Prof. {cls.teacher_name}</p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground line-clamp-2">{cls.description}</p>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <Button size="sm" variant="outline">
                      <BookOpen className="h-4 w-4 mr-2" /> Ver detalles
                    </Button>
                    <Button size="sm">Matricularse</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
