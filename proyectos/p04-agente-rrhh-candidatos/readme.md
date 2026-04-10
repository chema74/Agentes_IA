# P04 · Agente de criba de candidatos

> **Portfolio IA Aplicada · José María · Sevilla**  
> Stack: Groq · ChromaDB · sentence-transformers · PyMuPDF · Streamlit  
> Coste: **gratuito** · revisión humana obligatoria

## Qué hace este proyecto

Esta versión pública del agente final **Agente de criba de candidatos** permite:

- definir un puesto y las competencias requeridas,
- subir CVs en PDF,
- generar una preevaluación documental inicial,
- estructurar señales orientativas sobre ajuste al perfil,
- proponer preguntas de entrevista para revisión humana posterior.

Su función es **apoyar una criba inicial**, no tomar decisiones de contratación ni sustituir el criterio profesional de RR. HH.

## Qué devuelve

- señal orientativa de ajuste al perfil,
- fortalezas y gaps detectables en el CV,
- comprobación básica de experiencia mínima declarada,
- competencias observables en el documento,
- preguntas de entrevista para validar el perfil,
- ranking orientativo para revisión interna.

## Límites importantes

- Solo analiza lo que aparece en el CV.
- No garantiza objetividad total ni elimina sesgos por sí mismo.
- No debe usarse como sistema de decisión automática.
- Cualquier resultado requiere revisión humana antes de descartar o avanzar con un candidato.

## Instalación

```bash
cd proyectos/p04-agente-rrhh-candidatos
pip install -r requirements.txt
copy .env.example .env
# Añadir GROQ_API_KEY en el archivo .env
python -m streamlit run app.py
```

## Cómo funciona

```text
Usuario define puesto y competencias
        ↓
Sube uno o varios CVs en PDF
        ↓
La app extrae texto e indexa localmente los CVs
        ↓
Groq genera una evaluación estructurada por candidato
        ↓
Se muestra una criba inicial orientativa con señales, gaps y preguntas de entrevista
```

---

*Portfolio IA Aplicada · José María · Sevilla · 2026*
