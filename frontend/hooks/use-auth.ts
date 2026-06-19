"use client"

import { useState, useEffect } from "react"
import API from "@/lib/api"

export interface User {
  id: number
  email: string
  fullName: string
  role: "student" | "teacher" | "admin"
  points?: number
  streakDays?: number
  avatarUrl?: string | null
  publicId?: string | null
  teacherRequestStatus?: string | null
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

function mapBackendUserToFrontend(backendData: any): User {
  return {
    id: backendData.id || 0,
    email: backendData.email || "",
    fullName: backendData.full_name || backendData.fullName || "Usuario",
    role: (backendData.role || "student") as "student" | "teacher" | "admin",
    points: backendData.points || 0,
    streakDays: backendData.streak_days || backendData.streakDays || 0,
    avatarUrl: backendData.avatar_url || backendData.avatarUrl || null,
    publicId: backendData.public_id || backendData.publicId || null,
    teacherRequestStatus: backendData.teacher_request_status || backendData.teacherRequestStatus || null,
  }
}

import { clearAuthCookies } from "@/app/actions/auth"

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  })

  const checkSession = async () => {
    try {
      const res = await fetch(`${API}/users/profile`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })

      if (res.status === 401 || res.status === 404) {
        try { await clearAuthCookies() } catch (e) {}
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
        })
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
            window.location.href = '/login'
        }
        return
      }

      if (!res.ok) {
        throw new Error("Respuesta no OK del backend")
      }

      const data = await res.json()
      const userData = data.user || data

      setState({
        user: mapBackendUserToFrontend(userData),
        isLoading: false,
        isAuthenticated: true,
      })
    } catch (error) {
      console.info("Backend inactivo. No se puede verificar la sesión.")
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      })
    }
  }

  useEffect(() => { checkSession() }, [])

  const login = async (email: string, password: string) => {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.error || data.detail || "Error al iniciar sesión")
    }

    const userData = mapBackendUserToFrontend(data.user || data)

    setState({
      user: userData,
      isLoading: false,
      isAuthenticated: true,
    })

    await new Promise(resolve => setTimeout(resolve, 100))

    window.location.href = "/dashboard"
    return data
  }

  const register = async (
    email: string,
    password: string,
    fullName: string,
    requestTeacher: boolean = false
  ) => {
    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password, full_name: fullName, request_teacher: requestTeacher }),
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.error || data.detail || "Error al crear la cuenta")
    }

    const userData = mapBackendUserToFrontend(data.user || data)

    setState({
      user: userData,
      isLoading: false,
      isAuthenticated: true,
    })

    await new Promise(resolve => setTimeout(resolve, 100))

    window.location.href = "/dashboard"
    return data
  }

  const logout = () => {
    window.location.href = "/logout"
  }

  return {
    ...state,
    login,
    register,
    logout,
    refresh: checkSession,
  }
}
