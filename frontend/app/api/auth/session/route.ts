import { NextResponse } from "next/server"
import { getSession, getCurrentUser } from "@/lib/auth"

export async function GET() {
  try {
    const session = await getSession()
    
    if (!session) {
      return NextResponse.json({ authenticated: false })
    }

    const user = await getCurrentUser()
    
    if (!user) {
      return NextResponse.json({ authenticated: false })
    }

    return NextResponse.json({
      authenticated: true,
      user: {
        id: user.id,
        email: user.email,
        fullName: user.full_name,
        role: user.role,
        points: user.points,
        streakDays: user.streak_days,
        avatarUrl: user.avatar_url,
      },
    })
  } catch (error) {
    console.error("Session API error:", error)
    return NextResponse.json({ authenticated: false })
  }
}
