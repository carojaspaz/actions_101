# Tutorial: Sincronización bidireccional de Issues entre dos organizaciones (AO ↔ NO) con GitHub Actions (Paso 1 al 12)

> Objetivo: Para el demo, cuando se cree o edite un Issue en cualquiera de los repos demo, se cree y mantenga sincronizado su **Issue espejo** en la otra organización, incluyendo:
>
> - Creación automática del espejo (Paso 10)
> - Sincronización bidireccional de **título** y **descripción** (Paso 11)
> - Sincronización bidireccional de **labels** y **assignees** (Paso 12)
>
> **Fuera de alcance en este tutorial (por ahora):** sincronización de Projects v2 (Status/campos), comentarios, milestones, etc.

---

## Contexto del demo

- Organización AO (Akaxa): `akaxaorg`
- Organización NO (Nayra): `nayraorg`

Projects (ambos **Projects v2** a nivel organización):
- AO: **Akaxa Backend**
- NO: **Nayra Backend**

Repos demo (origen de Issues):
- AO repo: `akaxaorg/ao_backend_demo`
- NO repo: `nayraorg/no_backend_demo`

Secret compartido:
- `SYNC_PAT` (Classic PAT) en **ambos repos**

Label técnico:
- `synced` (para trazabilidad y prevención de bucles)

Marcador en body:
- `Mirror: <URL del issue espejo>`

---

# Paso 0 (preparación): agregar repositorio al Project (Projects v2)

> Este paso se ejecutó para permitir que el Project NO trabaje con Issues reales del repo.

En el Project **Nayra Backend**:
1. Abrir la organización `nayraorg`
2. Entrar al Project **Nayra Backend**
3. `⋯` → **Settings**
4. **Repositories** → **Add repositories**
5. Seleccionar `nayraorg/no_backend_demo`
6. Validación: crear un Issue en `no_backend_demo` y verificar que puede agregarse al Project

---

# Paso 1: confirmar que los Projects son v2 y que trabajas con Issues reales

Checklist:
- URL estilo `https://github.com/orgs/<org>/projects/<n>`
- Vistas tipo **Table / Board / Roadmap**
- Campos configurables (incluyendo `Status`)
- Los items son **Issues reales** (no drafts como mecanismo principal)

Resultado esperado:
- **Akaxa Backend** y **Nayra Backend** son Projects v2 a nivel organización y trabajan con Issues reales.

---

# Paso 2: definir el evento detonante de la sincronización (Opción A)

Decisión tomada:
- **Opción A**: la sincronización se detona por la **creación del Issue** (`issues.opened`)

---

# Paso 3: definir llave de sincronización y prevención de bucles (Opción A)

Decisión tomada:
- **Opción A**: usar **Body marker + label técnico**
  - En el body: `Mirror: <url>`
  - Label: `synced`

Objetivo:
- Poder identificar el Issue espejo de forma inequívoca
- Evitar loops y duplicados

---

# Paso 4: credencial cross-org (PAT)

Decisión tomada:
- Usar **Classic Personal Access Token (PAT)** para evitar limitaciones de Fine-grained tokens (resource owner por org).

Scopes recomendados para el PAT (demo):
- `repo`
- `project`
- `read:org`

> Nota: Fine-grained PAT no permite un único token que vea repos de múltiples organizaciones como owner.

---

# Paso 5: dónde vive la automatización (Opción A)

Decisión tomada:
- Workflows en **ambos repos**
  - AO: workflows en `akaxaorg/ao_backend_demo`
  - NO: workflows en `nayraorg/no_backend_demo`

Ventaja:
- Bidireccionalidad natural y depuración por lado.

---

# Paso 6: delimitar scope (repos origen) y target de Projects

Repos origen definidos (para demo):
- AO: `akaxaorg/ao_backend_demo`
- NO: `nayraorg/no_backend_demo`

Target Projects definidos:
- AO: **Akaxa Backend**
- NO: **Nayra Backend**

> En pasos 1–12 no sincronizamos Projects v2 aún; solo Issues.

---

# Paso 7: crear el PAT y guardarlo como secret

## 7.1 Crear Classic PAT (en la cuenta del usuario)
Ruta:
- **Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token**

Config:
- Name: `AO-NO-project-sync-demo`
- Expiration: a elección (demo)
- Scopes: `repo`, `project`, `read:org`

## 7.2 Guardar como secret en ambos repos
En **cada repo**:
- Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `SYNC_PAT`
- Secret: pegar el valor del PAT

---

# Paso 8: verificación rápida de owner real (org login)

Para llamadas API/CLI, usar el **login real**:
- `akaxaorg` (NO usar “AO” en la API)
- `nayraorg` (NO usar “NO” en la API)

Esto evita errores tipo:
- `404 Not Found` por owner incorrecto

