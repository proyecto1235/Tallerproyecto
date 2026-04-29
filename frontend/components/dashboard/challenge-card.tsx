import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Star, Flame, Zap, Trophy } from "lucide-react"

export interface ChallengeCardProps {
  id: string
  title: string
  description: string
  difficulty: "Fácil" | "Medio" | "Difícil" | "Jefe Final"
  reward: number
  status: "completed" | "active" | "expired" | "running"
  type: "daily" | "weekly" | "special"
  timeRemaining?: string
  onClick?: () => void
}

export function ChallengeCard({
  title,
  description,
  difficulty,
  reward,
  status,
  type,
  timeRemaining,
  onClick
}: ChallengeCardProps) {
  
  const difficultyColors = {
    "Fácil": "bg-green-500/10 text-green-600 border-green-500/20",
    "Medio": "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
    "Difícil": "bg-orange-500/10 text-orange-600 border-orange-500/20",
    "Jefe Final": "bg-red-500/10 text-red-600 border-red-500/20",
  }

  const typeIcon = {
    "daily": <Zap className="h-5 w-5 text-yellow-500" />,
    "weekly": <Flame className="h-5 w-5 text-orange-500" />,
    "special": <Trophy className="h-5 w-5 text-purple-500" />
  }

  return (
    <Card className={`relative overflow-hidden border-2 transition-all ${
      status === 'completed' ? 'border-green-500/50 bg-green-500/5' : 
      status === 'expired' ? 'opacity-60 grayscale-[0.5]' : 'border-primary/20 hover:border-primary/50'
    }`}>
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div className="flex gap-3 items-center">
            <div className="p-2 rounded-xl bg-background shadow-sm border">
              {typeIcon[type]}
            </div>
            <div>
              <h3 className="font-bold text-lg leading-tight">{title}</h3>
              {timeRemaining && status === 'active' && (
                <p className="text-xs text-muted-foreground mt-1">
                  Termina en {timeRemaining}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1 bg-yellow-500/10 text-yellow-600 px-2 py-1 rounded-full text-sm font-bold">
            <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
            +{reward}
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-4">
          {description}
        </p>

        <div className="flex items-center justify-between">
          <span className={`text-xs px-2 py-1 rounded-md border font-semibold ${difficultyColors[difficulty]}`}>
            {difficulty}
          </span>
          
          {status === 'completed' ? (
            <span className="text-sm font-bold text-green-500 flex items-center gap-1">
              ¡Completado!
            </span>
          ) : status === 'expired' ? (
            <span className="text-sm font-bold text-muted-foreground flex items-center gap-1">
              Expirado
            </span>
          ) : (
            <Button 
              size="sm" 
              variant="secondary" 
              className="font-bold"
              onClick={onClick}
              disabled={status === 'running'}
            >
              {status === 'running' ? 'Completando...' : 'Intentar Reto'}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
