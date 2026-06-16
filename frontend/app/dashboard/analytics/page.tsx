"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, Legend,
  ScatterChart, Scatter,
} from "recharts"
import {
  Loader2, AlertTriangle, TrendingUp, Brain, Users,
  Target, Zap, Clock, AlertCircle, UserX, Star, ThumbsUp, ThumbsDown,
  GitBranch, Activity,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null)
  const [students, setStudents] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [difficultyAnalysis, setDifficultyAnalysis] = useState<any[]>([])
  const [riskStudents, setRiskStudents] = useState<any[]>([])
  const [clusters, setClusters] = useState<any>(null)
  const [anomalies, setAnomalies] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const dashRes = await fetch(`${API_URL}/analytics/dashboard?days=30`, { credentials: "include" })
        const json = await dashRes.json()
        if (json.success) {
          const cp = json.class_predictions || {}
          const isProcessing = cp.processing === true
          setData(json)
          setStudents(cp.students || [])
          setSummary(cp.summary || {})
          setProcessing(isProcessing)
        } else {
          setErrorMsg(json.detail || json.error || "Error al cargar analítica")
        }
      } catch (err: any) {
        setErrorMsg(err.message || "Error de conexión al cargar analítica")
      }
    }

    const fetchDifficulty = async () => {
      try {
        const diffRes = await fetch(`${API_URL}/exercises/difficulty-analysis`, { credentials: "include" })
        const diffJson = await diffRes.json()
        if (diffJson.success) {
          setDifficultyAnalysis(diffJson.suggestions || [])
        }
      } catch {
        // Silently fail — difficulty analysis is secondary
      }
    }

    const fetchRiskStudents = async () => {
      try {
        const res = await fetch(`${API_URL}/analytics/risk-students?min_dropout_risk=0.3`, { credentials: "include" })
        const json = await res.json()
        if (json.success) setRiskStudents(json.risk_students || [])
      } catch {}
    }

    const fetchClusters = async () => {
      try {
        const res = await fetch(`${API_URL}/analytics/clusters`, { credentials: "include" })
        const json = await res.json()
        if (json.success) setClusters(json)
      } catch {}
    }

    const fetchAnomalies = async () => {
      try {
        const res = await fetch(`${API_URL}/analytics/anomalies`, { credentials: "include" })
        const json = await res.json()
        if (json.success) setAnomalies(json.anomalies || [])
      } catch {}
    }

    const fetchData = async () => {
      await Promise.all([fetchDashboard(), fetchDifficulty(), fetchRiskStudents(), fetchClusters(), fetchAnomalies()])
      setIsLoading(false)
    }

    fetchData()
  }, [])

  // Poll while predictions are processing
  useEffect(() => {
    if (!processing) return
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/analytics/dashboard?days=30`, { credentials: "include" })
        const json = await res.json()
        if (json.success) {
          const cp = json.class_predictions || {}
          setData(json)
          setStudents(cp.students || [])
          setSummary(cp.summary || {})
          if (cp.processing !== true) {
            setProcessing(false)
          }
        }
      } catch {}
    }, 10000)
    return () => clearInterval(interval)
  }, [processing])

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
        <p className="font-medium text-lg">No pudimos cargar la analítica</p>
        <p className="text-sm">{errorMsg}</p>
      </div>
    )
  }

  const riskColors = { high: "text-destructive", medium: "text-orange-500", low: "text-green-500" }
  const perfColors = { excellent: "text-purple-500", good: "text-green-500", average: "text-yellow-500", low: "text-red-500" }

  const distribution = [
    { name: "Alto Rendimiento", value: summary?.excellent_count || 0, color: "#8b5cf6" },
    { name: "En Riesgo", value: summary?.at_risk_count || 0, color: "#ef4444" },
    { name: "Normal", value: Math.max(0, (summary?.total_students || 0) - (summary?.excellent_count || 0) - (summary?.at_risk_count || 0)), color: "#3b82f6" },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Brain className="h-8 w-8 text-primary" />
          Analítica Predictiva IA
        </h1>
        <p className="text-muted-foreground">
          Métricas avanzadas de rendimiento estudiantil generadas por machine learning.
        </p>
      </div>

      {processing && (
        <div className="flex items-center gap-3 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-700 dark:text-amber-400 text-sm">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Generando predicciones de IA. Los resultados se actualizarán automáticamente en unos segundos.</span>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-primary/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Estudiantes</CardTitle>
            <Users className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary?.total_students || 0}</div>
            <p className="text-xs text-muted-foreground">En tus clases</p>
          </CardContent>
        </Card>
        <Card className="border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Riesgo de Abandono</CardTitle>
            <UserX className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {summary?.at_risk_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {summary?.total_students > 0
                ? `${((summary.at_risk_count / summary.total_students) * 100).toFixed(1)}% del total`
                : "Estudiantes en riesgo"}
            </p>
          </CardContent>
        </Card>
        <Card className="border-purple-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sobresalientes</CardTitle>
            <Star className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-500">
              {summary?.excellent_count || 0}
            </div>
            <p className="text-xs text-muted-foreground">Estudiantes con alto rendimiento</p>
          </CardContent>
        </Card>
        <Card className="border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Engagement Promedio</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary?.avg_engagement != null
                ? `${(summary.avg_engagement * 100).toFixed(0)}%`
                : "—"}
            </div>
            <p className="text-xs text-muted-foreground">Nivel de compromiso general</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="students" className="space-y-4">
        <TabsList>
          <TabsTrigger value="students">Estudiantes</TabsTrigger>
          <TabsTrigger value="distribution">Distribución</TabsTrigger>
          <TabsTrigger value="activity">Actividad</TabsTrigger>
          <TabsTrigger value="difficulty">Dificultad</TabsTrigger>
          <TabsTrigger value="risk" className="text-red-500">En Riesgo</TabsTrigger>
          <TabsTrigger value="clusters">Clusters</TabsTrigger>
          <TabsTrigger value="anomalies">Anomalías</TabsTrigger>
        </TabsList>

        <TabsContent value="students" className="space-y-4">
          {students.length === 0 && processing ? (
            <div className="flex flex-col items-center justify-center p-12 bg-card rounded-xl border border-dashed text-center">
              <Loader2 className="h-8 w-8 text-primary animate-spin mb-4" />
              <h3 className="text-lg font-semibold mb-1">Generando predicciones...</h3>
              <p className="text-muted-foreground text-sm">Estamos analizando los datos de tus estudiantes. Los resultados aparecerán automáticamente en unos momentos.</p>
            </div>
          ) : students.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 bg-card rounded-xl border border-dashed text-center">
              <Users className="h-8 w-8 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-1">Sin datos de estudiantes</h3>
              <p className="text-muted-foreground text-sm">Aún no hay suficientes datos para generar predicciones.</p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {students.map((s: any) => (
                <Card key={s.student_id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base">Estudiante #{s.student_id}</CardTitle>
                      <Badge variant={s.dropout_risk > 0.5 ? "destructive" : s.dropout_risk > 0.3 ? "secondary" : "outline"}>
                        {s.dropout_risk_label === "high" ? "Alto Riesgo" : s.dropout_risk_label === "medium" ? "Riesgo Medio" : "Estable"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Rendimiento</span>
                        <span className={`font-medium ${perfColors[s.performance_label as keyof typeof perfColors] || ""}`}>
                          {(s.performance_score * 100).toFixed(0)}% - {s.performance_label}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Engagement</span>
                        <span className="font-medium">
                          {(s.engagement_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Frustración</span>
                        <span className={`font-medium ${s.frustration_level >= 2 ? "text-destructive" : s.frustration_level === 1 ? "text-orange-500" : "text-green-500"}`}>
                          {s.frustration_label}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Riesgo Abandono</span>
                        <span className={`font-medium ${riskColors[s.dropout_risk_label as keyof typeof riskColors] || ""}`}>
                          {(s.dropout_risk * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="distribution">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Distribución de Rendimiento</CardTitle>
                <CardDescription>Clasificación de estudiantes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={distribution}
                        cx="50%" cy="50%"
                        innerRadius={60} outerRadius={90}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ value }) => value > 0 ? value : ""}
                      >
                        {distribution.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resumen de Clase</CardTitle>
                <CardDescription>Métricas promedio</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-primary/5 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-primary" />
                    <span className="text-sm">Rendimiento Promedio</span>
                  </div>
                  <span className="font-bold">
                    {summary?.avg_performance != null
                      ? `${(summary.avg_performance * 100).toFixed(1)}%`
                      : "—"}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-500/5 rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">Engagement Promedio</span>
                  </div>
                  <span className="font-bold">
                    {summary?.avg_engagement != null
                      ? `${(summary.avg_engagement * 100).toFixed(1)}%`
                      : "—"}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-red-500/5 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span className="text-sm">Riesgo de Abandono Prom.</span>
                  </div>
                  <span className="font-bold text-red-500">
                    {summary?.avg_dropout_risk != null
                      ? `${(summary.avg_dropout_risk * 100).toFixed(1)}%`
                      : "—"}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="activity">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Actividad Diaria (7 días)</CardTitle>
                <CardDescription>Eventos registrados por día</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data?.daily_activity || []}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="_id" tick={{ fontSize: 11 }} />
                      <YAxis />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Señales de Frustración</CardTitle>
                <CardDescription>Últimos 7 días</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data?.frustration_trend || []}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="_id" tick={{ fontSize: 11 }} />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="difficulty">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-primary" />
                  Análisis de Dificultad de Ejercicios
                </CardTitle>
                <CardDescription>Sugerencias basadas en tasas de acierto de estudiantes</CardDescription>
              </CardHeader>
              <CardContent>
                {difficultyAnalysis.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>Aún no hay suficientes datos para analizar la dificultad de los ejercicios.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {difficultyAnalysis.map((s: any) => (
                      <Card key={s.exercise_id} className={`border-l-4 ${s.type === "too_hard" ? "border-l-red-500" : s.type === "too_easy" ? "border-l-green-500" : "border-l-amber-500"}`}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h4 className="font-semibold text-sm">{s.title}</h4>
                                <span className="text-xs text-muted-foreground">— {s.module_title}</span>
                              </div>
                              <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                                <span className="flex items-center gap-1"><Zap className="w-3 h-3" />{s.total_attempts} intentos</span>
                                <span className="flex items-center gap-1"><Users className="w-3 h-3" />{s.unique_students} estudiantes</span>
                                <span className="flex items-center gap-1">
                                  {s.pass_rate >= 85 ? <ThumbsUp className="w-3 h-3 text-green-500" /> : s.pass_rate < 30 ? <ThumbsDown className="w-3 h-3 text-red-500" /> : <Clock className="w-3 h-3" />}
                                  {s.pass_rate}% acierto
                                </span>
                              </div>
                              <p className="text-sm">{s.message}</p>
                              {s.alternative && (
                                <p className="text-xs text-muted-foreground mt-1 italic">{s.alternative}</p>
                              )}
                            </div>
                            <div className="shrink-0">
                              <Badge variant={s.type === "too_hard" ? "destructive" : s.type === "too_easy" ? "secondary" : "outline"}>
                                {s.type === "too_hard" ? "Muy difícil" : s.type === "too_easy" ? "Muy fácil" : "Revisar"}
                              </Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="risk">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserX className="h-5 w-5 text-red-500" />
                  Estudiantes en Riesgo
                </CardTitle>
                <CardDescription>Estudiantes con alto riesgo de abandono, frustración o bajo engagement</CardDescription>
              </CardHeader>
              <CardContent>
                {riskStudents.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No hay estudiantes en riesgo detectados.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {riskStudents.map((s: any) => (
                      <Card key={s.student_id} className="border-l-4 border-l-red-500">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold text-sm">Estudiante #{s.student_id}</h4>
                              <div className="flex gap-3 mt-2 text-sm text-muted-foreground">
                                <span className="text-red-500">Abandono: {s.dropout_risk != null ? `${(s.dropout_risk * 100).toFixed(0)}%` : "N/A"}</span>
                                <span className="text-amber-500">Frustración: {s.frustration_level === 2 ? "Alta" : s.frustration_level === 1 ? "Media" : "Baja"}</span>
                                <span className="text-blue-500">Engagement: {s.engagement != null ? `${(s.engagement * 100).toFixed(0)}%` : s.engagement_score != null ? `${(s.engagement_score * 100).toFixed(0)}%` : "N/A"}</span>
                              </div>
                            </div>
                            <Badge variant="destructive">En Riesgo</Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="clusters">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-primary" />
                  Distribución de Clusters
                </CardTitle>
                <CardDescription>Grupos de aprendizaje detectados por KMeans</CardDescription>
              </CardHeader>
              <CardContent>
                {clusters?.distribution ? (
                  <div className="h-[250px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={Object.entries(clusters.distribution).map(([k, v]) => ({ cluster: k, count: v }))}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="cluster" />
                        <YAxis />
                        <RechartsTooltip />
                        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                          {(Object.entries(clusters.distribution) as [string, number][]).map(([k]) => (
                            <rect key={k} fill={["#3b82f6","#10b981","#f59e0b","#ef4444"][parseInt(k) % 4]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-center py-8 text-muted-foreground text-sm">Sin datos de clusters.</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  Proyección PCA 2D
                </CardTitle>
                <CardDescription>Visualización de clusters reducida a 2 componentes</CardDescription>
              </CardHeader>
              <CardContent>
                {clusters?.pca_projection && clusters.pca_projection.length > 0 ? (
                  <div className="h-[250px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="x" type="number" />
                        <YAxis dataKey="y" type="number" />
                        <RechartsTooltip />
                        {Array.from(new Set(clusters.pca_projection.map((p: any) => p.cluster))).map((c: any) => (
                          <Scatter key={c} data={clusters.pca_projection.filter((p: any) => p.cluster === c)} fill={["#3b82f6","#10b981","#f59e0b","#ef4444"][c % 4]} name={`Cluster ${c}`} />
                        ))}
                      </ScatterChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-center py-8 text-muted-foreground text-sm">Sin datos de proyección PCA.</p>
                )}
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Resumen de Clusters</CardTitle>
              </CardHeader>
              <CardContent>
                {clusters?.summary && clusters.summary.length > 0 ? (
                  <div className="grid gap-3 md:grid-cols-4">
                    {clusters.summary.map((s: any, i: number) => (
                      <Card key={i} className="p-3">
                        <h4 className="text-sm font-semibold mb-1">Cluster {s.cluster}</h4>
                        <p className="text-xs text-muted-foreground">Estudiantes: {s.count}</p>
                        <p className="text-xs text-muted-foreground">Engagement: {(s.avg_engagement * 100).toFixed(0)}%</p>
                        <p className="text-xs text-muted-foreground">Rendimiento: {(s.avg_performance * 100).toFixed(0)}%</p>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <p className="text-center py-4 text-muted-foreground">Sin resumen disponible.</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="anomalies">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                Detección de Anomalías
              </CardTitle>
              <CardDescription>Estudiantes con patrones de comportamiento atípicos detectados por IsolationForest</CardDescription>
            </CardHeader>
            <CardContent>
              {anomalies.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No se detectaron anomalías recientes.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {anomalies.map((a: any, i: number) => (
                    <Card key={i} className="border-l-4 border-l-amber-500">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-sm">Estudiante #{a.student_id}</h4>
                            <p className="text-sm text-muted-foreground mt-1">
                              Semana {a.week_number} — Score: {(a.anomaly_score * 100).toFixed(0)}%
                            </p>
                            {a.reason && <p className="text-xs text-muted-foreground mt-1">{a.reason}</p>}
                          </div>
                          <Badge variant="outline" className="text-amber-500 border-amber-500">
                            Score: {(a.anomaly_score * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
