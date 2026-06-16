describe("Exercise Workflow", () => {
  beforeEach(() => {
    cy.visit("/login")
    cy.get('input[type="email"]').type("student@test.com")
    cy.get('input[type="password"]').type("password123")
    cy.get('button[type="submit"]').click()
  })

  it("should load the dashboard after login", () => {
    cy.url().should("include", "/dashboard")
    cy.contains(/dashboard|ejercicios|módulos/i).should("exist")
  })

  it("should navigate to exercises page", () => {
    cy.contains(/ejercicios|módulos/i).click()
    cy.url().should("include", "/exercises")
  })

  it("should display at least one module in the modules page", () => {
    cy.visit("/dashboard/modules")
    cy.contains(/módulos|lecciones/i).should("exist")
  })
})
