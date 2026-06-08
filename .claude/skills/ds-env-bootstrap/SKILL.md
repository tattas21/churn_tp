---
name: ds-env-bootstrap
description: Detecta dependencias probables para proyectos de data science a partir de una consigna y crea un entorno Python reproducible. Use when el usuario pide preparar entorno, instalar librerías, bootstrap de proyecto, setup de notebook, o menciona "crear entorno", "requirements", "venv", "TP", "consigna".
metadata:
  author: agus-chaud
---

# DS Environment Bootstrap

## Objetivo
Crear un entorno ejecutable desde cero para alumnos, priorizando **reproducibilidad fuerte** con lockfile congelado.
Regla clave: todos instalan desde el mismo `requirements.txt` pinneado.

## Cuándo usar esta skill
- Cuando el usuario arranca un TP/proyecto DS y no tiene entorno listo.
- Cuando hay consigna en `.docx`, `.txt` o markdown y hay que inferir stack.
- Cuando piden `requirements.txt` reproducible para clase/equipo.

## Workflow
1. Mantener un `requirements.in` (top-level sin pin).
2. Ejecutar el script para instalar + congelar en `requirements.txt`.
3. En máquinas de alumnos, instalar siempre desde `requirements.txt` lockeado.
4. Verificar instalación y guardar resumen en `reports/setup_env_report.md`.

## Script utilitario
Usar `scripts/infer_and_setup_env.py`.

### Comando recomendado
```bash
python .cursor/skills/ds-env-bootstrap/scripts/infer_and_setup_env.py --env-name churn.env --base-requirements requirements.in --requirements requirements.txt --refresh-lock
```

### En alumnos (reusar lock sin recalcular)
```bash
python .cursor/skills/ds-env-bootstrap/scripts/infer_and_setup_env.py --env-name churn.env --requirements requirements.txt
```

### Bootstrap inicial desde consigna (solo si no tenés requirements.in)
```bash
python .cursor/skills/ds-env-bootstrap/scripts/infer_and_setup_env.py --env-name churn.env --bootstrap-spec TP_Churn_Consigna.docx --allow-risky --refresh-lock
```

### Qué hace
- Crea entorno virtual si no existe.
- Instala desde lockfile (`requirements.txt`) si ya existe.
- Si se pide `--refresh-lock`, instala base y regenera lockfile con `pip freeze --exclude-editable`.
- Soporta bootstrap opcional desde consigna solo como paso inicial.
- Instala dependencias con `pip`.
- Ejecuta una verificación mínima de imports.

## Criterios de éxito
- Existe `.venv` activo/creado.
- Existe `requirements.txt` lockeado con versiones exactas.
- Instalar dependencias termina sin errores.
- Verificación de imports principales pasa.

## Notas
- Si el lockfile existe, el script lo reutiliza por defecto.
- Para cambiar versiones, editar `requirements.in` y ejecutar `--refresh-lock`.
- Evitar subir `venv` a GitHub: versionar `requirements.in` + `requirements.txt`.

## Integración con Gentleman Mode

Referencia obligatoria de estilo: `skills/gentleman/SKILL.md`.

- Comunicar decisiones de entorno con tono de mentor técnico: directo, didáctico y con foco en reproducibilidad.
- Enfatizar los trade-offs (velocidad vs reproducibilidad) y evitar atajos frágiles.

## Regla transversal de hipótesis
- Si durante el setup aparece la necesidad de **plantear, refinar o validar hipótesis** (de negocio o estadísticas), derivar a la skill `ds-stats` antes de continuar.
