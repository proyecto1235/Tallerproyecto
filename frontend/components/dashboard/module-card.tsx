import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { CheckCircle2, Lock, PlayCircle, Trophy } from "lucide-react"

export interface ModuleCardProps {
  id: string
  title: string
  description: string
  level: number
  status: "completed" | "in-progress" | "locked"
  progress: number
  onClick?: () => void
}

export function ModuleCard({
  title,
  description,
  level,
  status,
  progress,
  onClick,
}: ModuleCardProps) {
  const isLocked = status === "locked"
  const isCompleted = status === "completed"

  return (
    <Card className={`relative overflow-hidden transition-all duration-300 ${isLocked ? 'opacity-70 grayscale-[0.5]' : 'hover:shadow-lg hover:-translate-y-1'}`}>
      <div className={`absolute top-0 left-0 w-2 h-full ${
        isCompleted ? 'bg-green-500' : 
        status === 'in-progress' ? 'bg-primary' : 'bg-muted'
      }`} />
      
      <CardHeader className="pl-6 pb-2">
        <div className="flex justify-between items-start">
          <div className="space-y-1">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
              Nivel {level}
            </span>
            <h3 className="font-bold text-xl leading-none">{title}</h3>
          </div>
          <div className={`p-2 rounded-full ${
            isCompleted ? 'bg-green-500/10 text-green-500' : 
            status === 'in-progress' ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
          }`}>
            {isCompleted ? <CheckCircle2 className="h-5 w-5" /> : 
             isLocked ? <Lock className="h-5 w-5" /> : 
             <PlayCircle className="h-5 w-5" />}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pl-6">
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
          {description}
        </p>
        
        {!isLocked && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-medium">
              <span>Progreso</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}
      </CardContent>

      <CardFooter className="pl-6 pt-2">
        <Button 
          variant={isCompleted ? "outline" : "default"} 
          className={`w-full ${isLocked ? 'cursor-not-allowed' : ''}`}
          disabled={isLocked}
          onClick={onClick}
        >
          {isCompleted ? 'Repasar Módulo' : 
           isLocked ? 'Bloqueado' : 'Continuar Aprendiendo'}
        </Button>
      </CardFooter>
    </Card>
  )
}
