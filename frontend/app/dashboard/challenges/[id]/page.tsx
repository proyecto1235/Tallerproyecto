"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import CodeMirror from "@uiw/react-codemirror"
import { python } from "@codemirror/lang-python"
import { oneDark } from "@codemirror/theme-one-dark"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Play, Terminal, CheckCircle2, XCircle, Trophy, ArrowLeft, Loader2, Clock, Eye, Zap, Target } from "lucide-react"
import { toast } from "sonner"

export default function ChallengeDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [challenge, setChallenge] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const [code, setCode] = useState("")
  const [output, setOutput] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "running" | "success" | "error">("idle")
  const [passed, setPassed] = useState(false)
  const [showSolution, setShowSolution] = useState(false)

  useEffect(() => {
    const fetchChallenge = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/challenges/${params.id}`, { credentials: 'include' })
        const data = await res.json()
        if (data.success) {
          setChallenge(data.challenge)
          setCode(data.challenge.base_code || data.challenge.instructions || "# Escribe tu código aquí\n")
          setPassed(data.challenge.user_passed || false)
          if (data.challenge.deadline_passed) {
            setShowSolution(true)
          }
        }
      } catch (e) {
        console.error("Error fetching challenge", e)
      } finally {
        setLoading(false)
      }
    }
    if (params.id) fetchChallenge()
  }, [params.id])

  const handleSubmit = async () => {
    if (passed) return
    setStatus("running")
    setOutput("Ejecutando código...")

    try {
      const res = await fetch("http://localhost:8000/api/challenges/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: 'include',
        body: JSON.stringify({ challenge_id: Number(params.id), code })
      })

      const data = await res.json()

      if (data.passed) {
        setPassed(true)
        setStatus("success")
        const outputText = (data.output || "") + "\n\n🏆 ¡Reto completado!"
        setOutput(outputText)
        toast.success(`¡Reto completado! +${data.points_earned || 0} pts`)
      } else {
        setStatus("error")
        const outputText = data.output || ""
        setOutput(data.error ? outputText + `\nError: ${data.error}` : outputText)
      }
    } catch (error) {
      setOutput("Error de conexión con el servidor")
      setStatus("error")
    }
  }

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (!challenge) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <h2 className="text-2xl font-bold">Reto no encontrado</h2>
        <Button onClick={() => router.push('/dashboard/challenges')} variant="outline"><ArrowLeft className="h-4 w-4 mr-2" />Volver</Button>
      </div>
    )
  }

  const deadlinePassed = challenge.deadline_passed
  const canShowSolution = deadlinePassed || passed

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <Button variant="ghost" onClick={() => router.push('/dashboard/challenges')} className="mb-2">
        <ArrowLeft className="h-4 w-4 mr-2" />Volver a retos
      </Button>

      <Card className="border-primary/20 neo-shadow">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Target className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">{challenge.title}</CardTitle>
                <p className="text-sm text-muted-foreground">por {challenge.author_name}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {challenge.deadline && (
                <div className={`flex items-center gap-1 text-sm font-bold ${deadlinePassed ? 'text-red-500' : 'text-amber-500'}`}>
                  <Clock className="w-4 h-4" />
                  {deadlinePassed ? 'Fecha límite pasada' : new Date(challenge.deadline).toLocaleDateString()}
                </div>
              )}
              <div className="flex items-center gap-1 text-sm font-bold text-primary">
                <Zap className="w-4 h-4" />
                {challenge.points} pts
              </div>
              <div className="flex items-center gap-1 text-sm font-bold text-amber-500">
                <Trophy className="w-4 h-4" />
                Dificultad: {'⭐'.repeat(challenge.difficulty || 1)}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="prose prose-invert max-w-none">
            <p>{challenge.description}</p>
            {challenge.instructions && (
              <pre className="bg-muted p-4 rounded-lg text-sm font-mono whitespace-pre-wrap mt-4">{challenge.instructions}</pre>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between bg-card border rounded-lg p-2 shadow-sm">
            <span className="text-sm font-semibold text-muted-foreground px-3">solución.py</span>
            <div className="flex items-center gap-2">
              {challenge.user_attempts > 0 && !passed && (
                <span className="text-xs text-muted-foreground">Intentos: {challenge.user_attempts}</span>
              )}
              {passed && <span className="text-green-500 text-sm font-bold flex items-center gap-1"><CheckCircle2 className="w-4 h-4" /> Completado</span>}
              <Button
                size="sm"
                onClick={handleSubmit}
                disabled={status === "running" || passed || deadlinePassed}
                className="bg-green-600 hover:bg-green-700"
              >
                {status === "running" ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                {status === "running" ? "Evaluando..." : passed ? "Completado" : "Enviar Solución"}
              </Button>
            </div>
          </div>

          <div className="flex-1 border rounded-xl overflow-hidden bg-[#282c34] shadow-inner min-h-[400px]">
            <CodeMirror
              value={code}
              height="100%"
              minHeight="400px"
              theme={oneDark}
              extensions={[python()]}
              onChange={(value) => setCode(value)}
              className="text-base"
            />
          </div>
        </div>

        <div className="flex flex-col gap-4">
          {canShowSolution && challenge.solution_code && (
            <Card className="border-amber-500/30 bg-amber-500/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2 text-amber-500">
                  <Eye className="w-4 h-4" />
                  Solución del reto
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="font-mono text-sm whitespace-pre-wrap overflow-x-auto bg-muted p-4 rounded-lg">{challenge.solution_code}</pre>
              </CardContent>
            </Card>
          )}

          {deadlinePassed && !passed && (
            <Card className="border-red-500/30 bg-red-500/5">
              <CardContent className="p-4">
                <p className="text-sm text-red-500 font-bold">La fecha límite de este reto ha pasado. Ya no se pueden enviar soluciones para ganar puntos.</p>
              </CardContent>
            </Card>
          )}

          {deadlinePassed && !challenge.solution_code && challenge.solution_output && (
            <Card className="border-amber-500/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2 text-amber-500">
                  <Eye className="w-4 h-4" />
                  Output esperado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="font-mono text-sm whitespace-pre-wrap bg-muted p-4 rounded-lg">{challenge.solution_output}</pre>
              </CardContent>
            </Card>
          )}

          <div className={`h-48 rounded-xl border-2 flex flex-col overflow-hidden transition-colors ${
            status === 'success' ? 'border-green-500/50 bg-green-500/5' :
            status === 'error' ? 'border-red-500/50 bg-red-500/5' :
            'border-border bg-card'
          }`}>
            <div className="bg-muted/50 border-b px-4 py-2 flex items-center gap-2 text-sm font-bold">
              <Terminal className="w-4 h-4" />
              Terminal de Salida
              {status === 'success' && <span className="ml-auto text-green-500"><CheckCircle2 className="w-4 h-4 inline mr-1" />¡Correcto!</span>}
              {status === 'error' && <span className="ml-auto text-red-500"><XCircle className="w-4 h-4 inline mr-1" />Error</span>}
            </div>
            <div className="p-4 font-mono text-sm overflow-y-auto whitespace-pre-wrap flex-1">
              {output || <span className="text-muted-foreground italic">El resultado de tu código aparecerá aquí...</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}