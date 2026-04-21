import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { jwtVerify } from "jose"

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "your-secret-key-change-in-production"
)

const publicPaths = ["/", "/login", "/register", "/api/auth/login", "/api/auth/register"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow public paths
  if (publicPaths.some(path => pathname === path || pathname.startsWith("/api/auth/"))) {
    // If user is logged in and tries to access login/register, redirect to dashboard
    if (pathname === "/login" || pathname === "/register") {
      const token = request.cookies.get("auth-token")?.value
      if (token) {
        try {
          await jwtVerify(token, JWT_SECRET)
          return NextResponse.redirect(new URL("/dashboard", request.url))
        } catch {
          // Token invalid, allow access to login/register
        }
      }
    }
    return NextResponse.next()
  }

  // Check for auth token on protected routes
  const token = request.cookies.get("auth-token")?.value

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  try {
    const { payload } = await jwtVerify(token, JWT_SECRET)
    
    // Add user info to headers for use in server components
    const response = NextResponse.next()
    response.headers.set("x-user-id", String(payload.userId))
    response.headers.set("x-user-role", String(payload.role))
    
    return response
  } catch {
    // Invalid token, redirect to login
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
