// k6 Load Test — RoboLearn v4 (student flow, no seed data dependency)
// Run: k6 run tests/load/k6-load-test.js

import http from "k6/http"
import { check, sleep } from "k6"
import { Rate, Trend } from "k6/metrics"

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000"

const failedRequests = new Rate("failed_requests")
const loginTrend = new Trend("login_duration")
const profileTrend = new Trend("profile_duration")
const modulesTrend = new Trend("modules_duration")
const recsTrend = new Trend("recommendations_duration")

export const options = {
  stages: [
    { duration: "30s", target: 100 },
    { duration: "30s", target: 250 },
    { duration: "1m", target: 500 },
    { duration: "2m", target: 500 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<10000"],
    http_req_failed: ["rate<0.05"],
    failed_requests: ["rate<0.10"],
  },
  setupTimeout: "30s",
}

export function setup() {
  const ts = Date.now()
  const email = `loadtest_${ts}@robolearn.com`
  const password = "LoadTestPass1!"

  const regPayload = JSON.stringify({
    email, password,
    full_name: "Load Test Student",
    request_teacher: false,
  })

  const regRes = http.post(`${BASE_URL}/api/auth/register`, regPayload, {
    headers: { "Content-Type": "application/json" },
  })

  if (regRes.status !== 200) {
    console.warn(`Registration returned ${regRes.status}: ${regRes.body}`)
  }

  return { email, password }
}

export default function (data) {
  if (!data || !data.email) return

  const loginPayload = JSON.stringify({
    email: data.email,
    password: data.password,
  })

  const loginRes = http.post(`${BASE_URL}/api/auth/login`, loginPayload, {
    headers: { "Content-Type": "application/json" },
  })

  loginTrend.add(loginRes.timings.duration)
  failedRequests.add(loginRes.status !== 200)

  check(loginRes, {
    "login status is 200": (r) => r.status === 200,
    "login response has user": (r) => r.json("user") != null,
  })

  if (loginRes.status !== 200) {
    sleep(Math.random() * 3 + 1)
    return
  }

  // 1. GET /api/modules — public, no auth needed
  const modulesRes = http.get(`${BASE_URL}/api/modules`, {
    headers: { "Content-Type": "application/json" },
  })
  modulesTrend.add(modulesRes.timings.duration)
  failedRequests.add(modulesRes.status !== 200)
  check(modulesRes, {
    "modules list is 200": (r) => r.status === 200,
  })

  // 2. GET /api/recommendations — needs auth
  const recsRes = http.get(`${BASE_URL}/api/recommendations`, {
    headers: { "Content-Type": "application/json" },
  })
  recsTrend.add(recsRes.timings.duration)
  failedRequests.add(recsRes.status !== 200)
  check(recsRes, {
    "recommendations is 200": (r) => r.status === 200,
  })

  // 3. GET /api/profile — needs auth
  const profileRes = http.get(`${BASE_URL}/api/auth/profile`, {
    headers: { "Content-Type": "application/json" },
  })
  profileTrend.add(profileRes.timings.duration)
  failedRequests.add(profileRes.status !== 200)
  check(profileRes, {
    "profile is 200": (r) => r.status === 200,
  })

  // 4. GET /api/modules/enrolled — needs auth
  const enrolledRes = http.get(`${BASE_URL}/api/modules/enrolled`, {
    headers: { "Content-Type": "application/json" },
  })
  failedRequests.add(enrolledRes.status !== 200)
  check(enrolledRes, {
    "enrolled modules is 200": (r) => r.status === 200,
  })

  // 5. GET /api/achievements — needs auth
  const achieveRes = http.get(`${BASE_URL}/api/achievements`, {
    headers: { "Content-Type": "application/json" },
  })
  failedRequests.add(achieveRes.status !== 200)
  check(achieveRes, {
    "achievements is 200": (r) => r.status === 200,
  })

  sleep(Math.random() * 2 + 1)
}
