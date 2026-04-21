"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"

export interface User {
  id: number
  email: string
  fullName: string
  role: "student" | "teacher" | "admin"
  points: number
  streakDays: number
  avatarUrl: string | null
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  })
  const router = useRouter()

  const checkSession = useCallback(async () => {
    try {
      const res = await fetch("/api/auth/session")
      const data = await res.json()
      
      setState({
        user: data.authenticated ? data.user : null,
        isLoading: false,
        isAuthenticated: data.authenticated,
      })
    } catch {
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      })
    }
  }, [])

  useEffect(() => {
    checkSession()
  }, [checkSession])

  const login = async (email: string, password: string) => {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      throw new Error(data.error || "Error al iniciar sesión")
    }

    setState({
      user: data.user,
      isLoading: false,
      isAuthenticated: true,
    })
    
    router.push("/dashboard")
    return data
  }

  const register = async (
    email: string,
    password: string,
    fullName: string,
    requestTeacher: boolean = false
  ) => {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, fullName, requestTeacher }),
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      throw new Error(data.error || "Error al crear la cuenta")
    }

    setState({
      user: data.user,
      isLoading: false,
      isAuthenticated: true,
    })
    
    router.push("/dashboard")
    return data
  }

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST" })
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
    })
    router.push("/login")
  }

  return {
    ...state,
    login,
    register,
    logout,
    refresh: checkSession,
  }
}
