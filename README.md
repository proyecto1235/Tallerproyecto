# Robolearn

Plataforma web para el aprendizaje de programación y robótica para niños y adolescentes.

> **Note**
> Este proyecto cuenta con arquitectura hexagonal. Las tecnologías principales son **Next.js** para el frontend, **FastAPI** para el backend y **Dialogflow** para el chatbot.

## Integrantes

- Perez Ravelo Angel Simon
- Rojas Quispe Angela Deniss
- Velasquez Palomino Kevyn L
- Tucto Ubaldo Ricardo David

## Tecnologías

- **Frontend**: Next.js (React), TailwindCSS, TypeScript
- **Backend**: FastAPI, Python, PostgreSQL, MongoDB (para logs/eventos)
- **Chatbot**: Dialogflow
- **Arquitectura**: Arquitectura Hexagonal (Puertos y Adaptadores)

> [!Important]
> Algunas secciones siguen en construcción, pero buscamos brindarles la mejor experiencia posible.

El proyecto tiene un aspecto amigable y muy divertido para los estudiantes, cuenta con una interfaz muy intuitiva y fácil de usar.

## Deslpiegue de desarrollo

```bash
git clone https://github.com/proyecto1235/Tallerproyecto.git

cd backend
python3.11 -m venv .venv
source .venv/Scripts/activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

# En otra terminal
cd frontend
npm install
npm run dev
```

![home](./media/robolearn-home.png)
Página principal de la aplicación.

![login](./media/robolearn-login.png)
Página de inicio de sesión.

![dashboard](./media/robolearn-dashboard.png)
Panel principal de la aplicación.

Agradecemos el apoyo de todos los participantes del proyecto y seguiremos mejorandolo para que sea algo muy bonito :)

![lagartija saludando](./media/lagarto-gif.gif)