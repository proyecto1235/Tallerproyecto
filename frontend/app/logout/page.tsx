"use client"

import { useEffect } from "react"
import { Loader2, Code } from "lucide-react"
import { clearAuthCookies } from "@/app/actions/auth"

export default function LogoutPage() {
  useEffect(() => {
    let mounted = true;

    async function doLogout() {
      // 1. Limpiar local storage
      localStorage.removeItem("mock_session")
      
      // 2. Limpiar cookie segura mediante Server Action
      try {
        await clearAuthCookies()
      } catch (e) {
        console.warn("No se pudo limpiar la cookie del servidor", e)
      }

      // 3. Opcional: Llamar al endpoint de logout del backend si es necesario
      try {
        const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/$/, "")
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 1000)
        await fetch(`${API_URL}/auth/logout`, { 
          method: "POST",
          credentials: "include",
          signal: controller.signal
        })
        clearTimeout(timeoutId)
      } catch (error) {
        console.info("Backend inactivo durante logout.")
      }

      // 4. Redirigir a login después de un pequeño retraso para asegurar que la UI se renderice
      if (mounted) {
        setTimeout(() => {
          window.location.href = "/login"
        }, 500)
      }
    }

    doLogout()

    return () => {
      mounted = false;
    }
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <div className="flex flex-col items-center gap-6">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary shadow-lg">
          <Code className="h-10 w-10 text-primary-foreground" />
        </div>
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <h2 className="text-2xl font-bold text-foreground">Saliendo...</h2>
          <p className="text-muted-foreground">Cerrando sesión de forma segura</p>
        </div>
      </div>
    </div>
  )
}