---

# Paso 9: prueba manual cross-org (workflow_dispatch)

Objetivo:
- Probar que el PAT puede crear Issues cross-org antes de automatizar `issues.opened`.

Acción:
- Ejecutar workflows manuales en AO y NO que creen un Issue en la otra org usando `SYNC_PAT`.

Resultado esperado:
- El Issue se crea correctamente en el repo destino.
- El run queda en verde y confirma permisos cross-org.

---

# Paso 10: automatizar creación del Issue espejo (issues.opened)

Objetivo:
- Cuando se crea un Issue nuevo en AO o NO, se crea automáticamente el espejo en el otro repo, y se marca:
  - `Mirror: <url>`
  - label `synced`

## 10.1 Reglas anti-bucle
Antes de replicar:
- Si el body contiene `Mirror:` → **skip**
- Si el Issue tiene label `synced` → **skip**

## 10.2 Workflows (uno por repo)
Colocar estos workflows en ambos repos:

### AO: `akaxaorg/ao_backend_demo/.github/workflows/sync-on-issue-opened-to-no.yml`
```yaml
name: Sync - On Issue Opened (AO -> NO)

on:
  issues:
    types: [opened]

permissions:
  contents: read

jobs:
  mirror_to_no:
    runs-on: ubuntu-latest
    steps:
      - name: Install jq
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Mirror issue to NO (create + link + label)
        env:
          GH_TOKEN: ${{ secrets.SYNC_PAT }}

          SOURCE_OWNER: "akaxaorg"
          SOURCE_REPO: "ao_backend_demo"

          TARGET_OWNER: "nayraorg"
          TARGET_REPO: "no_backend_demo"

          SYNC_LABEL: "synced"

          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ISSUE_TITLE: ${{ github.event.issue.title }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          ISSUE_HTML_URL: ${{ github.event.issue.html_url }}
        run: |
          set -euo pipefail

          body="${ISSUE_BODY:-}"

          # Guards
          if echo "$body" | grep -qiE '^[[:space:]]*Mirror:'; then
            echo "Skip: already contains Mirror."
            exit 0
          fi

          labels_json="$(gh api "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}" --jq '.labels[].name' || true)"
          if echo "$labels_json" | grep -qx "${SYNC_LABEL}"; then
            echo "Skip: already has '${SYNC_LABEL}'."
            exit 0
          fi

          # Create mirror
          mirror_json="$(gh api -X POST "repos/${TARGET_OWNER}/${TARGET_REPO}/issues"             -f title="${ISSUE_TITLE}"             -f body="Mirror: ${ISSUE_HTML_URL}

---

${body}")"

          mirror_number="$(echo "$mirror_json" | jq -r '.number')"
          mirror_url="$(echo "$mirror_json" | jq -r '.html_url')"

          echo "Mirror created: ${mirror_url} (#${mirror_number})"

          # Update source with Mirror marker
          updated_source_body="Mirror: ${mirror_url}

---

${body}"
          gh api -X PATCH "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}"             -f body="${updated_source_body}" >/dev/null

          # Label both
          gh api -X POST "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}/labels"             -f labels[]="${SYNC_LABEL}" >/dev/null

          gh api -X POST "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${mirror_number}/labels"             -f labels[]="${SYNC_LABEL}" >/dev/null

          echo "Done."
```

### NO: `nayraorg/no_backend_demo/.github/workflows/sync-on-issue-opened-to-ao.yml`
```yaml
name: Sync - On Issue Opened (NO -> AO)

on:
  issues:
    types: [opened]

permissions:
  contents: read

jobs:
  mirror_to_ao:
    runs-on: ubuntu-latest
    steps:
      - name: Install jq
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Mirror issue to AO (create + link + label)
        env:
          GH_TOKEN: ${{ secrets.SYNC_PAT }}

          SOURCE_OWNER: "nayraorg"
          SOURCE_REPO: "no_backend_demo"

          TARGET_OWNER: "akaxaorg"
          TARGET_REPO: "ao_backend_demo"

          SYNC_LABEL: "synced"

          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ISSUE_TITLE: ${{ github.event.issue.title }}
          ISSUE_BODY: ${{ github.event.issue.body }}
          ISSUE_HTML_URL: ${{ github.event.issue.html_url }}
        run: |
          set -euo pipefail

          body="${ISSUE_BODY:-}"

          # Guards
          if echo "$body" | grep -qiE '^[[:space:]]*Mirror:'; then
            echo "Skip: already contains Mirror."
            exit 0
          fi

          labels_json="$(gh api "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}" --jq '.labels[].name' || true)"
          if echo "$labels_json" | grep -qx "${SYNC_LABEL}"; then
            echo "Skip: already has '${SYNC_LABEL}'."
            exit 0
          fi

          # Create mirror
          mirror_json="$(gh api -X POST "repos/${TARGET_OWNER}/${TARGET_REPO}/issues"             -f title="${ISSUE_TITLE}"             -f body="Mirror: ${ISSUE_HTML_URL}

---

${body}")"

          mirror_number="$(echo "$mirror_json" | jq -r '.number')"
          mirror_url="$(echo "$mirror_json" | jq -r '.html_url')"

          echo "Mirror created: ${mirror_url} (#${mirror_number})"

          # Update source with Mirror marker
          updated_source_body="Mirror: ${mirror_url}

---

${body}"
          gh api -X PATCH "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}"             -f body="${updated_source_body}" >/dev/null

          # Label both
          gh api -X POST "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}/labels"             -f labels[]="${SYNC_LABEL}" >/dev/null

          gh api -X POST "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${mirror_number}/labels"             -f labels[]="${SYNC_LABEL}" >/dev/null

          echo "Done."
```

