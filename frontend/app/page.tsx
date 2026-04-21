import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Code,
  Cpu,
  Trophy,
  Users,
  Zap,
  BookOpen,
  GraduationCap,
  Rocket,
  CheckCircle,
  ArrowRight,
} from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <Code className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">RoboLearn</span>
          </Link>
          <nav className="hidden items-center gap-6 md:flex">
            <Link href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Caracteristicas
            </Link>
            <Link href="#modules" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Modulos
            </Link>
            <Link href="#roles" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Roles
            </Link>
          </nav>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link href="/login">Iniciar Sesion</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Registrarse</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 md:py-32">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
        <div className="container mx-auto px-4 text-center">
          <div className="mx-auto max-w-3xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-card px-4 py-1.5 text-sm">
              <Zap className="h-4 w-4 text-primary" />
              <span>Plataforma educativa gamificada</span>
            </div>
            <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground md:text-6xl text-balance">
              Aprende{" "}
              <span className="text-primary">Programacion</span> y{" "}
              <span className="text-accent">Robotica</span> de forma divertida
            </h1>
            <p className="mb-8 text-lg text-muted-foreground md:text-xl text-pretty">
              Una plataforma disenada para estudiantes que quieren aprender Python desde cero. 
              Con ejercicios interactivos, retos semanales y un sistema de logros que hace 
              el aprendizaje emocionante.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button size="lg" asChild className="w-full sm:w-auto">
                <Link href="/register">
                  Comenzar gratis
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="w-full sm:w-auto">
                <Link href="#modules">Ver modulos</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="border-t bg-card py-20">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">
              Por que elegir CodeKids
            </h2>
            <p className="text-muted-foreground">
              Disenado especialmente para estudiantes en etapa escolar
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={<BookOpen className="h-6 w-6" />}
              title="Aprendizaje Progresivo"
              description="Modulos organizados como un arbol de conocimiento. Avanza a tu propio ritmo desde lo basico hasta conceptos avanzados."
            />
            <FeatureCard
              icon={<Zap className="h-6 w-6" />}
              title="Ejercicios Interactivos"
              description="Practica escribiendo codigo real con retroalimentacion inmediata. Aprende haciendo, no solo leyendo."
            />
            <FeatureCard
              icon={<Trophy className="h-6 w-6" />}
              title="Gamificacion"
              description="Gana puntos, medallas y sube en el ranking. Los retos semanales mantienen la motivacion alta."
            />
            <FeatureCard
              icon={<Cpu className="h-6 w-6" />}
              title="Robotica"
              description="Aprende a programar robots y entiende como el codigo controla el mundo fisico."
            />
            <FeatureCard
              icon={<Users className="h-6 w-6" />}
              title="Clases y Docentes"
              description="Unete a clases creadas por docentes verificados. Recibe retroalimentacion personalizada."
            />
            <FeatureCard
              icon={<Rocket className="h-6 w-6" />}
              title="IA de Apoyo"
              description="Recomendaciones personalizadas que identifican tus areas de mejora y te sugieren ejercicios."
            />
          </div>
        </div>
      </section>

      {/* Learning Path Section */}
      <section id="modules" className="py-20">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">
              Tu camino de aprendizaje
            </h2>
            <p className="text-muted-foreground">
              Desde los fundamentos hasta la robotica
            </p>
          </div>
          <div className="mx-auto max-w-4xl">
            <div className="relative">
              {/* Connection line */}
              <div className="absolute left-8 top-0 hidden h-full w-0.5 bg-border md:block" />
              <div className="space-y-6">
                <ModuleCard
                  number={1}
                  title="Introduccion a Python"
                  description="Conoce el lenguaje, escribe tu primer programa y entiende la sintaxis basica."
                  difficulty="Principiante"
                  lessons={3}
                />
                <ModuleCard
                  number={2}
                  title="Variables y Tipos de Datos"
                  description="Aprende a almacenar informacion en variables y a trabajar con numeros y texto."
                  difficulty="Principiante"
                  lessons={3}
                />
                <ModuleCard
                  number={3}
                  title="Estructuras de Control"
                  description="Toma decisiones en tu codigo con if, elif y else."
                  difficulty="Intermedio"
                  lessons={2}
                />
                <ModuleCard
                  number={4}
                  title="Bucles y Repeticiones"
                  description="Domina for y while para automatizar tareas repetitivas."
                  difficulty="Intermedio"
                  lessons={2}
                />
                <ModuleCard
                  number={5}
                  title="Funciones"
                  description="Crea bloques de codigo reutilizables y organiza mejor tus programas."
                  difficulty="Avanzado"
                  lessons={3}
                />
                <ModuleCard
                  number={6}
                  title="Robotica Basica"
                  description="Aplica todo lo aprendido para programar robots y proyectos fisicos."
                  difficulty="Avanzado"
                  lessons={4}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section id="roles" className="border-t bg-card py-20">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-foreground md:text-4xl">
              Para cada tipo de usuario
            </h2>
            <p className="text-muted-foreground">
              Funcionalidades especificas segun tu rol
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            <RoleCard
              icon={<GraduationCap className="h-8 w-8" />}
              title="Estudiantes"
              features={[
                "Dashboard con progreso y logros",
                "Modulos de aprendizaje interactivos",
                "Retos semanales con recompensas",
                "Inscripcion a clases de docentes",
              ]}
            />
            <RoleCard
              icon={<BookOpen className="h-8 w-8" />}
              title="Docentes"
              features={[
                "Panel de metricas de estudiantes",
                "Crear y gestionar clases",
                "Alertas de IA sobre dificultades",
                "Crear contenido educativo",
              ]}
              highlighted
            />
            <RoleCard
              icon={<Users className="h-8 w-8" />}
              title="Administradores"
              features={[
                "Gestion de usuarios y roles",
                "Aprobar solicitudes de docentes",
                "Supervision de contenido",
                "Configuracion del sistema",
              ]}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl rounded-2xl bg-primary p-8 text-center text-primary-foreground md:p-12">
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">
              Comienza tu aventura hoy
            </h2>
            <p className="mb-8 text-primary-foreground/80">
              Unete a miles de estudiantes que estan aprendiendo programacion de forma divertida.
            </p>
            <Button size="lg" variant="secondary" asChild>
              <Link href="/register">
                Crear cuenta gratis
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <Code className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-semibold text-foreground">CodeKids</span>
            </div>
            <p className="text-sm text-muted-foreground">
              2024 CodeKids. Plataforma educativa de programacion.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <Card className="border-0 shadow-sm">
      <CardContent className="p-6">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
          {icon}
        </div>
        <h3 className="mb-2 text-lg font-semibold text-foreground">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}

