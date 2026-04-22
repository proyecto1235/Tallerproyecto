import { Pool } from "pg"
import { MongoClient, Db } from "mongodb"

// ============================================
// PostgreSQL Configuration (Main Database)
// ============================================
// Environment variables needed:
// - POSTGRES_HOST (default: localhost)
// - POSTGRES_PORT (default: 5432)
// - POSTGRES_DB (default: robolearn)
  // - POSTGRES_USER (default: postgres)
  // - POSTGRES_PASSWORD (required)

const pgPool = new Pool({
  host: process.env.POSTGRES_HOST || "localhost",
  port: parseInt(process.env.POSTGRES_PORT || "5432"),
  database: process.env.POSTGRES_DB || "robolearn",
  user: process.env.POSTGRES_USER || "postgres",
  password: process.env.POSTGRES_PASSWORD,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

export async function query<T>(text: string, params?: unknown[]): Promise<T[]> {
  const client = await pgPool.connect()
  try {
    const result = await client.query(text, params)
    return result.rows as T[]
  } finally {
    client.release()
  }
}

export async function queryOne<T>(text: string, params?: unknown[]): Promise<T | null> {
  const rows = await query<T>(text, params)
  return rows[0] || null
}

export async function execute(text: string, params?: unknown[]): Promise<number> {
  const client = await pgPool.connect()
  try {
    const result = await client.query(text, params)
    return result.rowCount || 0
  } finally {
    client.release()
  }
}

// ============================================
// MongoDB Configuration (Metrics Database)
// ============================================
// Environment variables needed:
// - MONGODB_URI (default: mongodb://localhost:27017)
// - MONGODB_DB (default: robolearn_metrics)

let mongoClient: MongoClient | null = null
let mongoDb: Db | null = null

export async function getMongoDb(): Promise<Db> {
  if (mongoDb) return mongoDb

  const uri = process.env.MONGODB_URI || "mongodb://localhost:27017"
  const dbName = process.env.MONGODB_DB || "robolearn_metrics"

  mongoClient = new MongoClient(uri)
  await mongoClient.connect()
  mongoDb = mongoClient.db(dbName)

  return mongoDb
}

// Metrics helper functions
export async function logMetric(collection: string, data: Record<string, unknown>) {
  const db = await getMongoDb()
  await db.collection(collection).insertOne({
    ...data,
    timestamp: new Date(),
  })
}

export async function getMetrics(collection: string, filter: Record<string, unknown> = {}) {
  const db = await getMongoDb()
  return db.collection(collection).find(filter).toArray()
}

// ============================================
// Type Definitions
// ============================================

export type UserRole = "student" | "teacher" | "admin"
export type TeacherRequestStatus = "pending" | "approved" | "rejected"
export type ContentStatus = "draft" | "pending_review" | "approved" | "rejected"
export type EnrollmentStatus = "pending" | "approved" | "rejected" | "withdrawn"

export interface User {
  id: number
  email: string
  password_hash: string
  full_name: string
  role: UserRole
  avatar_url: string | null
  points: number
  streak_days: number
  last_activity_date: string | null
  created_at: string
  updated_at: string
}

export interface Module {
  id: number
  title: string
  description: string | null
  difficulty_level: number
  order_index: number
  parent_module_id: number | null
  icon: string | null
  created_by: number | null
  status: ContentStatus
  created_at: string
  updated_at: string
}

export interface Lesson {
  id: number
  module_id: number
  title: string
  content: string | null
  order_index: number
  estimated_minutes: number
  status: ContentStatus
  created_by: number | null
  created_at: string
  updated_at: string
}

export interface Exercise {
  id: number
  lesson_id: number
  title: string
  description: string | null
  initial_code: string | null
  expected_output: string | null
  test_cases: unknown
  hints: unknown
  points: number
  difficulty: number
  order_index: number
  status: ContentStatus
  created_by: number | null
  ai_generated: boolean
  created_at: string
}

export interface Class {
  id: number
  teacher_id: number
  name: string
  description: string | null
  code: string
  is_active: boolean
  max_students: number
  created_at: string
  updated_at: string
}

export interface Achievement {
  id: number
  name: string
  description: string | null
  icon: string | null
  points: number
  criteria: unknown
}

export interface UserAchievement {
  id: number
  user_id: number
  achievement_id: number
  earned_at: string
}

export interface AIAlert {
  id: number
  teacher_id: number
  student_id: number
  alert_type: string
  message: string
  topic: string | null
  is_read: boolean
  created_at: string
}
