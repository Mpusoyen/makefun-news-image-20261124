// Entrypoint for the Tuesday Ledger v4 news-image entry.
//
// The finished artwork already sits in entry.png beside this file.
// The grader expects those exact bytes at <output dir>/entry.png,
// where the output dir comes from MAKEFUN_OUTPUT_DIR when set and
// falls back to /output inside the grading container.

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });

const target = join(outDir, "entry.png");
copyFileSync(source, target);
console.log(`wrote ${target} (${statSync(target).size} bytes)`);
