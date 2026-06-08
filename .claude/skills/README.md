# Skills bundleadas para el equipo

Esta carpeta contiene las skills que **la rúbrica del TP pide instalar** (página 5), copiadas dentro del repo para que todo el equipo (Tomás, Agustín, Bautista) las tenga al hacer `git clone` sin que cada uno tenga que hacer el setup global por separado.

## Por qué están acá

`.claude/skills/` es la ubicación que Claude Code reconoce para skills de proyecto — viajan con el repo y se activan automáticamente para cualquier miembro del equipo que abra el proyecto. La alternativa (`~/.claude/skills/`) es solo personal y obliga a cada miembro a hacer el setup por separado.

> Las 5 skills específicas del TP (`/add-decision`, `/check-checkpoint`, `/eda-churn`, `/ml-churn`, `/negocio-ecommerce`) viven en `.claude/commands/` — son una convención más antigua del proyecto, distintas a estas.

## Skills incluidas

### Data Science Kit (10 skills) — autor: `agus-chaud`

Repo upstream: https://github.com/agus-chaud/data-science-kit · Licencia: **Apache 2.0**

| Skill | Para qué |
|-------|----------|
| `ds-env-bootstrap` | Setup de entorno Python reproducible desde la consigna |
| `ds-planner` | Convierte un objetivo ambiguo en fases verificables (no lee datos) |
| `ds-explorer` | EDA + hipótesis de negocio (cada una con test + interpretación + recomendación) |
| `ds-dq` | Calidad de datos con pandas (nulos, duplicados, tipos, cardinalidad) |
| `ds-stats` | Marco inferencial — elección de tests, IC, p-valores, supuestos |
| `ds-feature` | Feature engineering con dos modos (ML / negocio), sin leakage |
| `ds-model` | Entrenamiento + comparación; baseline dummy obligatorio, criterio antes de resultados |
| `ds-reviewer` | QA crítico independiente — no escribe código, solo flagea con severidad |
| `ds-report` | Traduce hallazgos técnicos a un reporte ejecutivo (4-6 pp, sin jerga) |
| `gentleman` | Tutor senior con voz argentina para explicar conceptos |

### grill-me — autor: `mattpocock`

Fuente original: https://skills.sh/mattpocock/skills/grill-me

Te interroga sobre cualquier plan o decisión hasta llegar a entendimiento compartido. La rúbrica la pide explícitamente (página 3): "Si no podés responderlas, usá la skill grill-me".

## Cómo se invocan

Cualquier miembro del equipo con el repo clonado las puede usar:
- Escribiendo el slash directamente: `/ds-plan`, `/ds-explore`, `/ds-model`, `/ds-report`, `/ds-review`, `/ds-feature`, `/ds-stats`, `/ds-dq`, `/ds-env-bootstrap`, `/gentleman`, `/grill-me`
- O dejando que Claude Code las detecte automáticamente cuando el contexto matchea su trigger

## Modificaciones

**Ninguna.** Las skills están idénticas a la versión upstream al momento del clone (`2026-06-07`). Si Agustín Chaud o Matt Pocock publican actualizaciones, hay que re-bundlearlas (ver abajo).

## Cómo actualizar desde upstream

Si en el futuro hay una versión nueva del data-science-kit:

```bash
# Desde la raíz del repo churn_tp
rm -rf .claude/skills/ds-*
rm -rf .claude/skills/gentleman
git clone https://github.com/agus-chaud/data-science-kit.git /tmp/dsk
cp -r /tmp/dsk/skills/ds-* .claude/skills/
cp -r /tmp/dsk/skills/gentleman .claude/skills/
rm -rf /tmp/dsk

# Verificar y commitear
git status
git add .claude/skills/
git commit -m "chore: actualiza skills del data-science-kit a la última versión"
```

Para grill-me se reinstala desde https://skills.sh/mattpocock/skills/grill-me.

## Atribución

- **Data Science Kit** © Agustín Chaud — Apache 2.0 License — https://github.com/agus-chaud/data-science-kit
- **grill-me** © Matt Pocock — https://skills.sh/mattpocock/skills/grill-me

Esta carpeta redistribuye obras de terceros conservando autor y licencia. Si reusás este enfoque de bundling, mantené la atribución original.
