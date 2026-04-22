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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  })
  const router = useRouter()

  const checkSession = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/users/profile`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })
      
      const data = await res.json()
      
      setState({
        user: res.ok ? data.user : null,
        isLoading: false,
        isAuthenticated: res.ok,
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
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
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
    const res = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password, full_name: fullName, request_teacher: requestTeacher }),
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
    await fetch(`${API_URL}/auth/logout`, { 
      method: "POST",
      credentials: "include",
    })
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
