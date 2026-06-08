# Plan: {objetivo en una oración}

**Fecha**: {YYYY-MM-DD}
**Proyecto**: {nombre del proyecto}
**Alternativa elegida**: {nombre de la alternativa}
**Alternativas descartadas**: 
- {alternativa 2} — {razón en una línea}
- {alternativa 3} — {razón en una línea}

**STATUS**: LISTO_PARA_EJECUCION

---

## Spec

**Objetivo**: {qué se busca lograr}

**No-objetivos**:
- {qué NO se va a hacer}

**Supuestos**:
- {supuesto 1 — a validar en Fase 0}
- {supuesto 2}

---

## Fase 0: Validación de Supuestos

- **Objetivo**: Confirmar que los supuestos del plan son válidos antes de ejecutar cualquier análisis
- **Entregable concreto**: `reports/supuestos_validados.md` con cada supuesto marcado VÁLIDO o INVÁLIDO
- **Criterio de aceptación**: Existe el archivo con todos los supuestos evaluados
- **Esfuerzo estimado**: 1-2h
- **Dependencias**: ninguna
- **Agente ejecutor**: humano / ds-eda

### Tareas
1. Listar todos los supuestos identificados en la spec
2. Para cada supuesto, definir cómo verificarlo (sin mirar datos crudos si es posible)
3. Ejecutar verificación mínima
4. Documentar resultado: VÁLIDO / INVÁLIDO / PARCIAL con evidencia
5. Si hay supuesto INVÁLIDO → re-evaluar plan antes de continuar

---

## Fase 1: {nombre}

- **Objetivo**: {qué se logra al completar esta fase}
- **Entregable concreto**: {archivo específico o resultado verificable}
- **Criterio de aceptación**: {condición binaria — se cumple o no se cumple}
- **Esfuerzo estimado**: {X horas}
- **Dependencias**: {Fase N o "ninguna"}
- **Agente ejecutor**: {ds-eda | ds-feature | ds-model | ds-eval | humano}

### Tareas
1. {verbo + objeto concreto}
2. {verbo + objeto concreto}
3. {verbo + objeto concreto}

---

## Checkpoint de Re-evaluación (después de Fase {N})

Antes de continuar, responder:
- ¿Los resultados de las fases anteriores validan el enfoque?
- ¿Hay hallazgos que cambien las prioridades?
- ¿Alguna fase siguiente necesita ajuste?

---

## Handoff

- **Próxima fase a ejecutar**: Fase 0
- **Agente sugerido**: {agente}
- **Path a este plan**: `plans/PLAN_{fecha}_{tema}.md`
- **Comando sugerido**: `/ds-{agente} ejecutar Fase 0 del plan plans/PLAN_{fecha}_{tema}.md`
