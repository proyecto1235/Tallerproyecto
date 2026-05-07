"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowLeft, BookOpen, CheckCircle2, Lock, Code, ChevronDown, ChevronRight } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { InlineExercise } from "@/components/interactive/InlineExercise"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

const LESSON_DATA: Record<string, any> = {
  "g-1": {
    title: "Introducción a Python",
    difficulty: "Principiante",
    lessons: [
      {
        id: "l1-1", title: "¿Qué es Python?",
        theory: `# ¿Qué es Python?

Python es un lenguaje de programación **interpretado**, **fácil de leer** y muy **versátil**. Fue creado por Guido van Rossum en 1991 y hoy es uno de los lenguajes más populares del mundo.

## ¿Por qué aprender Python?

- **Sintaxis sencilla**: Se lee casi como inglés
- **Multipropósito**: Web, ciencia de datos, robótica, IA, juegos
- **Gran comunidad**: Millones de desarrolladores comparten código
- **Gratuito**: Es open source y funciona en cualquier sistema

## Tu primer programa

En Python, imprimir un mensaje en pantalla es muy fácil:

\`\`\`python
print("¡Hola, Mundo!")
\`\`\`

La función \`print()\` muestra texto en la consola. Es como decirle a la computadora: "oye, muestra esto".

## Comentarios

Los comentarios son notas que el programador escribe para sí mismo. Python los ignora:

\`\`\`python
# Esto es un comentario (Python no lo ejecuta)
print("Este mensaje sí se muestra")  # También puedes comentar al final
\`\`\`

## Errores comunes

No te preocupes si ves errores al principio. Hasta los programadores expertos cometen errores todos los días.

\`\`\`python
# Error típico: olvidar las comillas
print(Hola)  # Error! NameError

# Error típico: paréntesis desbalanceados
print("Hola"  # Error! SyntaxError
\`\`\`

> **Tip**: Siempre revisa que tus comillas y paréntesis estén balanceados.`
      },
      {
        id: "l1-2", title: "Sintaxis Básica",
        theory: `# Sintaxis Básica de Python

Python tiene una sintaxis muy limpia. No necesitas llaves \`{}\` ni punto y coma \`;\`. La **indentación** (espacios al inicio) es lo que define los bloques.

## Números y operaciones

\`\`\`python
# Suma
print(5 + 3)   # 8

# Resta
print(10 - 4)  # 6

# Multiplicación
print(3 * 4)   # 12

# División
print(15 / 4)  # 3.75 (siempre da decimal)

# División entera
print(15 // 4) # 3 (solo la parte entera)

# Módulo (residuo)
print(15 % 4)  # 3

# Potencia
print(2 ** 3)  # 8
\`\`\`

## Texto (Strings)

\`\`\`python
print("Hola")       # Con comillas dobles
print('Mundo')      # Con comillas simples
print("Ella dijo: \"Hola\"")  # Escapando comillas
\`\`\`

## La función input()

Podemos pedir datos al usuario:

\`\`\`python
nombre = input("¿Cómo te llamas? ")
print("Hola, " + nombre)
\`\`\`

> **Nota**: \`input()\` siempre devuelve texto. Si necesitas un número, usa \`int()\` o \`float()\`.`
      },
      {
        id: "l1-3", title: "Ejercicios Prácticos",
        theory: `# Practiquemos lo Aprendido

Llegó el momento de escribir tu propio código. Los ejercicios están en el panel de abajo.

## Recuerda:

1. Usa \`print()\` para mostrar mensajes
2. Usa \`input()\` para recibir datos del usuario
3. Los comentarios empiezan con \`#\`
4. Python es sensible a mayúsculas y minúsculas

¡Intenta resolver cada ejercicio!`
      }
    ],
    exercises: {
      "l1-1": [
        { id: "g1-e1", title: "Tu Primer Hola Mundo", type: "coding", instructions: "# Escribe un programa que imprima \"¡Hola, Mundo!\"\n\nprint(\"¡Hola, Mundo!\")", difficulty: "easy", points: 10 },
        { id: "g1-e2", title: "Presentación Personal", type: "coding", instructions: "# Imprime tu nombre y tu edad\n# Ejemplo: \"Me llamo Ana y tengo 12 años\"\n\nnombre = \"Ana\"\nedad = 12\nprint(\"Me llamo \" + nombre + \" y tengo \" + str(edad) + \" años\")", difficulty: "easy", points: 15 }
      ],
      "l1-2": [
        { id: "g1-e3", title: "Calculadora Simple", type: "coding", instructions: "# Calcula el área de un rectángulo\n# base = 5, altura = 3\n# Fórmula: área = base * altura\n\nbase = 5\naltura = 3\narea = base * altura\nprint(\"El área es:\", area)", difficulty: "easy", points: 15 },
        { id: "g1-e4", title: "Saludo Personalizado", type: "coding", instructions: "# Pide el nombre al usuario y salúdalo\n# Usa input() y print()\n\nnombre = input(\"¿Cómo te llamas? \")\nprint(\"Mucho gusto, \" + nombre + \"!\")", difficulty: "medium", points: 20 }
      ],
      "l1-3": [
        { id: "g1-e5", title: "Mini Historia", type: "coding", instructions: '# Crea un programa que cuente una mini historia de 3 líneas\n# Usa print() para cada línea\n\nprint("Había una vez un robot llamado Py.")\nprint("Py quería aprender a programar.")\nprint("Después de mucho esfuerzo, ¡lo logró!")', difficulty: "easy", points: 10 }
      ]
    }
  },
  "g-2": {
    title: "Variables y Tipos de Datos",
    difficulty: "Principiante",
    lessons: [
      {
        id: "l2-1", title: "¿Qué son las Variables?",
        theory: `# Variables en Python

Una **variable** es como una caja donde guardamos información. Le ponemos una etiqueta (nombre) y dentro guardamos un valor.

## Creando variables

\`\`\`python
mensaje = "Hola"      # Variable de texto
edad = 15             # Variable numérica
precio = 19.99        # Número decimal
activo = True         # Booleano (Verdadero/Falso)
\`\`\`

## Reglas para nombres de variables

- Pueden contener letras, números y guión bajo \`_\`
- **No pueden** empezar con número
- **No pueden** tener espacios
- Distinguen mayúsculas/minúsculas (\`edad\` ≠ \`Edad\`)

\`\`\`python
# Válidos
mi_variable = 10
nombre1 = "Ana"
_contador = 0

# Inválidos
# 1er_lugar = "si"  # Error!
# mi variable = 5    # Error!
\`\`\`

## Reasignar variables

\`\`\`python
x = 10
print(x)  # 10
x = 20
print(x)  # 20 (cambió)
x = x + 5
print(x)  # 25
\`\`\``
      },
      {
        id: "l2-2", title: "Tipos de Datos",
        theory: `# Tipos de Datos en Python

Cada valor en Python tiene un **tipo**. Los tipos más comunes son:

| Tipo | Ejemplo | Descripción |
|------|---------|-------------|
| \`int\` | \`42\` | Números enteros |
| \`float\` | \`3.14\` | Números decimales |
| \`str\` | \`"Hola"\` | Texto (strings) |
| \`bool\` | \`True\` | Verdadero o Falso |

## Descubriendo el tipo

Usamos \`type()\` para saber el tipo de un valor:

\`\`\`python
print(type(42))      # <class 'int'>
print(type(3.14))    # <class 'float'>
print(type("Hola"))  # <class 'str'>
print(type(True))    # <class 'bool'>
\`\`\`

## Conversión entre tipos

A veces necesitamos convertir un tipo a otro:

\`\`\`python
# String a número
edad = "15"
edad_numero = int(edad)
print(edad_numero + 5)  # 20

# Número a string
puntaje = 100
mensaje = "Tu puntaje es " + str(puntaje)
print(mensaje)
\`\`\``
      },
      {
        id: "l2-3", title: "Operadores y Ejercicios",
        theory: `# Operadores con Variables

## Operadores Aritméticos

| Operador | Significado | Ejemplo |
|----------|-------------|---------|
| \`+\` | Suma | \`5 + 3 = 8\` |
| \`-\` | Resta | \`10 - 4 = 6\` |
| \`*\` | Multiplicación | \`3 * 4 = 12\` |
| \`/\` | División | \`15 / 4 = 3.75\` |
| \`//\` | División entera | \`15 // 4 = 3\` |
| \`%\` | Módulo (residuo) | \`15 % 4 = 3\` |
| \`**\` | Potencia | \`2 ** 3 = 8\` |

## Operadores de Comparación

| Operador | Significado |
|----------|-------------|
| \`==\` | Igual a |
| \`!=\` | Diferente de |
| \`>\` | Mayor que |
| \`<\` | Menor que |
| \`>=\` | Mayor o igual |
| \`<=\` | Menor o igual |

## Buenas prácticas

- Usa nombres descriptivos: \`edad_usuario\` en vez de \`x\`
- Usa \`snake_case\`: palabras separadas por guión bajo
- No uses palabras reservadas (\`if\`, \`for\`, \`while\`, etc.)`
      }
    ],
    exercises: {
      "l2-1": [
        { id: "g2-e1", title: "Mis Primeras Variables", type: "coding", instructions: "# Crea tres variables:\n# - nombre (texto)\n# - edad (número)\n# - altura (decimal)\n# Luego imprime cada una\n\nnombre = \"Carlos\"\nedad = 14\naltura = 1.65\nprint(nombre)\nprint(edad)\nprint(altura)", difficulty: "easy", points: 10 },
        { id: "g2-e2", title: "Intercambio de Valores", type: "coding", instructions: "# Intercambia los valores de a y b\n# Debe quedar a=20 y b=10\n\na = 10\nb = 20\nprint(\"Antes: a =\", a, \"b =\", b)\n\ntemporal = a\na = b\nb = temporal\n\nprint(\"Después: a =\", a, \"b =\", b)", difficulty: "medium", points: 20 }
      ],
      "l2-2": [
        { id: "g2-e3", title: "Calculadora de IVA", type: "coding", instructions: "# Calcula el precio total con IVA (21%)\n# precio_sin_iva = 100\n# Calcula el IVA y el total\n\nprecio_sin_iva = 100\niva = precio_sin_iva * 0.21\ntotal = precio_sin_iva + iva\nprint(\"Precio sin IVA:\", precio_sin_iva)\nprint(\"IVA:\", iva)\nprint(\"Total:\", total)", difficulty: "medium", points: 20 }
      ],
      "l2-3": [
        { id: "g2-e4", title: "Conversión de Unidades", type: "coding", instructions: "# Convierte metros a centímetros\n# 1 metro = 100 centímetros\n# Pide al usuario los metros y muestra los cm\n\nmetros = float(input(\"Ingresa los metros: \"))\ncentimetros = metros * 100\nprint(metros, \"metros =\", centimetros, \"centímetros\")", difficulty: "medium", points: 25 }
      ]
    }
  },
  "g-3": {
    title: "Estructuras de Control",
    difficulty: "Intermedio",
    lessons: [
      {
        id: "l3-1", title: "if, elif y else",
        theory: `# Condicionales en Python

Los condicionales permiten que tu programa **tome decisiones**. El robot decide si avanzar o detenerse según lo que detectan sus sensores.

## if

\`\`\`python
edad = 15

if edad >= 18:
    print("Eres mayor de edad")
\`\`\`

La indentación (espacios) es **obligatoria**. Todo lo que esté indentado después del \`if\` se ejecuta si la condición es verdadera.

## if - else

\`\`\`python
edad = 15

if edad >= 18:
    print("Eres mayor de edad")
else:
    print("Eres menor de edad")
\`\`\`

## if - elif - else

\`\`\`python
nota = 85

if nota >= 90:
    print("Excelente")
elif nota >= 70:
    print("Bien")
elif nota >= 60:
    print("Suficiente")
else:
    print("Necesitas mejorar")
\`\`\`

## Comparaciones útiles

\`\`\`python
# Múltiples condiciones
if temperatura > 30 and humedad < 50:
    print("Hace calor pero no hay humedad")

if temperatura > 30 or humedad > 80:
    print("Al menos una condición se cumple")

if not lloviendo:
    print("Podemos salir")
\`\`\``
      },
      {
        id: "l3-2", title: "Anidación y Ejercicios",
        theory: `# Condicionales Anidados

Podemos poner condicionales dentro de otros condicionales:

\`\`\`python
tiene_llave = True
puerta_abierta = False

if tiene_llave:
    print("Tienes la llave")
    if puerta_abierta:
        print("Puedes entrar directamente")
    else:
        print("Debes usar la llave para abrir")
else:
    print("No puedes entrar, no tienes llave")
\`\`\`

## Operador Ternario

Una forma corta de escribir un if-else simple:

\`\`\`python
edad = 20
mensaje = "Mayor" if edad >= 18 else "Menor"
print(mensaje)  # "Mayor"
\`\`\`

## Errores comunes

\`\`\`python
# Error: olvidar los dos puntos
if edad > 18   # SyntaxError! falta:

# Error: indentación inconsistente
if edad > 18:
print("Mayor")  # IndentationError!
\`\`\`

> Recuerda siempre los dos puntos \`:\` al final del \`if\`, \`elif\` y \`else\``
      }
    ],
    exercises: {
      "l3-1": [
        { id: "g3-e1", title: "Clasificador de Edades", type: "coding", instructions: "# Pide la edad al usuario y clasifícala:\n# 0-12: Niño\n# 13-17: Adolescente\n# 18-64: Adulto\n# 65+: Adulto mayor\n\nedad = int(input(\"Ingresa tu edad: \"))\n\nif edad <= 12:\n    print(\"Niño\")\nelif edad <= 17:\n    print(\"Adolescente\")\nelif edad <= 64:\n    print(\"Adulto\")\nelse:\n    print(\"Adulto mayor\")", difficulty: "medium", points: 20 },
        { id: "g3-e2", title: "Robot Decide", type: "coding", instructions: "# Simula un robot que decide qué hacer según la distancia\n# distancia < 10: \"Detenerse\"\n# distancia < 30: \"Girar\"\n# sino: \"Avanzar\"\n\ndistancia = 25\n\nif distancia < 10:\n    print(\"Detenerse\")\nelif distancia < 30:\n    print(\"Girar\")\nelse:\n    print(\"Avanzar\")", difficulty: "easy", points: 15 }
      ],
      "l3-2": [
        { id: "g3-e3", title: "Calculadora de Notas", type: "coding", instructions: "# Pide la nota del estudiante (0-100)\n# Muestra la calificación:\n# 90-100: A\n# 80-89: B\n# 70-79: C\n# 60-69: D\n# 0-59: F\n# Si la nota es inválida (>100 o <0), muestra \"Nota inválida\"\n\nnota = int(input(\"Ingresa la nota (0-100): \"))\n\nif nota < 0 or nota > 100:\n    print(\"Nota inválida\")\nelif nota >= 90:\n    print(\"A\")\nelif nota >= 80:\n    print(\"B\")\nelif nota >= 70:\n    print(\"C\")\nelif nota >= 60:\n    print(\"D\")\nelse:\n    print(\"F\")", difficulty: "medium", points: 25 }
      ]
    }
  },
  "g-4": {
    title: "Bucles y Repeticiones",
    difficulty: "Intermedio",
    lessons: [
      {
        id: "l4-1", title: "Bucle for",
        theory: `# El Bucle for

El bucle \`for\` se usa para **repetir** un bloque de código un número determinado de veces.

## Sintaxis básica

\`\`\`python
for i in range(5):
    print("Repetición", i)
\`\`\`

Esto imprime:
\`\`\`
Repetición 0
Repetición 1
Repetición 2
Repetición 3
Repetición 4
\`\`\`

\`range(5)\` genera los números 0, 1, 2, 3, 4.

## range() con inicio y fin

\`\`\`python
for i in range(2, 6):
    print(i)  # 2, 3, 4, 5
\`\`\`

## range() con paso

\`\`\`python
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8
\`\`\`

## Recorriendo listas

\`\`\`python
colores = ["rojo", "verde", "azul"]
for color in colores:
    print(color)
\`\`\`

## range() descendente

\`\`\`python
for i in range(10, 0, -1):
    print(i)  # 10, 9, 8, ..., 1
\`\`\``
      },
      {
        id: "l4-2", title: "Bucle while",
        theory: `# El Bucle while

El bucle \`while\` repite mientras una condición sea verdadera.

## Sintaxis básica

\`\`\`python
contador = 0
while contador < 5:
    print("Contador:", contador)
    contador = contador + 1  # ¡Importante: actualizar!
\`\`\`

## Cuidado con bucles infinitos

Si olvidas actualizar la condición, el bucle nunca termina:

\`\`\`python
# PELIGRO: Bucle infinito
x = 0
while x < 10:
    print(x)
    # Olvidé: x = x + 1
\`\`\`

## break y continue

\`\`\`python
# break: sale del bucle
for i in range(10):
    if i == 5:
        break  # Termina el bucle
    print(i)  # 0, 1, 2, 3, 4

# continue: salta a la siguiente iteración
for i in range(5):
    if i == 2:
        continue  # Salta el 2
    print(i)  # 0, 1, 3, 4
\`\`\`

## Uso típico: validar entrada

\`\`\`python
respuesta = ""
while respuesta != "si" and respuesta != "no":
    respuesta = input("¿Quieres continuar? (si/no): ")
print("Respuesta válida:", respuesta)
\`\`\``
      }
    ],
    exercises: {
      "l4-1": [
        { id: "g4-e1", title: "Cuenta Regresiva", type: "coding", instructions: "# Usa un bucle for para contar del 10 al 1\n# Luego imprime \"¡Despegue!\"\n\nfor i in range(10, 0, -1):\n    print(i)\n\nprint(\"¡Despegue!\")", difficulty: "easy", points: 15 },
        { id: "g4-e2", title: "Tabla de Multiplicar", type: "coding", instructions: "# Pide un número al usuario\n# Muestra su tabla de multiplicar del 1 al 10\n\nnumero = int(input(\"Ingresa un número: \"))\n\nfor i in range(1, 11):\n    print(numero, \"x\", i, \"=\", numero * i)", difficulty: "medium", points: 20 }
      ],
      "l4-2": [
        { id: "g4-e3", title: "Adivina el Número", type: "coding", instructions: "# Crea un juego donde el usuario adivina\n# El número secreto es 7\n# El bucle continúa hasta que acierte\n\nsecreto = 7\nintento = 0\n\nwhile intento != secreto:\n    intento = int(input(\"Adivina el número (1-10): \"))\n    if intento != secreto:\n        print(\"¡Incorrecto! Intenta de nuevo\")\n\nprint(\"¡Correcto! El número era\", secreto)", difficulty: "hard", points: 30 }
      ]
    }
  },
  "g-5": {
    title: "Funciones",
    difficulty: "Avanzado",
    lessons: [
      {
        id: "l5-1", title: "Definiendo Funciones",
        theory: `# Funciones en Python

Las funciones son **bloques de código reutilizables**. Agrupan instrucciones bajo un nombre para usarlas cuando quieras.

## Definiendo una función

\`\`\`python
def saludar():
    print("¡Hola!")
    print("Bienvenido a Python")
\`\`\`

## Llamando una función

\`\`\`python
saludar()  # Ejecuta todo el bloque
saludar()  # Lo puedes llamar varias veces
\`\`\`

## Funciones con parámetros

\`\`\`python
def saludar_persona(nombre):
    print(f"¡Hola, {nombre}!")

saludar_persona("Ana")   # ¡Hola, Ana!
saludar_persona("Luis")  # ¡Hola, Luis!
\`\`\`

## Funciones con múltiples parámetros

\`\`\`python
def sumar(a, b):
    resultado = a + b
    print(f"{a} + {b} = {resultado}")

sumar(5, 3)  # 5 + 3 = 8
\`\`\``
      },
      {
        id: "l5-2", title: "Return y Scope",
        theory: `# Return en Funciones

Las funciones pueden **devolver** valores usando \`return\`:

\`\`\`python
def sumar(a, b):
    return a + b

resultado = sumar(5, 3)
print(resultado)  # 8
\`\`\`

## Función sin return

Si no usas \`return\`, la función devuelve \`None\`:

\`\`\`python
def mostrar_mensaje():
    print("Hola")

valor = mostrar_mensaje()
print(valor)  # None
\`\`\`

## Scope (alcance) de variables

Las variables dentro de una función no se ven desde fuera:

\`\`\`python
def mi_funcion():
    x = 10  # x solo existe aquí
    print(x)

mi_funcion()  # 10
# print(x)  # Error! x no está definida
\`\`\`

## Parámetros por defecto

\`\`\`python
def saludar(nombre="amigo"):
    print(f"¡Hola, {nombre}!")

saludar()         # ¡Hola, amigo!
saludar("Ana")    # ¡Hola, Ana!
\`\`\``
      },
      {
        id: "l5-3", title: "Ejercicios con Funciones",
        theory: `# Practicando Funciones

## Buenas prácticas

1. **Nombres descriptivos**: \`calcular_area\` en vez de \`ca\`
2. **Una sola responsabilidad**: cada función hace una cosa
3. **Documenta**: usa comentarios para explicar qué hace

## Ejemplo completo

\`\`\`python
def calcular_promedio(notas):
    """Calcula el promedio de una lista de notas"""
    suma = sum(notas)
    cantidad = len(notas)
    return suma / cantidad

def clasificar_promedio(promedio):
    if promedio >= 90:
        return "Excelente"
    elif promedio >= 70:
        return "Bien"
    else:
        return "Necesitas mejorar"

# Usando las funciones
mis_notas = [85, 92, 78, 95]
prom = calcular_promedio(mis_notas)
print(f"Promedio: {prom}")
print(f"Clasificación: {clasificar_promedio(prom)}")
\`\`\``
      }
    ],
    exercises: {
      "l5-1": [
        { id: "g5-e1", title: "Mi Primera Función", type: "coding", instructions: "# Crea una función llamada 'cuadrado' que reciba un número\n# y devuelva su cuadrado (número * número)\n\ndef cuadrado(numero):\n    return numero * numero\n\nprint(cuadrado(4))  # Debe imprimir 16\nprint(cuadrado(7))  # Debe imprimir 49", difficulty: "medium", points: 20 },
        { id: "g5-e2", title: "Saludo Personalizado", type: "coding", instructions: "# Crea una función saludar(nombre, idioma)\n# Si idioma es \"es\", saluda en español\n# Si idioma es \"en\", saluda en inglés\n\ndef saludar(nombre, idioma):\n    if idioma == \"es\":\n        print(f\"¡Hola, {nombre}!\")\n    elif idioma == \"en\":\n        print(f\"Hello, {nombre}!\")\n    else:\n        print(f\"Hola, {nombre}!\")\n\nsaludar(\"Ana\", \"es\")\nsaludar(\"John\", \"en\")", difficulty: "medium", points: 25 }
      ],
      "l5-2": [
        { id: "g5-e3", title: "Calculadora con Return", type: "coding", instructions: "# Crea funciones para las 4 operaciones básicas\n# sumar, restar, multiplicar, dividir\n# Cada una recibe dos números y devuelve el resultado\n\ndef sumar(a, b):\n    return a + b\n\ndef restar(a, b):\n    return a - b\n\ndef multiplicar(a, b):\n    return a * b\n\ndef dividir(a, b):\n    if b != 0:\n        return a / b\n    else:\n        return \"Error: división por cero\"\n\nprint(sumar(10, 5))\nprint(restar(10, 5))\nprint(multiplicar(10, 5))\nprint(dividir(10, 5))", difficulty: "hard", points: 30 }
      ]
    }
  },
  "g-6": {
    title: "Listas y Tuplas",
    difficulty: "Intermedio",
    lessons: [
      {
        id: "l6-1", title: "Listas",
        theory: `# Listas en Python

Las **listas** son colecciones ordenadas que pueden contener cualquier tipo de dato.

## Creando listas

\`\`\`python
# Lista vacía
mi_lista = []

# Lista con elementos
frutas = ["manzana", "banana", "naranja"]
numeros = [1, 2, 3, 4, 5]
mixta = [1, "hola", True, 3.14]
\`\`\`

## Accediendo a elementos

\`\`\`python
frutas = ["manzana", "banana", "naranja"]

print(frutas[0])   # manzana (índice 0)
print(frutas[1])   # banana
print(frutas[-1])  # naranja (último)
print(frutas[-2])  # banana
\`\`\`

## Modificando listas

\`\`\`python
frutas = ["manzana", "banana", "naranja"]

# Cambiar un elemento
frutas[1] = "pera"
print(frutas)  # ["manzana", "pera", "naranja"]

# Agregar al final
frutas.append("uva")
print(frutas)  # ["manzana", "pera", "naranja", "uva"]

# Insertar en posición
frutas.insert(1, "kiwi")
print(frutas)  # ["manzana", "kiwi", "pera", "naranja", "uva"]

# Eliminar por valor
frutas.remove("pera")
print(frutas)  # ["manzana", "kiwi", "naranja", "uva"]

# Eliminar por índice
eliminado = frutas.pop(1)
print(eliminado)  # "kiwi"
print(frutas)     # ["manzana", "naranja", "uva"]
\`\`\``
      },
      {
        id: "l6-2", title: "Tuplas y Métodos",
        theory: `# Tuplas y Métodos de Listas

## Tuplas

Las **tuplas** son como listas pero **inmutables** (no se pueden modificar).

\`\`\`python
# Se crean con paréntesis
coordenadas = (10, 20)
colores_rgb = (255, 0, 0)

# Acceder es igual que en listas
print(coordenadas[0])  # 10

# Pero NO se pueden modificar
# coordenadas[0] = 5  # Error!

# ¿Por qué usar tuplas?
# - Son más rápidas que las listas
# - Protegen datos que no deben cambiar
# - Pueden usarse como claves de diccionario
\`\`\`

## Métodos útiles de listas

\`\`\`python
numeros = [3, 1, 4, 1, 5, 9, 2]

print(len(numeros))      # 7 (longitud)
print(sum(numeros))      # 25 (suma)
print(max(numeros))      # 9 (máximo)
print(min(numeros))      # 1 (mínimo)

numeros.sort()           
print(numeros)           # [1, 1, 2, 3, 4, 5, 9]

numeros.reverse()
print(numeros)           # [9, 5, 4, 3, 2, 1, 1]

print(5 in numeros)      # True
print(10 in numeros)     # False
\`\`\`

## Slicing (rebanado)

\`\`\`python
numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(numeros[2:5])   # [2, 3, 4]
print(numeros[:4])    # [0, 1, 2, 3]
print(numeros[6:])    # [6, 7, 8, 9]
print(numeros[::2])   # [0, 2, 4, 6, 8]
print(numeros[::-1])  # [9, 8, 7, ..., 0]
\`\`\``
      }
    ],
    exercises: {
      "l6-1": [
        { id: "g6-e1", title: "Lista de Compras", type: "coding", instructions: "# Crea una lista de compras con 4 items\n# Agrega 2 más con append()\n# Luego imprime cada item con un bucle for\n\ncompras = [\"leche\", \"pan\", \"huevos\", \"queso\"]\ncompras.append(\"manzanas\")\ncompras.append(\"arroz\")\n\nfor item in compras:\n    print(\"-\", item)", difficulty: "easy", points: 15 },
        { id: "g6-e2", title: "Promedio de Lista", type: "coding", instructions: "# Calcula el promedio de una lista de números\n# Usa sum() y len()\n\nnotas = [85, 92, 78, 95, 88]\npromedio = sum(notas) / len(notas)\nprint(\"Notas:\", notas)\nprint(\"Promedio:\", promedio)", difficulty: "medium", points: 20 }
      ],
      "l6-2": [
        { id: "g6-e3", title: "Analizador de Listas", type: "coding", instructions: "# Encuentra el número más grande y el más pequeño\n# de una lista usando un bucle (sin usar max/min)\n\nnumeros = [12, 45, 7, 23, 56, 89, 34]\nmas_grande = numeros[0]\nmas_pequeno = numeros[0]\n\nfor n in numeros:\n    if n > mas_grande:\n        mas_grande = n\n    if n < mas_pequeno:\n        mas_pequeno = n\n\nprint(\"Lista:\", numeros)\nprint(\"Más grande:\", mas_grande)\nprint(\"Más pequeño:\", mas_pequeno)", difficulty: "hard", points: 30 }
      ]
    }
  },
  "g-7": {
    title: "Diccionarios y Sets",
    difficulty: "Intermedio",
    lessons: [
      {
        id: "l7-1", title: "Diccionarios",
        theory: `# Diccionarios en Python

Los **diccionarios** almacenan datos en pares **clave: valor**. Como un diccionario real: buscas por la palabra (clave) y obtienes su significado (valor).

## Creando diccionarios

\`\`\`python
# Diccionario vacío
estudiante = {}

# Con datos
estudiante = {
    "nombre": "Ana",
    "edad": 15,
    "curso": "Python",
    "nota": 95
}
\`\`\`

## Accediendo a valores

\`\`\`python
print(estudiante["nombre"])  # Ana
print(estudiante.get("edad"))  # 15
print(estudiante.get("peso", "No existe"))  # No existe
\`\`\`

## Modificando diccionarios

\`\`\`python
# Agregar o modificar
estudiante["nota"] = 98  # Modificar
estudiante["ciudad"] = "Madrid"  # Agregar nuevo

# Eliminar
del estudiante["ciudad"]

# Ver todas las claves
print(estudiante.keys())    # dict_keys([...])

# Ver todos los valores
print(estudiante.values())  # dict_values([...])

# Ver todo
print(estudiante.items())   # pares (clave, valor)
\`\`\`

## Recorriendo diccionarios

\`\`\`python
for clave, valor in estudiante.items():
    print(f"{clave}: {valor}")
\`\`\``
      },
      {
        id: "l7-2", title: "Sets y Ejercicios",
        theory: `# Sets (Conjuntos)

Los **sets** son colecciones **no ordenadas** de elementos **únicos** (sin duplicados).

## Creando sets

\`\`\`python
set_vacio = set()
colores = {"rojo", "verde", "azul"}
numeros = set([1, 2, 3, 2, 1])  # {1, 2, 3}
\`\`\`

## Operaciones con sets

\`\`\`python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Unión
print(a | b)  # {1, 2, 3, 4, 5, 6}

# Intersección
print(a & b)  # {3, 4}

# Diferencia
print(a - b)  # {1, 2}

# ¿Es subconjunto?
print({1, 2}.issubset(a))  # True
\`\`\`

## ¿Lista, Tupla, Set o Diccionario?

| Tipo | Ordenado | Modificable | Duplicados | Ejemplo |
|------|----------|-------------|------------|---------|
| Lista | ✅ | ✅ | ✅ | \`[1, 2, 3]\` |
| Tupla | ✅ | ❌ | ✅ | \`(1, 2, 3)\` |
| Set | ❌ | ✅ | ❌ | \`{1, 2, 3}\` |
| Diccionario | ✅ | ✅ | Claves únicas | \`{"a": 1}\` |`
      }
    ],
    exercises: {
      "l7-1": [
        { id: "g7-e1", title: "Agenda de Contactos", type: "coding", instructions: "# Crea un diccionario con 3 contactos\n# Cada contacto tiene nombre, teléfono y ciudad\n# Luego imprime cada contacto\n\ncontactos = {\n    \"Ana\": {\"telefono\": \"123-456\", \"ciudad\": \"Madrid\"},\n    \"Luis\": {\"telefono\": \"789-012\", \"ciudad\": \"Barcelona\"},\n    \"Sofía\": {\"telefono\": \"345-678\", \"ciudad\": \"Valencia\"}\n}\n\nfor nombre, info in contactos.items():\n    print(f\"{nombre}: {info['telefono']} - {info['ciudad']}\")", difficulty: "medium", points: 25 },
        { id: "g7-e2", title: "Contador de Palabras", type: "coding", instructions: "# Cuenta cuántas veces aparece cada palabra\n# Usa un diccionario para almacenar los conteos\n\ntexto = \"python es genial python es divertido python es poderoso\"\npalabras = texto.split()\nconteo = {}\n\nfor palabra in palabras:\n    if palabra in conteo:\n        conteo[palabra] += 1\n    else:\n        conteo[palabra] = 1\n\nfor palabra, veces in conteo.items():\n    print(f\"{palabra}: {veces}\")", difficulty: "hard", points: 30 }
      ]
    }
  },
  "g-8": {
    title: "Manejo de Archivos",
    difficulty: "Avanzado",
    lessons: [
      {
        id: "l8-1", title: "Lectura de Archivos",
        theory: `# Leyendo Archivos en Python

Python puede leer y escribir archivos en tu computadora. Esto es esencial para trabajar con datos.

## Abriendo un archivo

\`\`\`python
# Modo lectura (por defecto)
archivo = open("datos.txt", "r")
contenido = archivo.read()
archivo.close()
\`\`\`

## La forma segura: with

\`\`\`python
with open("datos.txt", "r") as archivo:
    contenido = archivo.read()
    print(contenido)
# El archivo se cierra automáticamente
\`\`\`

## Métodos de lectura

\`\`\`python
with open("datos.txt", "r") as f:
    # Leer todo
    todo = f.read()
    
    # Leer línea por línea
    for linea in f:
        print(linea.strip())  # strip() quita el \\n
\`\`\`

## Modos de apertura

| Modo | Descripción |
|------|-------------|
| \`"r"\` | Lectura (por defecto) |
| \`"w"\` | Escritura (sobrescribe) |
| \`"a"\` | Agregar al final |
| \`"r+"\` | Lectura y escritura |`
      },
      {
        id: "l8-2", title: "Escritura y CSV",
        theory: `# Escribiendo Archivos

\`\`\`python
with open("salida.txt", "w") as f:
    f.write("Hola, mundo!\\n")
    f.write("Esta es una nueva línea.\\n")

# Modo append (agregar)
with open("salida.txt", "a") as f:
    f.write("Esta línea se agrega al final.\\n")
\`\`\`

## Trabajando con CSV

Los archivos CSV son como tablas de Excel en texto:

\`\`\`python
# Leer CSV
with open("notas.csv", "r") as f:
    for linea in f:
        datos = linea.strip().split(",")
        nombre = datos[0]
        nota = datos[1]
        print(f"{nombre}: {nota}")
\`\`\`

## Escribir CSV

\`\`\`python
estudiantes = [
    ["Ana", 95],
    ["Luis", 87],
    ["Sofía", 92]
]

with open("notas.csv", "w") as f:
    f.write("nombre,nota\\n")  # Encabezado
    for e in estudiantes:
        f.write(f"{e[0]},{e[1]}\\n")
\`\`\`

> **Tip**: Para archivos CSV complejos, usa el módulo \`csv\` de Python. Para Excel real, usa \`openpyxl\`.`
      }
    ],
    exercises: {
      "l8-1": [
        { id: "g8-e1", title: "Simular Lectura", type: "coding", instructions: "# Simula la lectura de un archivo\n# Tenemos una variable con el contenido\n# Cuenta cuántas líneas tiene\n\ncontenido = \"\"\"línea 1\nlínea 2\nlínea 3\nlínea 4\nlínea 5\"\"\"\n\nlineas = contenido.split(\"\\n\")\nprint(\"Número de líneas:\", len(lineas))\n\nfor i, linea in enumerate(lineas, 1):\n    print(f\"{i}: {linea}\")", difficulty: "medium", points: 20 },
        { id: "g8-e2", title: "Procesar CSV", type: "coding", instructions: "# Simula procesar un archivo CSV de estudiantes\n# Calcula el promedio de notas\n\ndatos = \"\"\"nombre,nota\nAna,95\nLuis,87\nSofía,92\nCarlos,78\nMaría,96\"\"\"\n\nlineas = datos.strip().split(\"\\n\")\nsuma = 0\ncantidad = 0\n\nfor linea in lineas[1:]:  # Saltar encabezado\n    partes = linea.split(\",\")\n    nota = int(partes[1])\n    suma += nota\n    cantidad += 1\n\npromedio = suma / cantidad\nprint(f\"Promedio del curso: {promedio}\")", difficulty: "hard", points: 30 }
      ]
    }
  },
  "g-9": {
    title: "Módulos y Paquetes",
    difficulty: "Avanzado",
    lessons: [
      {
        id: "l9-1", title: "Importando Módulos",
        theory: `# Módulos en Python

Los **módulos** son archivos con código Python que puedes reutilizar. Python viene con muchos módulos incluidos.

## Importando módulos

\`\`\`python
# Importar todo el módulo
import math
print(math.sqrt(16))  # 4.0
print(math.pi)        # 3.14159...

# Importar funciones específicas
from math import sqrt, pi
print(sqrt(25))   # 5.0
print(pi)         # 3.14159...

# Importar con alias
import math as m
print(m.sqrt(36))  # 6.0
\`\`\`

## Módulos útiles de Python

| Módulo | Para qué sirve |
|--------|---------------|
| \`math\` | Funciones matemáticas |
| \`random\` | Números aleatorios |
| \`datetime\` | Fechas y horas |
| \`os\` | Sistema operativo |
| \`json\` | Trabajar con JSON |

## Ejemplo: random

\`\`\`python
import random

# Número aleatorio entre 1 y 10
print(random.randint(1, 10))

# Elegir al azar de una lista
colores = ["rojo", "verde", "azul"]
print(random.choice(colores))

# Mezclar una lista
numeros = [1, 2, 3, 4, 5]
random.shuffle(numeros)
print(numeros)
\`\`\``
      },
      {
        id: "l9-2", title: "Creando tus Propios Módulos",
        theory: `# Creando tus Propios Módulos

Puedes crear tus propios módulos para organizar tu código.

## math_utils.py

\`\`\`python
# Este sería un archivo separado: math_utils.py
def suma(a, b):
    return a + b

def resta(a, b):
    return a - b

PI = 3.14159
\`\`\`

## Usando tu módulo

\`\`\`python
# En otro archivo
import math_utils

print(math_utils.suma(10, 5))  # 15
print(math_utils.PI)           # 3.14159
\`\`\`

## Paquetes

Un **paquete** es una carpeta con varios módulos. Debe tener un archivo \`__init__.py\`:

\`\`\`
mi_paquete/
  __init__.py
  operaciones.py
  graficos.py
  utilidades.py
\`\`\`

## Instalando con pip

\`\`\`bash
pip install requests
pip install numpy
pip install matplotlib
\`\`\`

\`\`\`python
# Luego de instalar
import requests
respuesta = requests.get("https://api.github.com")
print(respuesta.status_code)
\`\`\``
      }
    ],
    exercises: {
      "l9-1": [
        { id: "g9-e1", title: "Dados Virtuales", type: "coding", instructions: "# Simula el lanzamiento de dos dados usando random\n# Muestra los valores y la suma\n\nimport random\n\ndado1 = random.randint(1, 6)\ndado2 = random.randint(1, 6)\n\nprint(f\"Dado 1: {dado1}\")\nprint(f\"Dado 2: {dado2}\")\nprint(f\"Suma: {dado1 + dado2}\")", difficulty: "medium", points: 20 },
        { id: "g9-e2", title: "Fecha Actual", type: "coding", instructions: "# Usa el módulo datetime para mostrar la fecha y hora actual\n# Luego muestra solo el año\n\nimport datetime\n\nahora = datetime.datetime.now()\nprint(\"Fecha y hora actual:\", ahora)\nprint(\"Año:\", ahora.year)\nprint(\"Mes:\", ahora.month)\nprint(\"Día:\", ahora.day)", difficulty: "medium", points: 20 }
      ]
    }
  },
  "g-10": {
    title: "Proyecto Final: Robot Autónomo",
    difficulty: "Avanzado",
    lessons: [
      {
        id: "l10-1", title: "Diseño del Robot",
        theory: `# Proyecto Final: Robot Autónomo

¡Llegó el momento de aplicar todo lo aprendido! Vamos a programar un robot virtual que navega por sí mismo.

## El Robot

Nuestro robot tiene:
- **Sensor ultrasónico**: Mide distancia a objetos (cm)
- **Sensor de luz**: Detecta claridad (0-100)
- **Motores**: Puede avanzar, retroceder y girar

## Funciones del Robot

\`\`\`python
# Estas funciones ya están definidas para ti:
# medir_distancia() -> número (cm)
# medir_luz() -> número (0-100)
# avanzar(pasos)
# retroceder(pasos)
# girar(angulo)  # ángulo en grados
# detener()
\`\`\`

## Tu misión

Programar al robot para que:
1. Avance cuando no haya obstáculos
2. Gire cuando detecte un obstáculo lejano
3. Retroceda cuando el obstáculo esté muy cerca
4. Se detenga cuando llegue a su destino`
      },
      {
        id: "l10-2", title: "Programando la Navegación",
        theory: `# Lógica de Navegación

## Máquina de Estados

Usaremos una máquina de estados simple:

\`\`\`python
ESTADO_AVANZAR = "avanzar"
ESTADO_GIRAR = "girar"
ESTADO_RETROCEDER = "retroceder"
ESTADO_DETENER = "detener"

estado = ESTADO_AVANZAR
\`\`\`

## Ciclo Principal

\`\`\`python
while estado != ESTADO_DETENER:
    distancia = medir_distancia()
    
    if distancia > 50:
        estado = ESTADO_AVANZAR
    elif distancia > 20:
        estado = ESTADO_GIRAR
    elif distancia > 5:
        estado = ESTADO_RETROCEDER
    else:
        estado = ESTADO_DETENER
    
    # Ejecutar acción según estado
    if estado == ESTADO_AVANZAR:
        avanzar(1)
    elif estado == ESTADO_GIRAR:
        girar(45)
    elif estado == ESTADO_RETROCEDER:
        retroceder(3)
        girar(90)
    else:
        detener()
\`\`\``
      },
      {
        id: "l10-3", title: "Desafío Final",
        theory: `# Desafío Final

## Mejoras opcionales

Una vez que tu robot navegue básicamente, intenta:

### 1. Memoria del entorno
\`\`\`python
obstaculos_vistos = []

def recordar_obstaculo(distancia):
    obstaculos_vistos.append(distancia)
    if len(obstaculos_vistos) > 10:
        obstaculos_vistos.pop(0)
\`\`\`

### 2. Modo exploración
\`\`\`python
def explorar():
    """Gira 360° buscando el camino más despejado"""
    mejor_direccion = 0
    mejor_distancia = 0
    
    for angulo in range(0, 360, 30):
        girar(30)
        d = medir_distancia()
        if d > mejor_distancia:
            mejor_distancia = d
            mejor_direccion = angulo
    
    print(f"Mejor dirección: {mejor_direccion}° con {mejor_distancia}cm libres")
\`\`\`

### 3. Contador de pasos
\`\`\`python
pasos_totales = 0

def avanzar_con_conteo(pasos):
    global pasos_totales
    pasos_totales += pasos
    print(f"Total de pasos: {pasos_totales}")
    avanzar(pasos)
\`\`\`

¡Buena suerte, futuro ingeniero! 🚀`
      }
    ],
    exercises: {
      "l10-1": [
        { id: "g10-e1", title: "Sensores del Robot", type: "coding", instructions: "# Simula la lectura de los sensores del robot\n# Define funciones que simulen medir_distancia() y medir_luz()\n\ndef medir_distancia():\n    return 30  # Simula 30 cm\n\ndef medir_luz():\n    return 75  # Simula 75% de luz\n\ndistancia = medir_distancia()\nluz = medir_luz()\nprint(f\"Distancia: {distancia} cm\")\nprint(f\"Luz: {luz}%\")", difficulty: "easy", points: 15 },
        { id: "g10-e2", title: "Primera Decisión", type: "coding", instructions: "# Usa la distancia medida para decidir\n# Si distancia < 20: print(\"Obstáculo cerca\")\n# Si distancia < 50: print(\"Precaución\")\n# Sino: print(\"Camino libre\")\n\ndistancia = 35\n\nif distancia < 20:\n    print(\"Obstáculo cerca\")\nelif distancia < 50:\n    print(\"Precaución\")\nelse:\n    print(\"Camino libre\")", difficulty: "easy", points: 15 }
      ],
      "l10-2": [
        { id: "g10-e3", title: "Navegación Automática", type: "coding", instructions: "# Simula 5 ciclos de navegación del robot\n# En cada ciclo, genera una distancia y decide\n\nfor ciclo in range(5):\n    distancia = 10 + ciclo * 20  # 10, 30, 50, 70, 90\n    \n    if distancia > 50:\n        print(f\"Ciclo {ciclo+1}: Avanzar ({distancia}cm)\")\n    elif distancia > 20:\n        print(f\"Ciclo {ciclo+1}: Girar ({distancia}cm)\")\n    else:\n        print(f\"Ciclo {ciclo+1}: Retroceder ({distancia}cm)\")", difficulty: "medium", points: 25 }
      ],
      "l10-3": [
        { id: "g10-e4", title: "Robot Completo", type: "coding", instructions: "# Programa completo del robot autónomo\n# Combina todo lo aprendido\n\ndef medir_distancia():\n    return 30\n\ndef avanzar():\n    print(\"Avanzando...\")\n\ndef girar():\n    print(\"Girando...\")\n\ndef retroceder():\n    print(\"Retrocediendo...\")\n\n# Ciclo principal\nfor i in range(3):\n    d = medir_distancia() + i * 15  # Simula cambios\n    print(f\"Iteración {i+1}: distancia = {d}\")\n    \n    if d > 40:\n        avanzar()\n    elif d > 15:\n        girar()\n    else:\n        retroceder()", difficulty: "hard", points: 35 }
      ]
    }
  }
}