---

# Paso 11: sincronizar ediciones (título + body) bidireccional (issues.edited)

Objetivo:
- Si se edita `title` o `body` del Issue origen, actualizar el espejo.

Evento:
- `issues: [edited]`

Guards:
- Skip si `github.actor == github-actions[bot]`
- Skip si no tiene label `synced`
- Skip si no contiene `Mirror:`

Idempotencia:
- Si el target ya tiene el mismo `title` y body calculado, no hace PATCH.

## Workflow (mismo archivo en ambos repos)
**Archivo:** `.github/workflows/sync-on-issue-edited.yml`

```yaml
name: Sync - On Issue Edited (Bidirectional)

on:
  issues:
    types: [edited]

permissions:
  contents: read

jobs:
  sync_issue_edits:
    runs-on: ubuntu-latest
    steps:
      - name: Install jq
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Sync title/body to mirror issue
        env:
          GH_TOKEN: ${{ secrets.SYNC_PAT }}
          SYNC_LABEL: "synced"
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ACTOR: ${{ github.actor }}
          REPO_FULL: ${{ github.repository }}
          SOURCE_HTML_URL: ${{ github.event.issue.html_url }}
        run: |
          set -euo pipefail

          if [ "${ACTOR}" = "github-actions[bot]" ]; then
            echo "Skip: edit made by github-actions[bot]."
            exit 0
          fi

          SOURCE_OWNER="${REPO_FULL%%/*}"
          SOURCE_REPO="${REPO_FULL##*/}"

          source_json="$(gh api "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}")"
          source_title="$(echo "$source_json" | jq -r '.title')"
          source_body="$(echo "$source_json" | jq -r '.body // ""')"

          has_label="$(echo "$source_json" | jq -r --arg L "${SYNC_LABEL}" '[.labels[].name] | index($L) != null')"
          if [ "$has_label" != "true" ]; then
            echo "Skip: missing '${SYNC_LABEL}'."
            exit 0
          fi

          mirror_url="$(echo "$source_body" | awk '/^[[:space:]]*Mirror:[[:space:]]*/ {sub(/^[[:space:]]*Mirror:[[:space:]]*/, "", $0); print; exit}')"
          if [ -z "${mirror_url}" ]; then
            echo "Skip: no Mirror marker."
            exit 0
          fi

          if [[ ! "${mirror_url}" =~ github\.com/([^/]+)/([^/]+)/issues/([0-9]+) ]]; then
            echo "Error: Mirror URL not recognized: ${mirror_url}"
            exit 1
          fi

          TARGET_OWNER="${BASH_REMATCH[1]}"
          TARGET_REPO="${BASH_REMATCH[2]}"
          TARGET_NUMBER="${BASH_REMATCH[3]}"

          # Extract content after standard header
          content="$(printf "%s" "$source_body" | awk '
            BEGIN {state=0}
            state==0 && $0 ~ /^[[:space:]]*Mirror:/ {state=1; next}
            state==1 && $0 ~ /^[[:space:]]*$/ {next}
            state==1 && $0 ~ /^---[[:space:]]*$/ {state=2; next}
            state==2 && $0 ~ /^[[:space:]]*$/ {state=3; next}
            state>=1 {print}
          ')"
          if [ -z "${content}" ]; then
            content="$source_body"
          fi

          desired_body="Mirror: ${SOURCE_HTML_URL}"$'\n\n---\n\n'"${content}"

          target_json="$(gh api "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${TARGET_NUMBER}")"
          target_title="$(echo "$target_json" | jq -r '.title')"
          target_body="$(echo "$target_json" | jq -r '.body // ""')"

          if [ "${target_title}" = "${source_title}" ] && [ "${target_body}" = "${desired_body}" ]; then
            echo "No changes to apply."
            exit 0
          fi

          gh api -X PATCH "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${TARGET_NUMBER}"             -f title="${source_title}"             -f body="${desired_body}" >/dev/null

          echo "Done."
```

