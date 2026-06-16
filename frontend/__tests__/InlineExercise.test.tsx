import { describe, it, expect, vi, beforeEach } from "vitest"

const mockFetch = vi.fn()
global.fetch = mockFetch

describe("InlineExercise", () => {
  const mockExercise = {
    id: 1,
    title: "Suma de dos números",
    instructions: "# Suma dos números\nprint(1 + 2)",
    module_id: 1,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("should fetch exercise submission and return success", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        passed: true,
        output: "3",
        points_earned: 10,
      }),
    })

    const response = await fetch("http://localhost:8000/api/exercises/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        exercise_id: mockExercise.id,
        code: "print(1 + 2)",
        module_id: 1,
        is_class_exercise: false,
        class_module_id: 0,
      }),
    })

    const data = await response.json()
    expect(data.passed).toBe(true)
    expect(data.output).toBe("3")
    expect(data.points_earned).toBe(10)
  })

  it("should handle exercise failure with attempts count", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        passed: false,
        output: "SyntaxError: invalid syntax",
        attempts: 2,
        can_view_solution: true,
        solution: "print(1+2)",
      }),
    })

    const response = await fetch("http://localhost:8000/api/exercises/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        exercise_id: mockExercise.id,
        code: "print 1+2",
        module_id: 1,
        is_class_exercise: false,
        class_module_id: 0,
      }),
    })

    const data = await response.json()
    expect(data.passed).toBe(false)
    expect(data.attempts).toBe(2)
    expect(data.can_view_solution).toBe(true)
    expect(data.solution).toBeDefined()
  })

  it("should handle network errors gracefully", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network Error"))

    try {
      await fetch("http://localhost:8000/api/exercises/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          exercise_id: mockExercise.id,
          code: "print(1)",
          module_id: 1,
          is_class_exercise: false,
          class_module_id: 0,
        }),
      })
    } catch (error: any) {
      expect(error.message).toBe("Network Error")
    }
  })

  it("should reject empty code submission", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: async () => ({ detail: "Code cannot be empty" }),
    })

    const response = await fetch("http://localhost:8000/api/exercises/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        exercise_id: mockExercise.id,
        code: "",
        module_id: 1,
        is_class_exercise: false,
        class_module_id: 0,
      }),
    })

    expect(response.status).toBe(422)
  })
})
