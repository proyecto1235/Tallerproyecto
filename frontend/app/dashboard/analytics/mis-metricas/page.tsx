"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, ResponsiveContainer, Legend,
} from "recharts"
import {
  Loader2, AlertTriangle, TrendingUp, Brain, Target,
  Zap, AlertCircle, UserX, Star, Activity, Clock,
} from "lucide-react"
import { useAuth } from "@/hooks/use-auth"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const COLORS = {
  engagement: "#3b82f6",
  performance: "#10b981",
  dropout: "#ef4444",
  frustration: "#f59e0b",
}

export default function MisMetricasPage() {
  const { user } = useAuth()
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  useEffect(() => {
    if (!user?.id) return
    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${API_URL}/analytics/student/${user.id}`, { credentials: "include" })
        const json = await res.json()
        if (json.success) {
          setData(json)
        } else {
          setErrorMsg(json.detail || "Error al cargar métricas")
        }
      } catch (err: any) {
        setErrorMsg(err.message || "Error de conexión")
      } finally {
        setIsLoading(false)
      }
    }
    fetchMetrics()
  }, [user?.id])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (errorMsg) {
    return (
      <div className="flex flex-col justify-center items-center h-full min-h-[400px] text-muted-foreground gap-4">
        <AlertTriangle className="h-10 w-10 text-destructive/50" />
        <p className="font-medium text-lg">No pudimos cargar tus métricas</p>
        <p className="text-sm">{errorMsg}</p>
      </div>
    )
  }

  const preds = data?.predictions || {}
  const engagement = preds.engagement_projected || {}
  const performance = preds.performance_projected || {}
  const dropout = preds.dropout_risk || {}
  const frustration = preds.frustration_projected || {}

  const weekly = data?.weekly_history || []
  const weeklyChart = weekly.map((w: any) => ({
    week: `S${w.week_number}`,
    engagement: +(w.engagement_score * 100).toFixed(0),
    performance: +(w.performance_score * 100).toFixed(0),
    frustration: +(w.frustration_score * 100).toFixed(0),
    error_rate: +(w.avg_error_rate * 100).toFixed(0),
  })).reverse()

  const predictionsChart = [
    { name: "Engagement", value: +(engagement.value * 100).toFixed(0), fill: COLORS.engagement },
    { name: "Rendimiento", value: +(performance.value * 100).toFixed(0), fill: COLORS.performance },
    { name: "Frustración", value: +(frustration.probabilities?.[2] * 100).toFixed(0) || 0, fill: COLORS.frustration },
    { name: "Riesgo Abandono", value: +(dropout.probability * 100).toFixed(0), fill: COLORS.dropout },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Brain className="h-8 w-8 text-primary" />
          Mis Métricas de Aprendizaje
        </h1>
        <p className="text-muted-foreground">
          Proyecciones de Machine Learning basadas en tu actividad.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Engagement</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">
              {(engagement.value * 100).toFixed(0)}%
            </div>
            <p className="text-xs text-muted-foreground">{engagement.label}</p>
          </CardContent>
        </Card>

        <Card className="border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rendimiento</CardTitle>
            <Target className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {(performance.value * 100).toFixed(0)}%
            </div>
            <p className="text-xs text-muted-foreground">{performance.label}</p>
          </CardContent>
        </Card>

        <Card className="border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Riesgo Abandono</CardTitle>
            <UserX className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {(dropout.probability * 100).toFixed(1)}%
            </div>
            <Badge variant={dropout.label === "alto" ? "destructive" : dropout.label === "medio" ? "secondary" : "outline"}>
              {dropout.label}
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-amber-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Frustración</CardTitle>
            <Zap className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-500">
              {frustration.label}
            </div>
            <p className="text-xs text-muted-foreground">
              Nivel {frustration.class === 2 ? "Alto" : frustration.class === 1 ? "Medio" : "Bajo"}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              Proyecciones ML
            </CardTitle>
            <CardDescription>Predicciones actuales del modelo</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={predictionsChart}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} />
                  <RechartsTooltip formatter={(v: number) => `${v}%`} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {predictionsChart.map((entry, i) => (
                      <rect key={i} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Historial Semanal
            </CardTitle>
            <CardDescription>Evolución de métricas semana a semana</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weeklyChart}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="week" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="engagement" stroke={COLORS.engagement} strokeWidth={2} dot={false} name="Engagement" />
                  <Line type="monotone" dataKey="performance" stroke={COLORS.performance} strokeWidth={2} dot={false} name="Rendimiento" />
                  <Line type="monotone" dataKey="frustration" stroke={COLORS.frustration} strokeWidth={2} dot={false} name="Frustración" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5 text-primary" />
            Recomendaciones Personalizadas
          </CardTitle>
          <CardDescription>Basadas en tu perfil de aprendizaje</CardDescription>
        </CardHeader>
        <CardContent>
          {data?.recommendations?.length > 0 ? (
            <div className="space-y-3">
              {data.recommendations.map((rec: any, i: number) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                  <div className="mt-0.5">
                    {rec.type === "warning" ? (
                      <AlertCircle className="h-4 w-4 text-amber-500" />
                    ) : rec.type === "danger" ? (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    ) : (
                      <Star className="h-4 w-4 text-blue-500" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm">{rec.message || rec.recommendation}</p>
                    {rec.action && (
                      <p className="text-xs text-muted-foreground mt-1">{rec.action}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-4">
              No hay recomendaciones disponibles aún.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
