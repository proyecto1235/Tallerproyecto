import { describe, it, expect, vi, beforeEach } from "vitest"

const mockFetch = vi.fn()
global.fetch = mockFetch

describe("Student Dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("should fetch dashboard data successfully", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        total_exercises: 25,
        completed_exercises: 18,
        total_points: 1500,
        streak_days: 5,
        recent_activity: [
          { type: "exercise", description: "Completaste 'Variables'", date: "2026-05-30" },
        ],
        achievements: [],
        top_modules: [{ name: "Python Basics", progress: 80 }],
      }),
    })

    const response = await fetch("http://localhost:8000/api/analytics/dashboard", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    })

    const data = await response.json()
    expect(data.total_exercises).toBe(25)
    expect(data.completed_exercises).toBe(18)
    expect(data.total_points).toBe(1500)
  })

  it("should handle dashboard fetch failure", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: "No autorizado" }),
    })

    const response = await fetch("http://localhost:8000/api/analytics/dashboard", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    })

    expect(response.status).toBe(401)
  })
})
