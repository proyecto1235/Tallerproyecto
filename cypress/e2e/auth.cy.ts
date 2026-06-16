describe("Authentication Flows", () => {
  beforeEach(() => {
    cy.visit("/")
  })

  it("should display the login page", () => {
    cy.visit("/login")
    cy.contains("Iniciar Sesión").should("be.visible")
    cy.get('input[type="email"]').should("exist")
    cy.get('input[type="password"]').should("exist")
  })

  it("should show validation errors on empty login", () => {
    cy.visit("/login")
    cy.get('button[type="submit"]').click()
    cy.contains(/campo requerido|email|contraseña/i).should("exist")
  })

  it("should display the register page", () => {
    cy.visit("/register")
    cy.contains("Crear Cuenta").should("be.visible")
    cy.get('input[name="fullName"]').should("exist")
    cy.get('input[type="email"]').should("exist")
  })

  it("should navigate between login and register", () => {
    cy.visit("/login")
    cy.contains(/registrarse|crear cuenta/i).click()
    cy.url().should("include", "/register")
    cy.contains(/iniciar sesión/i).click()
    cy.url().should("include", "/login")
  })
})
