describe("Admin Flows", () => {
  beforeEach(() => {
    cy.visit("/login")
    cy.get('input[type="email"]').type("admin@test.com")
    cy.get('input[type="password"]').type("admin123")
    cy.get('button[type="submit"]').click()
  })

  it("should access admin dashboard", () => {
    cy.url().should("include", "/dashboard")
    cy.contains(/admin|usuarios|sistema/i).should("exist")
  })

  it("should see teacher requests", () => {
    cy.visit("/dashboard/teacher-requests")
    cy.contains(/solicitudes|profesor/i).should("exist")
  })

  it("should see audit log", () => {
    cy.visit("/dashboard/audit")
    cy.contains(/auditoría|actividad/i).should("exist")
  })

  it("should see system configuration", () => {
    cy.visit("/dashboard/system")
    cy.contains(/configuración|sistema/i).should("exist")
  })
})
