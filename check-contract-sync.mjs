#!/usr/bin/env node
/**
 * Fails if packages/types/contracts.json version !== packages/types/package.json version.
 * Run: node check-contract-sync.mjs  (or npm run check:contract)
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(readFileSync(join(root, "packages/types/package.json"), "utf8"));
const contract = JSON.parse(readFileSync(join(root, "packages/types/contracts.json"), "utf8"));

if (pkg.version !== contract.version) {
  console.error(`Contract drift: package.json ${pkg.version} !== contracts.json ${contract.version}`);
  process.exit(1);
}
console.log(`Contract OK: ${contract.version}`);