export default function ModuleViewPage() {
  const params = useParams()
  const router = useRouter()
  const [module, setModule] = useState<any>(null)
  const [exercises, setExercises] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeLesson, setActiveLesson] = useState<string | null>(null)

  useEffect(() => {
    const fetchModule = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/modules/${params.id}`, { credentials: 'include' })
        const data = await res.json()
        if (data.success && data.module) {
          setModule(data.module)
          const exRes = await fetch(`http://localhost:8000/api/modules/${params.id}/exercises`, { credentials: 'include' })
          const exData = await exRes.json()
          if (exData.success) setExercises(exData.exercises)
          setIsLoading(false)
          return
        }
      } catch (_) {}

      const modId = String(params.id)
      const lessonData = LESSON_DATA[modId]
      if (lessonData) {
        setModule({
          id: modId,
          title: lessonData.title,
          difficulty: lessonData.difficulty,
          status: "in-progress",
          progress: 30
        })
        setExercises(lessonData.lessons.map((l: any) => ({
          lessonId: l.id,
          title: l.title,
          theory: l.theory,
          exercises: lessonData.exercises[l.id] || []
        })))
      } else {
        setModule(null)
      }
      setIsLoading(false)
    }
    if (params.id) fetchModule()
  }, [params.id])

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
  }

  if (!module) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-4">
        <h2 className="text-2xl font-bold">Módulo no encontrado</h2>
        <Button onClick={() => router.back()} variant="outline"><ArrowLeft className="h-4 w-4 mr-2" />Volver</Button>
      </div>
    )
  }

  const lessonData = LESSON_DATA[String(params.id)]
  const lessons = lessonData?.lessons || []
  const progress = module.progress || 0

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <Button variant="ghost" onClick={() => router.push('/dashboard/modules')} className="mb-2">
        <ArrowLeft className="h-4 w-4 mr-2" />Volver a módulos
      </Button>

      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
          <BookOpen className="h-6 w-6 text-primary" />
        </div>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{module.title}</h1>
          <p className="text-muted-foreground">{lessons.length} lecciones · {lessonData?.difficulty || "Intermedio"}</p>
        </div>
        {progress > 0 && (
          <div className="w-32">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Progreso</span><span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}
      </div>

      <div className="space-y-4">
        {lessons.map((lesson: any, index: number) => {
          const isOpen = activeLesson === lesson.id
          const lessonExercises = lessonData?.exercises?.[lesson.id] || []
          return (
            <Card key={lesson.id} className={cn("overflow-hidden transition-all duration-300", isOpen ? "border-primary/30" : "")}>
              <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => setActiveLesson(isOpen ? null : lesson.id)}
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0",
                    index === 0 ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
                  )}>
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="font-semibold">{lesson.title}</h3>
                    <p className="text-xs text-muted-foreground">{lessonExercises.length} ejercicios</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {lessonExercises.length > 0 && (
                    <Code className="w-4 h-4 text-muted-foreground" />
                  )}
                  {isOpen ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                </div>
              </div>

              {isOpen && (
                <div className="border-t border-border p-6">
                  <div className="prose prose-invert max-w-none mb-8">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{lesson.theory}</ReactMarkdown>
                  </div>

                  {lessonExercises.length > 0 && (
                    <div className="space-y-8 border-t border-border pt-6">
                      <h4 className="font-bold text-lg flex items-center gap-2">
                        <Code className="w-5 h-5 text-primary" />
                        Ejercicios de la lección
                      </h4>
                      {lessonExercises.map((ex: any) => (
                        <InlineExercise key={ex.id} exercise={ex} />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}