import { Trophy, Star, Shield, Medal, Zap, Award, Target, Flame } from "lucide-react"

export interface AchievementBadgeProps {
  id: string
  title: string
  description: string
  icon: "trophy" | "star" | "shield" | "medal" | "zap" | "award" | "target" | "flame"
  date?: string
  isLocked?: boolean
  rarity?: "common" | "rare" | "epic" | "legendary"
}

export function AchievementBadge({
  title,
  description,
  icon,
  date,
  isLocked = false,
  rarity = "common"
}: AchievementBadgeProps) {
  
  const icons = {
    trophy: Trophy,
    star: Star,
    shield: Shield,
    medal: Medal,
    zap: Zap,
    award: Award,
    target: Target,
    flame: Flame
  }

  const IconComponent = icons[icon] || Trophy

  const rarityStyles = {
    common: "from-slate-200 to-slate-400 border-slate-300 text-slate-700",
    rare: "from-blue-200 to-blue-400 border-blue-300 text-blue-800",
    epic: "from-purple-200 to-purple-400 border-purple-300 text-purple-800",
    legendary: "from-yellow-200 to-yellow-500 border-yellow-400 text-yellow-900"
  }

  const activeStyle = rarityStyles[rarity]
  const lockedStyle = "from-muted to-muted/50 border-border text-muted-foreground grayscale"

  return (
    <div className={`relative group flex flex-col items-center text-center p-4 rounded-2xl transition-all duration-300 ${isLocked ? 'opacity-60' : 'hover:-translate-y-2 hover:shadow-xl bg-card border shadow-sm'}`}>
      
      <div className={`w-20 h-20 rounded-full flex items-center justify-center border-4 shadow-inner bg-gradient-to-br mb-3 ${isLocked ? lockedStyle : activeStyle}`}>
        <IconComponent className={`w-10 h-10 ${isLocked ? 'opacity-40' : 'drop-shadow-md'}`} />
      </div>
      
      <h4 className="font-bold text-sm mb-1 leading-tight">{title}</h4>
      <p className="text-xs text-muted-foreground line-clamp-2 max-w-[150px]">
        {isLocked ? 'Bloqueado' : description}
      </p>
      
      {!isLocked && date && (
        <span className="text-[10px] font-medium text-primary/70 mt-2 bg-primary/10 px-2 py-0.5 rounded-full">
          {date}
        </span>
      )}

      {/* Tooltip on hover */}
      <div className="absolute opacity-0 group-hover:opacity-100 transition-opacity bg-popover text-popover-foreground text-xs p-2 rounded shadow-lg -top-10 left-1/2 -translate-x-1/2 pointer-events-none w-48 z-10 border">
        <p className="font-bold mb-1">{title}</p>
        <p className="text-muted-foreground">{description}</p>
        {isLocked && <p className="text-primary mt-1 text-[10px]">Sigue jugando para desbloquear</p>}
      </div>
    </div>
  )
}
