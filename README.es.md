# optimize-agents-md

[English](README.md) · **Español**

Skill para agentes de programación (Claude Code y compatibles) que revisa el fichero de
instrucciones del proyecto —`AGENTS.md` o `CLAUDE.md`— y propone una versión que cueste
menos tokens en cada sesión **sin perder ni cambiar ninguna regla**.

## Por qué

Los agentes de programación leen `AGENTS.md` entero al empezar cada sesión. Todo lo que
contiene ocupa memoria de trabajo durante toda la sesión, se use o no. Con el tiempo, el
fichero acumula historia, explicaciones y ejemplos que no hacen falta siempre.

## Qué hace

Mueve, no borra. Reparte el contenido en tres tipos:

- **Siempre necesario** (reglas, prohibiciones, seguridad, despliegue): se queda, palabra por palabra.
- **Necesario solo para ciertas tareas**: se mueve a `docs/agents/`, con una línea que dice cuándo leerlo.
- **Historia y porqués**: se sustituye por una referencia al documento donde ya está.

Un comprobador busca cada regla del original en la propuesta y **falla si alguna ha desaparecido**.
Nada se aplica sin que el usuario diga «apply it» (o «aplícalo»).

## Instalación (Claude Code)

```bash
# desde la raíz de tu proyecto
mkdir -p .claude/skills .claude/commands
cp -r ruta/a/este/repo/skill/optimize-agents-md .claude/skills/
cp ruta/a/este/repo/commands/optimize-agents.md .claude/commands/
```

Abre una sesión nueva para que el agente detecte la skill y el comando.

## Uso

- `/optimize-agents` — revisa solo `AGENTS.md`.
- `/optimize-agents all` — revisa también los demás ficheros de instrucciones. A los documentos
  de registro (ADR, changelogs, bitácoras) no les cambia el contenido: solo añade índices para leer menos.
- `/optimize-agents check` — solo mide y dice si conviene revisar.
- `/optimize-agents ruta/al/fichero.md` — revisa solo ese fichero.

El agente mide, escribe la propuesta en una copia, pasa el comprobador, y te enseña el ahorro
y qué se ha movido. Cuando lo revises, dile «apply it» o pide cambios.

## Aviso automático

La comprobación periódica no gasta tokens: es el script en modo rápido, y nunca modifica nada.

```bash
python3 .claude/skills/optimize-agents-md/scripts/audit_agents.py AGENTS.md --check
```

Sale con 2 si `AGENTS.md` supera 4.000 tokens o ha crecido más de un 20 % desde la última
optimización aprobada (guardada en `.agents-baseline.json`), y con 0 si no. Prográmalo con cron,
systemd, tu CI o un gancho de git, y que te avise cuando salga con 2. Ejemplo con cron, los lunes:

```cron
0 9 * * 1  cd /ruta/al/proyecto && python3 .claude/skills/optimize-agents-md/scripts/audit_agents.py AGENTS.md --check || echo "revisa AGENTS.md" | mail -s agents tu@correo
```

La optimización nunca se lanza sola: el aviso solo sugiere ejecutar `/optimize-agents`.
También puedes comprobarlo a mano con `/optimize-agents check`.

## Probarla sin riesgo

```bash
cd skill/optimize-agents-md/scripts
python3 audit_agents.py ../../../example/AGENTS.md
python3 check_rules.py ../../../example/AGENTS.md ../../../example/AGENTS.proposed.md
```

La propuesta de ejemplo olvida a propósito una regla: el comprobador debe señalarla y salir con código 1.

## Límites

- El comprobador reconoce las reglas por palabras clave (never, always, must, do not, nunca, siempre, prohibido…).
  Una regla escrita sin ellas podría escaparse; por eso también marca las reglas cuya redacción
  cambió. La revisión humana es el último filtro.
- Si el ahorro es menor del 15 %, no propone cambios.
- No añade reglas ni toca código. Los scripts solo leen ficheros; no escriben, no borran, no usan red.
  El único fichero que se escribe, `.agents-baseline.json`, lo actualiza el agente al aplicar una optimización aprobada.
- Las instrucciones de la skill están en inglés, pero funciona con ficheros `AGENTS.md` en español:
  las palabras clave del comprobador cubren inglés y castellano.

## Licencia

MIT. Ver `LICENSE`.