---

# Paso 12: sincronizar labels y assignees bidireccional

Objetivo:
- Cuando cambien labels o assignees en el Issue origen, aplicar el set completo al espejo.

Evento:
- `issues: [labeled, unlabeled, assigned, unassigned]`

Guards:
- Skip si `github.actor == github-actions[bot]`
- Skip si no tiene label `synced`
- Skip si no contiene `Mirror:`

Idempotencia:
- Comparar arrays (labels/assignees) y solo actualizar si difieren.

## Workflow (mismo archivo en ambos repos)
**Archivo:** `.github/workflows/sync-on-issue-labels-assignees.yml`

```yaml
name: Sync - Labels & Assignees (Bidirectional)

on:
  issues:
    types: [labeled, unlabeled, assigned, unassigned]

permissions:
  contents: read

jobs:
  sync_labels_assignees:
    runs-on: ubuntu-latest
    steps:
      - name: Install jq
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Sync labels and assignees to mirror issue
        env:
          GH_TOKEN: ${{ secrets.SYNC_PAT }}
          SYNC_LABEL: "synced"
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          ACTOR: ${{ github.actor }}
          REPO_FULL: ${{ github.repository }}
        run: |
          set -euo pipefail

          if [ "${ACTOR}" = "github-actions[bot]" ]; then
            echo "Skip: github-actions[bot]."
            exit 0
          fi

          SOURCE_OWNER="${REPO_FULL%%/*}"
          SOURCE_REPO="${REPO_FULL##*/}"

          source_json="$(gh api "repos/${SOURCE_OWNER}/${SOURCE_REPO}/issues/${ISSUE_NUMBER}")"
          source_body="$(echo "$source_json" | jq -r '.body // ""')"

          has_label="$(echo "$source_json" | jq -r --arg L "${SYNC_LABEL}" '[.labels[].name] | index($L) != null')"
          if [ "$has_label" != "true" ]; then
            echo "Skip: missing '${SYNC_LABEL}'."
            exit 0
          fi

          mirror_url="$(echo "$source_body" | awk '/^[[:space:]]*Mirror:[[:space:]]*/ {sub(/^[[:space:]]*Mirror:[[:space:]]*/, "", $0); print; exit}')"
          if [ -z "${mirror_url}" ]; then
            echo "Skip: no Mirror marker."
            exit 0
          fi

          if [[ ! "${mirror_url}" =~ github\.com/([^/]+)/([^/]+)/issues/([0-9]+) ]]; then
            echo "Error: Mirror URL format not recognized: ${mirror_url}"
            exit 1
          fi

          TARGET_OWNER="${BASH_REMATCH[1]}"
          TARGET_REPO="${BASH_REMATCH[2]}"
          TARGET_NUMBER="${BASH_REMATCH[3]}"

          desired_labels_json="$(echo "$source_json" | jq -c --arg L "${SYNC_LABEL}" '
            ([.labels[].name] | unique) as $labs |
            (if ($labs | index($L)) == null then ($labs + [$L]) else $labs end)
          ')"

          desired_assignees_json="$(echo "$source_json" | jq -c '[.assignees[].login] | unique')"

          target_json="$(gh api "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${TARGET_NUMBER}")"
          target_labels_json="$(echo "$target_json" | jq -c '[.labels[].name] | unique')"
          target_assignees_json="$(echo "$target_json" | jq -c '[.assignees[].login] | unique')"

          labels_need_update="false"
          assignees_need_update="false"

          if [ "${target_labels_json}" != "${desired_labels_json}" ]; then
            labels_need_update="true"
          fi

          if [ "${target_assignees_json}" != "${desired_assignees_json}" ]; then
            assignees_need_update="true"
          fi

          if [ "${labels_need_update}" = "false" ] && [ "${assignees_need_update}" = "false" ]; then
            echo "No changes to apply."
            exit 0
          fi

          if [ "${labels_need_update}" = "true" ]; then
            printf '{"labels": %s}\n' "${desired_labels_json}" |               gh api -X PATCH "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${TARGET_NUMBER}"                 --input - >/dev/null
          fi

          if [ "${assignees_need_update}" = "true" ]; then
            printf '{"assignees": %s}\n' "${desired_assignees_json}" |               gh api -X PATCH "repos/${TARGET_OWNER}/${TARGET_REPO}/issues/${TARGET_NUMBER}"                 --input - >/dev/null
          fi

          echo "Done."
```

---

## Próximo paso
**Paso 13:** sincronizar **Status** en Projects v2 (requiere GraphQL y IDs de Project/Field/Options).
