"use client"

import { useState, useRef, useEffect } from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageCircle, X, Send, Bot, User, Brain, Loader2, ChevronDown, AlertTriangle, WifiOff } from "lucide-react"
import { toast } from "sonner"

interface Message {
  id: string
  role: "user" | "bot"
  text: string
  timestamp: number
  source?: string
}

type ServiceState = "checking" | "available" | "dialogflow_only" | "ollama_only" | "none"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"
const STORAGE_KEY = "robolearn_chat_history"
const SESSION_KEY = "robolearn_chat_session"

function getSessionId(): string {
  let session = localStorage.getItem(SESSION_KEY)
  if (!session) {
    session = "anon_" + Math.random().toString(36).substring(2, 15)
    localStorage.setItem(SESSION_KEY, session)
  }
  return session
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 7)
}

const INITIAL_BOT_MESSAGE: Message = {
  id: "welcome",
  role: "bot",
  text: "¡Hola! Soy el asistente de RoboLearn. Puedo ayudarte con:\n\n• Dudas sobre los módulos de Python\n• Explicar conceptos de programación\n• Ayudarte con ejercicios\n• Recomendarte qué estudiar\n\n¿En qué puedo ayudarte?",
  timestamp: Date.now()
}

function serviceStateLabel(state: ServiceState): string {
  switch (state) {
    case "dialogflow_only": return "solo dialogflow esta disponible"
    case "ollama_only": return "solo IA local disponible"
    case "none": return "ningun servicio de IA disponible"
    default: return ""
  }
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([INITIAL_BOT_MESSAGE])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [unread, setUnread] = useState(1)
  const [connectionError, setConnectionError] = useState(false)
  const [serviceState, setServiceState] = useState<ServiceState>("checking")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const hasHydrated = useRef(false)
  const checkedStatus = useRef(false)

  useEffect(() => {
    if (hasHydrated.current) return
    hasHydrated.current = true
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed)
          setUnread(0)
          return
        }
      }
    } catch {}
    setMessages([INITIAL_BOT_MESSAGE])
  }, [])

  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    if (hasHydrated.current && messages.length > 0) {
      clearTimeout(saveTimerRef.current)
      saveTimerRef.current = setTimeout(() => {
        const trimmed = messages.length > 50 ? messages.slice(-50) : messages
        localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
      }, 500)
    }
  }, [messages])

  // Open/close behavior — runs only when isOpen toggles
  useEffect(() => {
    if (!isOpen) return
    setUnread(0)
    setConnectionError(false)
    setTimeout(() => inputRef.current?.focus(), 300)
    checkServiceStatus()
  }, [isOpen])

  // Scroll on new messages only — runs when message count changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages.length])

  const checkServiceStatus = async () => {
    if (checkedStatus.current) return
    checkedStatus.current = true
    try {
      const res = await fetch(`${API_URL}/chatbot/status`)
      if (!res.ok) throw new Error("Status check failed")
      const data = await res.json()
      setServiceState(data.best_available || "none")
    } catch {
      setServiceState("none")
    }
  }

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || isLoading) return

    const userMsg: Message = {
      id: generateId(),
      role: "user",
      text,
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMsg])
    setInput("")
    setIsLoading(true)

    const sessionId = getSessionId()

    try {
      const res = await fetch(`${API_URL}/chatbot/public`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          history: messages.slice(-6).map(m => ({ role: m.role, text: m.text }))
        })
      })

      const data = await res.json()
      const source = data.source || "tutor"
      const botText = data.message || data.response || "Lo siento, no pude procesar tu mensaje."

      const botMsg: Message = {
        id: generateId(),
        role: "bot",
        text: botText,
        timestamp: Date.now(),
        source,
      }
      setMessages(prev => [...prev, botMsg])
    } catch {
      setConnectionError(true)
      toast.error("Error de conexión", {
        description: "No se pudo conectar con el servidor. Verifica que el backend esté funcionando.",
        duration: 5000,
      })
      const botMsg: Message = {
        id: generateId(),
        role: "bot",
        text: "⚠️ No pude conectar con el servidor. Verifica que el backend esté corriendo o intenta más tarde.",
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, botMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    localStorage.removeItem(STORAGE_KEY)
    setMessages([INITIAL_BOT_MESSAGE])
    setUnread(1)
    setIsOpen(false)
  }

  const isDisabled = serviceState === "none"
  const showDegradedBanner = serviceState === "dialogflow_only" || serviceState === "ollama_only"

  const buttonStyle = connectionError
    ? "bg-destructive text-destructive-foreground animate-pulse"
    : isDisabled && !connectionError
    ? "bg-muted-foreground/50 text-muted cursor-not-allowed"
    : showDegradedBanner
    ? "bg-amber-500 text-white"
    : "bg-primary text-primary-foreground hover:bg-primary/90"

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => !isDisabled && setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-all duration-300 hover:scale-110 active:scale-95 ${buttonStyle}`}
        aria-label="Abrir chat"
        title={isDisabled ? "Servicio de IA no disponible" : "Abrir chat"}
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <>
            <MessageCircle className="h-6 w-6" />
            {connectionError && (
              <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-foreground text-[10px] font-bold text-background animate-pulse">
                !
              </span>
            )}
            {isDisabled && !connectionError && (
              <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground">
                <WifiOff className="h-3 w-3" />
              </span>
            )}
            {showDegradedBanner && !connectionError && !isDisabled && (
              <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-amber-700 text-[10px] font-bold text-white">
                !
              </span>
            )}
            {unread > 0 && !connectionError && !showDegradedBanner && !isDisabled && (
              <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground animate-pulse">
                {unread}
              </span>
            )}
          </>
        )}
      </button>

      {/* Chat Panel */}
      <div
        className={`fixed bottom-24 right-6 z-50 w-[380px] max-w-[calc(100vw-2rem)] rounded-2xl border border-border bg-card shadow-2xl transition-all duration-300 origin-bottom-right ${
          isOpen ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        }`}
        style={{ maxHeight: "min(600px, calc(100vh - 8rem))" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between rounded-t-2xl border-b border-border bg-primary/5 px-4 py-3">
          <div className="flex items-center gap-3">
            <Image src="/logo.svg" alt="RoboLearn" width={90} height={22} />
          </div>
          <button
            onClick={clearChat}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted transition-colors"
            title="Limpiar chat"
          >
            <ChevronDown className="h-4 w-4 rotate-180" />
          </button>
        </div>

        {/* Service degraded banner */}
        {showDegradedBanner && (
          <div className="flex items-center gap-2 bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-xs text-amber-600">
            <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
            <span>{serviceStateLabel(serviceState)}</span>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ height: showDegradedBanner ? "376px" : "400px" }}>
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`flex gap-2 max-w-[85%] ${
                  msg.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full mt-1 ${
                    msg.role === "user" ? "bg-primary/10"
                    : msg.source === "ollama" ? "bg-purple-500/10"
                    : msg.source === "dialogflow" ? "bg-blue-500/10"
                    : msg.source === "ai_unavailable" ? "bg-amber-500/10"
                    : "bg-secondary/10"
                  }`}
                >
                  {msg.role === "user" ? (
                    <User className="h-3.5 w-3.5 text-primary" />
                  ) : msg.source === "ollama" ? (
                    <Brain className="h-3.5 w-3.5 text-purple-500" />
                  ) : msg.source === "dialogflow" ? (
                    <Bot className="h-3.5 w-3.5 text-blue-500" />
                  ) : msg.source === "ai_unavailable" ? (
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                  ) : (
                    <Bot className="h-3.5 w-3.5 text-secondary" />
                  )}
                </div>
                <div
                  className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-md"
                      : msg.source === "ollama"
                      ? "bg-purple-500/10 text-foreground border border-purple-500/20 rounded-tl-md"
                      : msg.source === "dialogflow"
                      ? "bg-blue-500/10 text-foreground border border-blue-500/20 rounded-tl-md"
                      : msg.source === "ai_unavailable"
                      ? "bg-amber-500/10 text-foreground border border-amber-500/20 rounded-tl-md"
                      : "bg-muted text-foreground rounded-tl-md"
                  }`}
                >
                  {msg.source === "ollama" && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-purple-500 mb-1.5 uppercase tracking-wide">
                      <Brain className="h-3 w-3" />
                      IA Local
                    </span>
                  )}
                  {msg.source === "dialogflow" && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-500 mb-1.5 uppercase tracking-wide">
                      <Bot className="h-3 w-3" />
                      Dialogflow
                    </span>
                  )}
                  {msg.source === "ai_unavailable" && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-500 mb-1.5 uppercase tracking-wide">
                      <AlertTriangle className="h-3 w-3" />
                      IA no disponible
                    </span>
                  )}
                  <div>{msg.text}</div>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-2 max-w-[85%]">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-secondary/10 mt-1">
                  <Bot className="h-3.5 w-3.5 text-secondary" />
                </div>
                <div className="rounded-2xl rounded-tl-md bg-muted px-4 py-3">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border p-3">
          <form
            onSubmit={e => { e.preventDefault(); sendMessage() }}
            className="flex items-center gap-2"
          >
            <Input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isDisabled ? "Servicio no disponible" : "Escribe tu mensaje..."}
              disabled={isLoading || isDisabled}
              className="flex-1 rounded-xl border-border bg-muted/50 text-sm"
            />
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim() || isLoading || isDisabled}
              className="h-10 w-10 shrink-0 rounded-xl"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </>
  )
}
