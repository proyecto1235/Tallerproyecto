"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"

export interface User {
  id: number
  email: string
  fullName: string
  role: "student" | "teacher" | "admin"
  points?: number
  streakDays?: number
  avatarUrl?: string | null
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

/**
 * Mapea los datos del backend al formato del frontend
 */
function mapBackendUserToFrontend(backendData: any): User {
  return {
    id: backendData.id || 0,
    email: backendData.email || "",
    fullName: backendData.full_name || backendData.fullName || "Usuario",
    role: (backendData.role || "student") as "student" | "teacher" | "admin",
    points: backendData.points || 0,
    streakDays: backendData.streak_days || backendData.streakDays || 0,
    avatarUrl: backendData.avatar_url || backendData.avatarUrl || null,
  }
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
      const res = await fetch(`${API_URL}/users/profile`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })
      
      if (!res.ok) {
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
        })
        return
      }

      const data = await res.json()
      const userData = data.user || data
      
      setState({
        user: mapBackendUserToFrontend(userData),
        isLoading: false,
        isAuthenticated: true,
      })
    } catch (error) {
      console.error("Session check error:", error)
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      })
    }
  }, [])

  useEffect(() => {
    checkSession()
    // Solo ejecutar una vez al montar
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      throw new Error(data.error || data.detail || "Error al iniciar sesión")
    }

    // Mapear datos del usuario
    const userData = mapBackendUserToFrontend(data.user || data)
    
    setState({
      user: userData,
      isLoading: false,
      isAuthenticated: true,
    })
    
    // Pequeño delay para asegurar que la cookie está guardada
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Redirigir a dashboard
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
      throw new Error(data.error || data.detail || "Error al crear la cuenta")
    }

    // Mapear datos del usuario
    const userData = mapBackendUserToFrontend(data.user || data)
    
    setState({
      user: userData,
      isLoading: false,
      isAuthenticated: true,
    })
    
    // Pequeño delay para asegurar que la cookie está guardada
    await new Promise(resolve => setTimeout(resolve, 100))
    
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
