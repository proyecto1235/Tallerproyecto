import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { jwtVerify } from "jose"

const JWT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET || process.env.SECRET_KEY || "")

const publicPaths = ["/", "/login", "/register"]

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (publicPaths.some(path => pathname === path)) {
    if (pathname === "/login" || pathname === "/register") {
      const token = request.cookies.get("auth-token")?.value
      if (token && JWT_SECRET) {
        try {
          await jwtVerify(token, JWT_SECRET)
          return NextResponse.redirect(new URL("/dashboard", request.url))
        } catch {}
      }
    }
    return NextResponse.next()
  }

  if (!JWT_SECRET) return NextResponse.redirect(new URL("/login", request.url))

  const token = request.cookies.get("auth-token")?.value
  if (!token) return NextResponse.redirect(new URL("/login", request.url))

  try {
    const { payload } = await jwtVerify(token, JWT_SECRET)
    const response = NextResponse.next()
    response.headers.set("x-user-id", String(payload.userId))
    response.headers.set("x-user-role", String(payload.role))
    return response
  } catch {
    const response = NextResponse.redirect(new URL("/login", request.url))
    response.cookies.delete("auth-token")
    return response
  }
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
