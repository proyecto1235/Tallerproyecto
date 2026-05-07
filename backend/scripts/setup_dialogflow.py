"""
Script de verificación y ayuda para configurar Dialogflow.

¿Cómo obtener las credenciales de Google Cloud para Dialogflow?
================================================================

1. Ve a https://console.cloud.google.com/
2. Crea un proyecto (o selecciona uno existente)
3. Habilita la API "Dialogflow API":
   - API y Servicios > Biblioteca > buscar "Dialogflow API" > Habilitar
4. Crea una cuenta de servicio:
   - API y Servicios > Credenciales > Crear credenciales > Cuenta de servicio
   - Ponle nombre: "robolearn-chatbot"
   - Rol: "Dialogflow > Cliente de Dialogflow" (o "Admin de Dialogflow")
   - Listo
5. Genera una clave JSON:
   - En la lista de cuentas de servicio, haz clic en la que creaste
   - Ve a "Claves" > "Agregar clave" > "Crear clave nueva" > JSON
   - Se descargará un archivo .json
6. Coloca ese archivo en la raíz del proyecto como `robolearn-key.json`
7. Crea un agente de Dialogflow:
   - Ve a https://dialogflow.cloud.google.com/
   - "Create Agent"
   - Selecciona tu proyecto
   - Ponle nombre, idioma (Spanish), timezone
   - Crea el agente
8. Copia el Agent ID desde la página de Dialogflow (Settings ⚙️ > General > Project ID / Agent ID)
9. Completa backend/.env:
   
   DIALOGFLOW_PROJECT_ID=tu-project-id
   DIALOGFLOW_AGENT_ID=tu-agent-id
   GOOGLE_CREDENTIALS_PATH=../robolearn-key.json

---

Verificación actual:
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

print(f"\n📋 Estado actual de la configuración de Dialogflow:\n")
print(f"   DIALOGFLOW_PROJECT_ID:      {settings.dialogflow_project_id or '(vacio)'}")
print(f"   DIALOGFLOW_AGENT_ID:        {settings.dialogflow_agent_id or '(vacio)'}")
print(f"   GOOGLE_CREDENTIALS_PATH:    {settings.google_credentials_path or '(vacio)'}")

if settings.google_credentials_path:
    abs_path = os.path.abspath(settings.google_credentials_path)
    exists = os.path.exists(abs_path)
    print(f"\n   📍 Ruta absoluta: {abs_path}")
    print(f"   {'✅ Archivo existe' if exists else '❌ Archivo NO encontrado'}")

    if exists:
        # Try to parse the JSON to validate
        try:
            import json
            with open(abs_path) as f:
                data = json.load(f)
            print(f"   ✅ JSON válido (project_id: {data.get('project_id', 'no encontrado')})")
        except json.JSONDecodeError:
            print(f"   ❌ El archivo no es un JSON válido")
        except Exception as e:
            print(f"   ❌ Error: {e}")
else:
    print(f"\n   ❌ GOOGLE_CREDENTIALS_PATH no está configurado")
    print(f"   → Descarga el JSON de tu cuenta de servicio y configúralo")

# Test Google imports
print(f"\n🔍 Verificando dependencias:\n")
try:
    from google.cloud import dialogflow
    print(f"   ✅ google-cloud-dialogflow instalado")
except ImportError:
    print(f"   ❌ google-cloud-dialogflow NO instalado. Ejecuta: pip install google-cloud-dialogflow")

try:
    import google.auth
    print(f"   ✅ google-auth instalado")
except ImportError:
    print(f"   ❌ google-auth NO instalado")

print(f"\n💡 Para más ayuda, revisa el script mismo o la documentación.")
