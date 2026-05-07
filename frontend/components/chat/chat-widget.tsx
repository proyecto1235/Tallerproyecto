"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MessageCircle, X, Send, Bot, User, Loader2, ChevronDown } from "lucide-react"

interface Message {
  id: string
  role: "user" | "bot"
  text: string
  timestamp: number
}

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

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([INITIAL_BOT_MESSAGE])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [unread, setUnread] = useState(1)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const hasHydrated = useRef(false)

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

  useEffect(() => {
    if (hasHydrated.current && messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
    }
  }, [messages])

  useEffect(() => {
    if (isOpen) {
      setUnread(0)
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [isOpen, messages])

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
      const botText = data.message || data.response || "Lo siento, no pude procesar tu mensaje."

      const botMsg: Message = {
        id: generateId(),
        role: "bot",
        text: botText,
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, botMsg])
    } catch {
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

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 transition-all duration-300 hover:scale-110 active:scale-95"
        aria-label="Abrir chat"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <>
            <MessageCircle className="h-6 w-6" />
            {unread > 0 && (
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
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-semibold">Asistente RoboLearn</p>
              <p className="text-[10px] text-muted-foreground">Online · Respondo al instante</p>
            </div>
          </div>
          <button
            onClick={clearChat}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted transition-colors"
            title="Limpiar chat"
          >
            <ChevronDown className="h-4 w-4 rotate-180" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ height: "400px" }}>
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`flex gap-2 max-w-[85%] ${
                  msg.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full mt-1 ${
                    msg.role === "user" ? "bg-primary/10" : "bg-secondary/10"
                  }`}
                >
                  {msg.role === "user" ? (
                    <User className="h-3.5 w-3.5 text-primary" />
                  ) : (
                    <Bot className="h-3.5 w-3.5 text-secondary" />
                  )}
                </div>
                <div
                  className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-md"
                      : "bg-muted text-foreground rounded-tl-md"
                  }`}
                >
                  {msg.text}
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
              placeholder="Escribe tu mensaje..."
              disabled={isLoading}
              className="flex-1 rounded-xl border-border bg-muted/50 text-sm"
            />
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim() || isLoading}
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