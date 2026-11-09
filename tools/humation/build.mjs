import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";
import { getPartsForSlot } from "@humation/core";
import { humation1 } from "@humation/assets-humation-1";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const slots = ["head", "body", "bottom", "item", "glasses"];
const catalog = Object.fromEntries(
  slots.map((slot) => [
    slot,
    getPartsForSlot(humation1, slot).map(({ id, name }) => ({ id, name })),
  ]),
);

await mkdir(resolve(root, "static", "vendor"), { recursive: true });
await writeFile(
  resolve(root, "static", "vendor", "humation-parts.json"),
  `${JSON.stringify(catalog, null, 2)}\n`,
);
await build({
  entryPoints: [resolve(dirname(fileURLToPath(import.meta.url)), "src.js")],
  outfile: resolve(root, "static", "js", "humation-avatar.js"),
  bundle: true,
  format: "iife",
  platform: "browser",
  target: ["es2020"],
  minify: true,
  legalComments: "inline",
});
