"use client"

import { useState, useEffect, useCallback } from "react"
import { toast } from "sonner"

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

// Remove trailing slash if present
const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/$/, "")

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

/**
 * Fallback de usuario para cuando el backend está offline
 */
const MOCK_USER: User = {
  id: 1,
  email: "estudiante@robolearn.com",
  fullName: "Estudiante Piloto",
  role: "student",
  points: 1500,
  streakDays: 5,
}

import { clearAuthCookies } from "@/app/actions/auth"

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  })

  const checkSession = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/users/profile`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })
      
      // Manejo de expiración o sesión inválida
      if (res.status === 401 || res.status === 404) {
        localStorage.removeItem("mock_session")
        try { await clearAuthCookies() } catch (e) {}
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
        })
        // Usamos window.location.href para forzar recarga y limpiar todos los estados locales
        // No redirigir si estamos en login o register (rutas públicas)
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
      // Usamos console.info en lugar de warn/error con el objeto de error 
      // para evitar que Next.js lo muestre como un stack trace rojo en la terminal.
      console.info("Info: Backend inactivo. Activando fallback de sesión local.")
      
      // Fallback: Verificar si hay una sesión mockeada guardada
      const mockSession = localStorage.getItem("mock_session")
      if (mockSession) {
        setState({
          user: JSON.parse(mockSession),
          isLoading: false,
          isAuthenticated: true,
        })
      } else {
        localStorage.removeItem("mock_session")
        try { await clearAuthCookies() } catch (e) {}
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
        })
        // No redirigir en rutas públicas (login, register) o en dashboard
        if (window.location.pathname.startsWith('/dashboard')) {
            window.location.href = '/login'
        }
      }
    }
  }, [])

  useEffect(() => {
    checkSession()
    // Solo ejecutar una vez al montar
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = async (email: string, password: string) => {
    try {
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

      const userData = mapBackendUserToFrontend(data.user || data)
      
      setState({
        user: userData,
        isLoading: false,
        isAuthenticated: true,
      })
      
      await new Promise(resolve => setTimeout(resolve, 100))
      
      window.location.href = "/dashboard"
      return data
    } catch (error: any) {
      // Si el error parece ser de red (TypeError, o contiene "fetch" o "NetworkError"), usamos el fallback
      const isNetworkError = error instanceof TypeError || 
                             (error.message && (error.message.toLowerCase().includes("fetch") || error.message.includes("NetworkError")));
                             
      if (!isNetworkError) {
        throw error;
      }
      
      console.warn("Backend inactivo, usando fallback local de Login.")
      
      const fallbackUser = { ...MOCK_USER, email }
      localStorage.setItem("mock_session", JSON.stringify(fallbackUser))
      
      setState({
        user: fallbackUser,
        isLoading: false,
        isAuthenticated: true,
      })
      
      window.location.href = "/dashboard"
      return { user: fallbackUser }
    }
  }

  const register = async (
    email: string,
    password: string,
    fullName: string,
    requestTeacher: boolean = false
  ) => {
    try {
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

      const userData = mapBackendUserToFrontend(data.user || data)
      
      setState({
        user: userData,
        isLoading: false,
        isAuthenticated: true,
      })
      
      await new Promise(resolve => setTimeout(resolve, 100))
      
      window.location.href = "/dashboard"
      return data
    } catch (error: any) {
      const isNetworkError = error instanceof TypeError || 
                             (error.message && (error.message.toLowerCase().includes("fetch") || error.message.includes("NetworkError")));
                             
      if (!isNetworkError) {
        throw error;
      }
      
      console.warn("Backend inactivo, usando fallback local de Registro.")
      
      const fallbackUser = { ...MOCK_USER, email, fullName, role: requestTeacher ? "teacher" : "student" } as User
      localStorage.setItem("mock_session", JSON.stringify(fallbackUser))
      
      setState({
        user: fallbackUser,
        isLoading: false,
        isAuthenticated: true,
      })
      
      window.location.href = "/dashboard"
      return { user: fallbackUser }
    }
  }

  const logout = () => {
    // Redirigir a la página de logout intermedia que se encarga
    // de mostrar "Saliendo..." y realizar la limpieza de forma segura.
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
