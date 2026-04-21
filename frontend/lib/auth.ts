import { SignJWT, jwtVerify } from "jose"
import { cookies } from "next/headers"
import { query, queryOne, execute, type User, type UserRole } from "./db"
import bcrypt from "bcryptjs"

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "your-secret-key-change-in-production"
)

export interface JWTPayload {
  userId: number
  email: string
  role: UserRole
  fullName: string
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export async function createToken(payload: JWTPayload): Promise<string> {
  return new SignJWT({ ...payload })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(JWT_SECRET)
}

export async function verifyToken(token: string): Promise<JWTPayload | null> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET)
    return payload as unknown as JWTPayload
  } catch {
    return null
  }
}

export async function getSession(): Promise<JWTPayload | null> {
  const cookieStore = await cookies()
  const token = cookieStore.get("auth-token")?.value
  
  if (!token) return null
  
  return verifyToken(token)
}

export async function getCurrentUser(): Promise<User | null> {
  const session = await getSession()
  if (!session) return null
  
  return queryOne<User>("SELECT * FROM users WHERE id = $1", [session.userId])
}

export async function registerUser(
  email: string,
  password: string,
  fullName: string,
  requestTeacher: boolean = false
): Promise<{ success: boolean; error?: string; user?: User }> {
  try {
    // Check if user exists
    const existing = await queryOne<{ id: number }>(
      "SELECT id FROM users WHERE email = $1",
      [email]
    )
    if (existing) {
      return { success: false, error: "El correo ya está registrado" }
    }

    const passwordHash = await hashPassword(password)
    
    const users = await query<User>(
      `INSERT INTO users (email, password_hash, full_name, role)
       VALUES ($1, $2, $3, 'student')
       RETURNING *`,
      [email, passwordHash, fullName]
    )
    
    const user = users[0]

    // If requesting teacher role, create a request
    if (requestTeacher) {
      await execute(
        `INSERT INTO teacher_requests (user_id, reason)
         VALUES ($1, 'Solicitud durante registro')`,
        [user.id]
      )
    }

    return { success: true, user }
  } catch (error) {
    console.error("Register error:", error)
    return { success: false, error: "Error al crear la cuenta" }
  }
}

export async function loginUser(
  email: string,
  password: string
): Promise<{ success: boolean; error?: string; token?: string; user?: User }> {
  try {
    const user = await queryOne<User>(
      "SELECT * FROM users WHERE email = $1",
      [email]
    )
    
    if (!user) {
      return { success: false, error: "Credenciales incorrectas" }
    }

    const validPassword = await verifyPassword(password, user.password_hash)
    
    if (!validPassword) {
      return { success: false, error: "Credenciales incorrectas" }
    }

    // Update last activity
    await execute(
      `UPDATE users 
       SET last_activity_date = CURRENT_DATE, updated_at = CURRENT_TIMESTAMP 
       WHERE id = $1`,
      [user.id]
    )

    const token = await createToken({
      userId: user.id,
      email: user.email,
      role: user.role,
      fullName: user.full_name,
    })

    return { success: true, token, user }
  } catch (error) {
    console.error("Login error:", error)
    return { success: false, error: "Error al iniciar sesión" }
  }
}
