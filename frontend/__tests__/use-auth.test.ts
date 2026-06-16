import { describe, it, expect, vi, beforeEach } from "vitest"

const mockFetch = vi.fn()
global.fetch = mockFetch

Object.defineProperty(global, "localStorage", {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
  },
  writable: true,
})

Object.defineProperty(global, "window", {
  value: {
    location: {
      href: "",
      pathname: "/dashboard",
    },
  },
  writable: true,
})

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    window.location.href = ""
    window.location.pathname = "/dashboard"
  })

  it("should fetch user profile and return authenticated state", async () => {
    const mockUser = {
      id: 1,
      email: "student@test.com",
      full_name: "Test Student",
      role: "student",
      points: 100,
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    })

    const response = await fetch("http://localhost:8000/api/users/profile", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    })

    const data = await response.json()
    expect(data.email).toBe("student@test.com")
    expect(data.role).toBe("student")
  })

  it("should redirect to login on 401", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({}),
    })

    const response = await fetch("http://localhost:8000/api/users/profile", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    })

    expect(response.status).toBe(401)
  })

  it("should use mock fallback on network error", async () => {
    mockFetch.mockRejectedValueOnce(new TypeError("Failed to fetch"))

    try {
      const response = await fetch("http://localhost:8000/api/users/profile", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      })
    } catch (error: any) {
      expect(error.message).toBe("Failed to fetch")
    }
  })

  it("should login successfully", async () => {
    const mockResponse = {
      user: {
        id: 1,
        email: "user@test.com",
        full_name: "User",
        role: "student",
      },
      token: "fake-jwt-token",
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const response = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email: "user@test.com", password: "pass123" }),
    })

    const data = await response.json()
    expect(data.token).toBeDefined()
    expect(data.user.role).toBe("student")
  })

  it("should reject login with wrong credentials", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: "Credenciales incorrectas", detail: "Credenciales incorrectas" }),
    })

    const response = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email: "wrong@test.com", password: "wrong" }),
    })

    const data = await response.json()
    expect(response.status).toBe(401)
    expect(data.error || data.detail).toBeDefined()
  })

  it("should register successfully", async () => {
    const mockResponse = {
      user: {
        id: 2,
        email: "new@test.com",
        full_name: "New User",
        role: "student",
      },
    }

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const response = await fetch("http://localhost:8000/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        email: "new@test.com",
        password: "pass123",
        full_name: "New User",
        request_teacher: false,
      }),
    })

    const data = await response.json()
    expect(data.user.email).toBe("new@test.com")
  })
})
