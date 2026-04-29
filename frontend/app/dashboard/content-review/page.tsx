"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Loader2, FileText, Globe, BookOpen, Edit, Trash2, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

const MOCK_CONTENT = [
  { id: 1, title: "Fundamentos de Robótica", author: "RoboLearn System", category: "General", isPublished: true, views: 1205 },
  { id: 2, title: "Programación en Python", author: "RoboLearn System", category: "General", isPublished: true, views: 890 },
  { id: 3, title: "Sensores Avanzados", author: "RoboLearn System", category: "General", isPublished: false, views: 0 },
  { id: 4, title: "Proyecto: Brazo Robótico", author: "Prof. Carlos", category: "Específico", isPublished: true, views: 340 },
  { id: 5, title: "Taller Arduino Básico", author: "Escuela San José", category: "Específico", isPublished: false, views: 0 },
]

export default function ContentReviewPage() {
  const [content, setContent] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    // Simular carga
    setTimeout(() => {
      setContent(MOCK_CONTENT)
      setIsLoading(false)
    }, 800)
  }, [])

  const handleTogglePublish = (id: number, currentStatus: boolean, title: string) => {
    setContent(content.map(c => c.id === id ? { ...c, isPublished: !currentStatus } : c))
    toast.success(`El módulo "${title}" ahora está ${!currentStatus ? 'publicado' : 'despublicado'}.`)
  }

  const handleDelete = (id: number, title: string) => {
    setContent(content.filter(c => c.id !== id))
    toast.success(`Módulo "${title}" eliminado permanentemente.`)
  }

  const renderTable = (filteredContent: any[]) => {
    const data = filteredContent.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()) || c.author.toLowerCase().includes(searchQuery.toLowerCase()))
    
    return (
      <div className="rounded-md border overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Título del Módulo</TableHead>
              <TableHead>Autor</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead>Vistas</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item) => (
              <TableRow key={item.id} className="hover:bg-muted/50">
                <TableCell>
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-primary" />
                    <span className="font-semibold">{item.title}</span>
                  </div>
                </TableCell>
                <TableCell>{item.author}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Switch 
                      checked={item.isPublished} 
                      onCheckedChange={() => handleTogglePublish(item.id, item.isPublished, item.title)} 
                    />
                    <Badge variant={item.isPublished ? "default" : "secondary"}>
                      {item.isPublished ? "Publicado" : "Borrador"}
                    </Badge>
                  </div>
                </TableCell>
                <TableCell>{item.views} lecturas</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="icon" onClick={() => toast.info("Función de editar en desarrollo")} title="Editar Módulo">
                      <Edit className="h-4 w-4 text-orange-500" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(item.id, item.title)} title="Eliminar Módulo">
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {data.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                  No se encontraron módulos.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Gestión de Contenido</h1>
        <p className="text-muted-foreground text-lg">
          Supervisa los módulos educativos, aprueba contenido de profesores y gestiona el catálogo.
        </p>
      </div>

      <Card className="neo-shadow border-primary/20">
        <CardHeader className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <CardTitle>Catálogo de Módulos</CardTitle>
            <CardDescription>Control total sobre lo que los estudiantes pueden ver.</CardDescription>
          </div>
          <div className="relative w-full md:w-auto">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar por título o autor..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-full md:w-80"
            />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <Tabs defaultValue="all" className="space-y-4">
              <TabsList className="bg-muted/50 p-1">
                <TabsTrigger value="all" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                  Todos los Módulos
                </TabsTrigger>
                <TabsTrigger value="general" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                  <Globe className="h-4 w-4" /> Globales
                </TabsTrigger>
                <TabsTrigger value="specific" className="flex items-center gap-2 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
                  <BookOpen className="h-4 w-4" /> De Profesores
                </TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4">
                {renderTable(content)}
              </TabsContent>
              
              <TabsContent value="general" className="space-y-4">
                {renderTable(content.filter(c => c.category === "General"))}
              </TabsContent>
              
              <TabsContent value="specific" className="space-y-4">
                {renderTable(content.filter(c => c.category === "Específico"))}
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
