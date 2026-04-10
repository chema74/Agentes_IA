# P29 · Simulador de habilidades directivas

> **Portfolio IA Aplicada · José María · Sevilla**  
> Stack: Groq · Streamlit  
> Coste: **gratuito** salvo el uso del modelo

## Qué hace este proyecto

Esta versión pública del agente final **Simulador de habilidades directivas** permite practicar conversaciones de liderazgo y gestión en un entorno simulado.

Hoy cubre un caso de uso concreto y defendible:

- seleccionar un escenario directivo,
- conversar con un interlocutor simulado por IA,
- ensayar respuestas en situaciones difíciles,
- recibir un feedback posterior orientativo para reflexión y práctica.

No sustituye formación directiva, coaching profesional ni evaluación formal de competencias.

## Casos de uso

- dar feedback difícil a un colaborador,
- gestionar un conflicto entre miembros del equipo,
- comunicar un cambio organizacional impopular,
- motivar a un equipo tras malos resultados,
- negociar con un colaborador clave,
- delegar una tarea importante.

## Cómo funciona

```text
Usuario selecciona un escenario
        ↓
La app configura el contexto de la simulación
        ↓
La IA interpreta al interlocutor y abre la conversación
        ↓
El usuario responde como directivo
        ↓
La conversación avanza por turnos
        ↓
Al finalizar, la app genera un feedback orientativo en JSON
        ↓
Se muestra un resumen con fortalezas, mejoras y una alternativa de formulación
```

## Límites operativos

- El feedback es orientativo y sirve para práctica y reflexión.
- No mide competencias de forma objetiva.
- No realiza evaluación psicológica ni diagnóstico conductual.
- No sustituye coaching, mentoring ni assessment profesional.

## Instalación

```bash
cd proyectos/p29-simulador-habilidades-directivas
pip install -r requirements.txt
copy .env.example .env
# Añadir GROQ_API_KEY en el archivo .env
python -m streamlit run app.py
```

---

*Portfolio IA Aplicada · José María · Sevilla · 2026*
