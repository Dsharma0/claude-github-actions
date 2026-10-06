# GitHub Actions: Zero to Hero (4 weeks, ~1 hr/day)

Learn by doing. Each stage has: **concepts → example workflow → exercises → checkpoint**.

## Setup (15 min, once)

1. Create a **new public GitHub repo** (public = free Actions minutes), e.g. `gha-practice`.
2. Copy the `app/` folder from this course into the repo root.
3. Workflows live in `.github/workflows/` in your repo. For each stage, copy the example from `workflows/` into that folder, commit, push, and watch the **Actions** tab.
4. Optional: install [`act`](https://github.com/nektos/act) (`brew install act`) to run workflows locally, and `actionlint` (`brew install actionlint`) to lint YAML before pushing.

```bash
mkdir -p .github/workflows
cp workflows/01-hello.yml .github/workflows/
git add . && git commit -m "stage 1" && git push
```

> Tip: only keep the stage you're studying active, or the workflows will all fire at once. Disable others from the Actions tab or delete them.

---

## Roadmap

| Week | Stage | Topic | File |
|---|---|---|---|
| 1 | 1 | Core model: workflow, job, step, runner | `01-hello.yml` |
| 1 | 2 | Triggers, filters, contexts, expressions, outputs | `02-triggers-contexts.yml` |
| 2 | 3 | Real CI: needs, matrix, cache, artifacts, concurrency | `03-ci-matrix-cache.yml` |
| 2 | 4 | Secrets, variables, environments, approvals, OIDC | `04-secrets-environments.yml` |
| 3 | 5 | Reusable workflows and composite actions | `05-*.yml`, `composite-action-greet.yml` |
| 3 | 6 | CI/CD: Docker to GHCR, releases, deploy | `06-cicd-deploy.yml` |
| 4 | 7 | Advanced: PR automation, dynamic matrix, security, services | `07-advanced.yml` |
| 4 | 8 | Capstone project | below |

---

## Stage 1: The core model
**Concepts**
- *Workflow* = a YAML file in `.github/workflows/`. *Event* triggers it. It has one or more *jobs*; each job runs on its own fresh *runner* (VM) and has ordered *steps*. A step is either `run:` (shell) or `uses:` (an action).
- Jobs run in parallel by default. Each starts with an empty machine, so you need `actions/checkout`.

**Exercises**
1. Run `01-hello.yml`. Open the run, expand each step, read the logs.
2. Click **Run workflow** (workflow_dispatch) to trigger it manually.
3. Add a second job `goodbye` that runs on `macos-latest`. Note both jobs run in parallel.
4. Make a step fail (`run: exit 1`). Observe what happens to later steps.
5. Break the YAML indentation on purpose and see how GitHub reports it.

**Checkpoint:** explain the difference between a workflow, job, step, and runner without notes.

---

## Stage 2: Triggers, contexts, expressions
**Concepts**
- Events: `push`, `pull_request`, `schedule` (cron), `workflow_dispatch`, `release`, `issues`, `workflow_run`.
- Filters: `branches`, `tags`, `paths`, `types`.
- `${{ }}` expressions read **contexts**: `github`, `env`, `secrets`, `vars`, `steps`, `needs`, `matrix`, `inputs`, `runner`.
- `if:` conditions, status functions (`always()`, `failure()`), `GITHUB_OUTPUT`, `GITHUB_STEP_SUMMARY`, `GITHUB_ENV`.

**Exercises**
1. Run `02-triggers-contexts.yml` via push, then manually with inputs.
2. Open a PR and confirm the "Only on PRs" step runs.
3. Edit only `README.md` and push: it should NOT trigger (paths-ignore).
4. Add a step that writes `MY_VAR=hi` to `$GITHUB_ENV` and prints it in the *next* step.
5. Add a step that only runs when the commit message contains `[deploy]`: `if: contains(github.event.head_commit.message, '[deploy]')`.

**Checkpoint:** you can answer "why is `env.X` empty here?" (scope) and "why did my step output not show?" (needs `id` + `GITHUB_OUTPUT`).

---

## Stage 3: Real CI
**Concepts**
- `needs` for job ordering and passing outputs.
- `strategy.matrix` to fan out across OS/versions; `include`/`exclude`; `fail-fast`.
- `actions/cache` and `setup-*` built-in caching to speed up runs.
- Artifacts to pass files between jobs / keep build outputs.
- `concurrency` to cancel superseded runs; `timeout-minutes`; `permissions`.

**Exercises**
1. Copy `03-ci-matrix-cache.yml`. Confirm the matrix creates 3 test jobs (windows+20 excluded).
2. Break a test in `app/app.test.js`. See which jobs fail and which get skipped.
3. Run twice and compare cache hit/miss in the logs.
4. Download the `dist` artifact from the run summary page.
5. Push two commits rapidly and watch the first run get cancelled.
6. Add `branches-ignore`-style protection: in repo Settings > Branches, require the `test` check before merging a PR.

**Checkpoint:** a PR cannot merge when tests fail.

---

## Stage 4: Secrets and environments
**Concepts**
- `secrets.*` (encrypted, masked) vs `vars.*` (plain config). Scope: repo, environment, org.
- `GITHUB_TOKEN`: auto-created per run; control with `permissions:`.
- **Environments** add required reviewers, wait timers, branch restrictions, scoped secrets.
- **OIDC**: cloud auth without long-lived keys (`id-token: write`).
- Secrets are not passed to workflows triggered from forked PRs.

**Exercises**
1. Follow the setup notes at the top of `04-secrets-environments.yml`.
2. Run it, approve the `production` deployment from the UI.
3. Try echoing the secret. Then try `echo $MY_SECRET | rev` and note masking limits (never print secrets).
4. Create environment-specific secrets (`staging` and `production` both with `API_URL`) and read them in two jobs.

**Checkpoint:** explain why OIDC beats stored cloud keys.

---

## Stage 5: Reuse
**Concepts**
- **Reusable workflow** (`on: workflow_call`, called with `uses:` at the *job* level): share whole pipelines.
- **Composite action** (`action.yml`, `runs.using: composite`): share a sequence of *steps*.
- Later: JavaScript/Docker actions, and publishing to the Marketplace.

**Exercises**
1. Create `.github/actions/greet/action.yml` from `composite-action-greet.yml`.
2. Copy both `05-*.yml` files, run the caller.
3. Add a new input `name` to the composite action and thread it through.
4. Refactor your Stage 3 `lint` + `test` into one reusable workflow called from two workflows.

**Checkpoint:** know when to pick reusable workflow (jobs) vs composite action (steps).

---

## Stage 6: CI/CD
**Concepts**
- Build and push a container to **GHCR** with `GITHUB_TOKEN` (`packages: write`).
- Tag-triggered releases (`v1.0.0`), `gh release create`.
- Gate deploys with environments; deploy only from `main`.
- Docker layer caching with `type=gha`.

**Exercises**
1. Add a Dockerfile:
   ```dockerfile
   FROM node:22-alpine
   WORKDIR /app
   COPY app/ .
   CMD ["node", "-e", "console.log(require('./app').greet('Docker'))"]
   ```
2. Run `06-cicd-deploy.yml`; find the image under your repo's **Packages**.
3. `git tag v0.1.0 && git push --tags` and watch the release job.
4. Make `deploy-staging` actually deploy somewhere free (GitHub Pages, Fly.io, Render, or a `docker run` over SSH to a VPS).

**Checkpoint:** merge to main produces an image; a tag produces a release.

---

## Stage 7: Advanced
Topics in `07-advanced.yml`: PR automation with `gh`, dynamic matrix via `fromJSON`, least-privilege `permissions: {}`, script-injection prevention, service containers.

**Exercises**
1. Open a PR and see the bot comment.
2. Change the matrix JSON to 5 services; confirm 5 jobs appear.
3. Add a workflow using `on: workflow_run` that fires after CI completes.
4. Add **Dependabot** for actions: `.github/dependabot.yml` with `package-ecosystem: github-actions`.
5. Add CodeQL scanning (Security tab > Code scanning > set up).
6. Install `actionlint` and fix every warning on your workflows.
7. Try a **self-hosted runner** on your Mac (Settings > Actions > Runners). Never use these on public repos with untrusted PRs.

---

## Stage 8: Capstone
Build a complete pipeline for a small app of your choice:

- [ ] PR checks: lint, unit tests (matrix), required status check
- [ ] Cache and artifacts, concurrency cancel
- [ ] Build and push Docker image to GHCR on `main`
- [ ] Auto-deploy to `staging`; manual approval gate for `production`
- [ ] Tag push creates a release with generated notes
- [ ] Reusable workflow plus one composite action in use
- [ ] Nightly scheduled job (e.g. dependency audit)
- [ ] Dependabot, CodeQL, pinned action SHAs, `permissions` set everywhere

---

## Cheat sheet

```yaml
on: [push]                           # trigger
jobs:
  name:
    runs-on: ubuntu-latest           # runner
    needs: [other]                   # ordering
    if: github.ref == 'refs/heads/main'
    env: { KEY: value }
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@v4    # action
      - run: echo hi                 # shell
        id: x
      - run: echo "k=v" >> "$GITHUB_OUTPUT"   # outputs; read: ${{ steps.x.outputs.k }}
      - run: echo "K=v" >> "$GITHUB_ENV"      # env for later steps
```

## Debugging
- Re-run with **Enable debug logging**, or set secret `ACTIONS_STEP_DEBUG=true`.
- `actionlint` catches most syntax and expression mistakes locally.
- `act -j jobname` runs a job locally in Docker (not 100% identical to GitHub).
- Add a `run: env | sort` or `toJSON(github)` step to inspect context.

## Resources
- Docs: https://docs.github.com/actions (start with *Understanding GitHub Actions* and *Workflow syntax*)
- Marketplace: https://github.com/marketplace?type=actions
- Security hardening: https://docs.github.com/actions/security-guides/security-hardening-for-github-actions
- Starter workflows: https://github.com/actions/starter-workflows
