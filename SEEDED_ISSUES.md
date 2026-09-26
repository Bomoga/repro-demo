# Seeded issues

Every issue in this repo is planted on purpose for the Repro demo. Every secret is fake.

## Inventory before the rebuild (commit 21291de)

Checked against the detectors Repro actually runs: the Semgrep registry packs `p/javascript`,
`p/typescript`, `p/python`, Repro's `privacy-patterns` pack, gitleaks, and osv-scanner.

| File | Issue | Detector that should catch it | Caught? |
|---|---|---|---|
| `src/assistant.js:7` | Prompt logged to the console unredacted | `privacy-patterns` (`privacy.prompt-logging.js`) | Yes |
| `src/assistant.js:8` | Prompt sent to the model provider | `privacy-patterns` (third-party forwarding) | No: the URL comes from config, and the provider is the tool's disclosed purpose anyway |
| `src/config.js:5` | Hardcoded `sk-demo-...` API key | gitleaks | No: gitleaks' generic rule ignores values containing stopwords like "demo" |
| `src/db.js:6,11` | SQL built by string concatenation | Semgrep | No: registry SQL rules only match specific clients (pg, mysql, knex) or framework request sources |

No "obvious fix is wrong" bug was seeded yet. Raw `semgrep --config p/default` found nothing and
raw gitleaks found no leaks, so there was no opening "wall of findings" either.
