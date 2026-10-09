# GluMee

App Android para seguimiento de glucosa, alimentación y actividad física, con análisis de menús de restaurante mediante un VLM (Gemini).

Proyecto de titulación - CETI Colomos - Ingeniería en Desarrollo de Software.
Autoras: Gabriela Jireh Arambula Cruz, Ana Sofía Guerrero Ruiz Velasco.

> GluMee es exclusivamente informativa. No diagnostica ni sustituye a un profesional de la salud.

## Estructura
- `mobile/`  App React Native (Expo)
- `backend/` API FastAPI
- `docs/`    Charter, arquitectura, decisiones
- `spike/`   Experimento del VLM con menús reales

## Flujo de trabajo (GitHub Flow)
1. `main` siempre estable. No se hace push directo.
2. Una rama por tarea: `feature/nombre-corto`.
3. Pull Request revisados.
4. Commits claros: `feat:`, `fix:`, `docs:`, `chore:`.