# add-decision

Agrega una nueva entrada al archivo `decisions.md` del proyecto de churn.

El usuario te va a dar (o inferís del contexto):
- **Qué decidió**: la decisión tomada
- **Por qué**: la justificación de negocio
- **Alternativas descartadas**: qué otras opciones evaluó
- **Consecuencias**: qué implica esta decisión para el resto del proyecto

Si el usuario no te da toda la información, **preguntale específicamente qué falta** antes de escribir. No inventes justificaciones.

Una vez que tenés todo, agregá al final de `decisions.md` una nueva sección con este formato exacto:

```markdown
---

## Decisión — [título breve en 4-6 palabras]

1. **Qué decidí:** [una oración clara]
2. **Por qué:** [justificación de negocio, no técnica]
3. **Alternativas que descarté:** [lista con guión, mínimo una]
4. **Consecuencias:** [qué implica esta decisión para el modelo o el análisis]
```

Después de escribirlo, confirmá que quedó bien leyendo el archivo y mostrá el fragmento agregado.
