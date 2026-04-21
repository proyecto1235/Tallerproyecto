import { NextResponse } from "next/server"
import { cookies } from "next/headers"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export async function GET() {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get("auth-token")?.value

    if (!token) {
      return NextResponse.json({ authenticated: false })
    }

    // Call backend API to get user profile
    const response = await fetch(`${API_URL}/users/profile`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      return NextResponse.json({ authenticated: false })
    }

    const data = await response.json()

    return NextResponse.json({
      authenticated: true,
      user: data.user,
    })
  } catch (error) {
    console.error("Session API error:", error)
    return NextResponse.json({ authenticated: false })
  }
}
