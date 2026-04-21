import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { registerUser, createToken } from "@/lib/auth"

export async function POST(request: Request) {
  try {
    const { email, password, fullName, requestTeacher } = await request.json()

    if (!email || !password || !fullName) {
      return NextResponse.json(
        { error: "Todos los campos son requeridos" },
        { status: 400 }
      )
    }

    if (password.length < 6) {
      return NextResponse.json(
        { error: "La contraseña debe tener al menos 6 caracteres" },
        { status: 400 }
      )
    }

    const result = await registerUser(email, password, fullName, requestTeacher)

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      )
    }

    // Create token and set cookie
    const token = await createToken({
      userId: result.user!.id,
      email: result.user!.email,
      role: result.user!.role,
      fullName: result.user!.full_name,
    })

    const cookieStore = await cookies()
    cookieStore.set("auth-token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7,
      path: "/",
    })

    return NextResponse.json({
      success: true,
      user: {
        id: result.user!.id,
        email: result.user!.email,
        fullName: result.user!.full_name,
        role: result.user!.role,
      },
      teacherRequestPending: requestTeacher,
    })
  } catch (error) {
    console.error("Register API error:", error)
    return NextResponse.json(
      { error: "Error del servidor" },
      { status: 500 }
    )
  }
}
