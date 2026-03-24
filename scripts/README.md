# Scripts

Repo maintenance helpers. Run from the **repository root** unless noted.

---

## `check-contract-sync.mjs`

Ensures **`packages/types/package.json` `version`** matches **`packages/types/contracts.json`**.

Python (`apps/server`) reads the same contract version via `app/contracts/version.py`.

```bash
node scripts/check-contract-sync.mjs
```

**npm (root):**

```bash
npm run check:contract
```

Use in CI before build/deploy.

---

## Adding scripts

Keep this folder small: one purpose per file, no shell spaghetti. Prefer Node for cross-platform paths.
