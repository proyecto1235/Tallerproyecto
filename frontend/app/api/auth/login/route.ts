import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { loginUser } from "@/lib/auth"

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json()

    if (!email || !password) {
      return NextResponse.json(
        { error: "Email y contraseña son requeridos" },
        { status: 400 }
      )
    }

    const result = await loginUser(email, password)

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 401 }
      )
    }

    // Set HTTP-only cookie
    const cookieStore = await cookies()
    cookieStore.set("auth-token", result.token!, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
    })

    return NextResponse.json({
      success: true,
      user: {
        id: result.user!.id,
        email: result.user!.email,
        fullName: result.user!.full_name,
        role: result.user!.role,
        points: result.user!.points,
        streakDays: result.user!.streak_days,
      },
    })
  } catch (error) {
    console.error("Login API error:", error)
    return NextResponse.json(
      { error: "Error del servidor" },
      { status: 500 }
    )
  }
}