function ModuleCard({
  number,
  title,
  description,
  difficulty,
  lessons,
}: {
  number: number
  title: string
  description: string
  difficulty: string
  lessons: number
}) {
  const difficultyColors: Record<string, string> = {
    Principiante: "bg-accent/10 text-accent-foreground",
    Intermedio: "bg-warning/10 text-warning-foreground",
    Avanzado: "bg-primary/10 text-primary",
  }

  return (
    <div className="relative flex gap-4">
      <div className="relative z-10 flex h-16 w-16 shrink-0 items-center justify-center rounded-full border-4 border-background bg-primary text-xl font-bold text-primary-foreground">
        {number}
      </div>
      <Card className="flex-1 border-0 shadow-sm">
        <CardContent className="p-4">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-foreground">{title}</h3>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${difficultyColors[difficulty]}`}>
              {difficulty}
            </span>
          </div>
          <p className="mb-2 text-sm text-muted-foreground">{description}</p>
          <p className="text-xs text-muted-foreground">{lessons} lecciones</p>
        </CardContent>
      </Card>
    </div>
  )
}

function RoleCard({
  icon,
  title,
  features,
  highlighted = false,
}: {
  icon: React.ReactNode
  title: string
  features: string[]
  highlighted?: boolean
}) {
  return (
    <Card className={`relative overflow-hidden border-0 shadow-sm ${highlighted ? "ring-2 ring-primary" : ""}`}>
      {highlighted && (
        <div className="absolute right-0 top-0 rounded-bl-lg bg-primary px-3 py-1 text-xs font-medium text-primary-foreground">
          Solicita ser docente
        </div>
      )}
      <CardContent className="p-6">
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-primary/10 text-primary">
          {icon}
        </div>
        <h3 className="mb-4 text-xl font-semibold text-foreground">{title}</h3>
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
              <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
