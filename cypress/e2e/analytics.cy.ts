describe("Analytics & Metrics", () => {
  beforeEach(() => {
    cy.visit("/login")
    cy.get('input[type="email"]').type("teacher@test.com")
    cy.get('input[type="password"]').type("teacher123")
    cy.get('button[type="submit"]').click()
  })

  it("should access analytics dashboard", () => {
    cy.visit("/dashboard/analytics")
    cy.contains(/analítica|métricas|rendimiento/i).should("exist")
  })

  it("should access metrics page", () => {
    cy.visit("/dashboard/metrics")
    cy.contains(/métricas|estadísticas|progreso/i).should("exist")
  })

  it("should access alerts page", () => {
    cy.visit("/dashboard/alerts")
    cy.contains(/alertas|notificaciones/i).should("exist")
  })
})
