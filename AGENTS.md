# AGENTS.md

This is an **Obsidian vault of Markdown notes** — 18 subjects across languages, databases, infrastructure, and systems design. **No build, test, CI, or package manager exists.** All verification is manual.

## Where To Start

- **Entrypoint**: `00_Vault_MOC.md` lists every subject.
- **Subject MOC**: each subject has `00_MOC/00_<Subject>_MOC.md` — **always read the MOC first** before editing.
- **Directory layout**: `00_MOC/  01_Foundations/  02_Core/  03_Advanced/  04_Playbooks/  05_Projects/  assets/`
- **File numbering**: `01_Topic_Name.md`, `02_Topic_Name.md` within each tier. Keep the scheme when adding files.
- **Exception**: `CICD/Kubernetes/01_Foundations/00_Kubernetes_Components_Reference.md` uses a `00_` prefix (reference table, not a numbered module).

## Size

~470 files, ~320,000 lines across 18 subjects. Largest: React (~30K), SpringBoot (~25K), JavaScript (~24K), SQL (~23K). Smallest: DesignPatterns (~8K), Go (~9K).

## Draft Status

Content files still `status: draft`:
- **Terraform** (10 files) — not yet rebuilt.
- **CICD top-level** (12 stubs: MOC, foundations, core, advanced, playbooks, projects) — cross-tool overview not rewritten.
- **Docker project** `01_Containerize_a_SpringBoot_App_Best_Practices.md` — 1 file.
- **Linux MOC** `00_Linux_MOC.md` — 1 file.
- **TypeScript A04** `04_Typing_Patterns_for_APIs.md` — 1 file.

Index stubs (`*/04_Playbooks/README.md`, `*/05_Projects/README.md`, `*/assets/README.md`) remain `draft` by convention — they are not content.

Everything else (~440 files) is `status: stable`.

## Per-File Conventions

Every content file must include:

1. **YAML frontmatter** with `tags`, `aliases`, `status`, `updated`. Valid statuses: `draft`, `stable`.
2. **Goal callout**: `> [!summary] Goal`.
3. **Anchor-linked ToC**: `## Table of Contents` with `[Section Name](#section-name)` links.
4. **Mermaid diagrams**: at least 2-3 per file (flowcharts, sequence, state, architecture).
5. **Code snippets**: language-specific, runnable in intent.
6. **Definitions**: `> [!tip]` or `> [!info]` callouts for key terms.
7. **Differences tables** wherever two approaches exist.
8. **How-to / when-to / where-to guidance**.
9. **Pitfalls section**: production mistakes and fixes.
10. **Q&A section**: `> [!question]- Interview Questions`.
11. **Cross-Links** using Obsidian wikilinks: `[[Subject/Tier/File_Name]]`.
12. **References** to official docs.

## Editing Rules

- Bump `updated:` to `YYYY-MM-DD` on material changes.
- Change `status: draft` → `stable` only when complete. **Never bulk-change statuses**.
- Cross-note links use full paths: `[[Java/02_Core/03_IO_NIO_and_Serialization]]`. Preserve the linking style of the folder you edit.
- When adding a file, update the subject MOC.
- When deleting or moving a file, find and fix all incoming wikilinks.

## CICD Structure

CICD is a parent directory with tool-specific sibling directories: `AWS`, `Docker`, `GitHub`, `GitHubActions`, `Harness`, `Jenkins`, `Kafka`, `Kubernetes`, `Terraform`. Each has its own MOC at `CICD/<Tool>/00_MOC/`. The top-level `CICD/` MOC is a cross-tool overview stub.

## Content Quality

- `stable` → production-ready (all 12 sections complete).
- `draft` → incomplete or needs review.
- Files under ~100L are likely thin. Average completed file is 250-500L.
- No CI. Verify by:
  - `grep -r "\[\[BrokenLink"` for orphaned flat-named wikilinks
  - `rg "\[\[.*\|.*\]\]"` for piped wikilinks pointing to nonexistent files
  - Spot-read for broken code fences, unbalanced callouts
  - Confirm new files are linked from the subject MOC

## Code Fence Discipline

Code fences are the most common source of rendering bugs. Follow these rules strictly:

### Mermaid Blocks

- Every ` ```mermaid ` block **must** have a closing ` ``` ` on the very next line after the last mermaid content (before any markdown resumes).
- The markdown that follows a mermaid diagram (headings, tables, lists, paragraphs) must sit **outside** both the mermaid opener and closer.
- **Correct pattern:**
  ````text
  ```mermaid
  flowchart LR
      ...
  end
  ```

  ### Next Section

  [markdown content continues...]
  ````
- **Wrong pattern (missing closer):**
  ````text
  ```mermaid
  flowchart LR
      ...
  end

  ### Next Section    ← markdown swallowed into mermaid block
  [markdown content...]
  ````

### Code Blocks

- Every ` ``` ` opening a code block **must** have a matching closing ` ``` `.
- **Never** write two consecutive ` ``` ` fences — they create an empty semantic code block.
- After closing a mermaid block, the next ` ``` ` must explicitly open its own code block.

### Verification

- Count fence lines per file: `grep -c '```' file.md` — must be **even**. An odd count means an unclosed fence.
- Check for double fences: `rg -n '```\n```' --multiline file.md`
- After adding or editing any ` ``` ` fence, run both checks.

## Tooling

Generator scripts (`gen_js.py`, `generate_sql_guides.py`, `JavaScript/*generate*`, `React/*generate*`) are all stubs. **Do not use them.** Prefer direct Markdown edits.

## Repo Reality

- **Not a git repository.** No commits, branches, PRs, or CI.
- No package managers, lockfiles, build configs, or test runners.
- All verification is manual spot-checking.
