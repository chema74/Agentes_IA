# Security Rotation Playbook

## Incident summary

On 2026-04-15, API keys were detected in Git history under:

- `proyectos/p04-agente-rrhh-candidatos/.env`
- `proyectos/p08-rag-normativa-comercio/.env`

History was rewritten to remove those files from all commits.

## Immediate actions (mandatory)

1. Revoke exposed keys in provider dashboards:
   - Groq key (prefix `gsk_...`)
   - Tavily key (prefix `tvly-...`)
2. Generate new keys.
3. Update local `.env` files only (never commit).

## Publish rewritten history

After history rewrite, push with force lease:

```bash
git push origin --force-with-lease main
```

If other rewritten branches must be published:

```bash
git push origin --force-with-lease --all
git push origin --force-with-lease --tags
```

## Team recovery steps

All collaborators must sync to the rewritten history:

```bash
git fetch origin --prune
git checkout main
git reset --hard origin/main
```

If they have local feature branches, they should rebase/cherry-pick on top of new `origin/main`.

## Verification commands

Run from repository root:

```bash
# secret pattern scan in all reachable commits
git rev-list --all | while read c; do
  git grep -n -E "gsk_[A-Za-z0-9]{20,}|tvly-[A-Za-z0-9-]{20,}" "$c" || true
done
```

Expected: no matches.

## Prevention checklist

- Keep `.env` ignored globally (`.gitignore` at repo root).
- Use `.env.example` for templates only (no real keys).
- Run secret scan before push in CI/local hooks.

