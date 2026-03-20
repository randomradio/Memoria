<div align="center">
  <img src="assets/memoria-logo.png" alt="Memoria Logo" width="300"/>
  
  # Memoria
  
  **Secure · Auditable · Programmable Memory for AI Agents**
  
  [![MatrixOne](https://img.shields.io/badge/Powered%20by-MatrixOne-00ADD8?style=flat-square&logo=database)](https://github.com/matrixorigin/matrixone)
  [![MCP](https://img.shields.io/badge/Protocol-MCP-7C3AED?style=flat-square)](https://modelcontextprotocol.io)
  [![Git for Data](https://img.shields.io/badge/Git%20for%20Data-Enabled-00A3CC?style=flat-square)](https://github.com/matrixorigin/matrixone)
  [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](LICENSE)
  
  [See It in Action](#see-git-for-data-in-action) · [Quick Start](#quick-start) · [Steering Rules](#steering-rules) · [API Reference](#api-reference) · [For AI Agents](#for-ai-agents)
  
</div>

---

## Overview

Memoria is a **persistent memory layer** for AI agents with Git-level version control.
Every memory change is tracked, auditable, and reversible — snapshots, branches, merges, and time-travel rollback, all powered by MatrixOne's native Copy-on-Write engine.

**Core Capabilities:**
- **Cross-conversation memory** — preferences, facts, and decisions persist across sessions
- **Semantic search** — retrieves memories by meaning, not just keywords
- **Git for Data** — zero-copy branching, instant snapshots, point-in-time rollback
- **Audit trail** — every memory mutation has a snapshot + provenance chain
- **Self-maintaining** — built-in governance detects contradictions, quarantines low-confidence memories
- **Private by default** — local embedding model option, no data leaves your machine

**Supported Agents:** [Kiro](https://kiro.dev) · [Cursor](https://cursor.sh) · [Claude Code](https://docs.anthropic.com/en/docs/claude-code) · [Codex](https://openai.com/index/introducing-codex/) · [OpenClaw](plugins/openclaw/README.md) · Any MCP-compatible agent

**Storage Backend:** [MatrixOne](https://github.com/matrixorigin/matrixone) — Distributed database with native vector indexing

---

## See Git for Data in Action

<p align="center">
  <img src="assets/git4data-story-writing-demo.svg" alt="Animated Memoria Git-for-Data demo showing an author branching a story draft, merging a better plot direction into the main storyline, and rolling back the last two unsatisfying beats." width="100%"/>
</p>

A story-writing scenario makes the core idea visible faster: an author already has a few accepted story-memory nodes, then opens an experimental branch to try a different plot direction. When the branch feels better, it is merged into the main storyline. Later, if the newest beats do not work, the author rolls back to an earlier snapshot and keeps writing from there.

**What the demo shows:**
- **Main storyline** — accepted story beats live on `main`
- **Experimental branch** — the author tries a new plot turn without rewriting canon
- **Merge** — the stronger draft is promoted back into the main storyline
- **Rollback** — the last two bad turns are discarded, and writing resumes from a safe snapshot

---

## Why Memoria?

| Capability | Memoria | Letta / Mem0 / Traditional RAG |
|---|---|---|
| Git-level version control | Native zero-copy snapshots & branches | File-level or none |
| Isolated experimentation | One-click branch, merge after validation | Manual data duplication |
| Audit trail | Full snapshot + provenance on every mutation | Limited logging |
| Semantic retrieval | Vector + full-text hybrid search | Vector only |
| Self-governance | Automatic contradiction detection & quarantine | Manual cleanup |

---

## Quick Start

### 1. Start MatrixOne

```bash
git clone https://github.com/matrixorigin/Memoria.git
cd Memoria
docker compose up -d
```

Or use [MatrixOne Cloud](https://cloud.matrixorigin.cn) (free tier, no Docker needed).

### 2. Install Memoria

```bash
curl -sSL https://raw.githubusercontent.com/matrixorigin/Memoria/main/scripts/install.sh | bash
```

Or download from [GitHub Releases](https://github.com/matrixorigin/Memoria/releases).

### 3. Configure your AI tool

```bash
cd your-project
memoria init -i   # Interactive wizard (recommended)
```

This creates MCP config + steering rules for your AI tool (Kiro, Cursor, Claude, or Codex).

### 🦞 OpenClaw Plugin (Already Using OpenClaw?)

Use the native OpenClaw plugin guide: [OpenClaw Plugin Setup](plugins/openclaw/README.md).

```bash
openclaw plugins install @matrixorigin/memory-memoria
openclaw plugins enable memory-memoria
openclaw memoria install
```

### 4. Restart & verify

Restart your AI tool, then ask: *"Do you have memory tools available?"*

For detailed setup, see [Setup Skill](skills/setup/SKILL.md).

---

## Steering Rules

Steering rules teach your AI agent **when and how** to use memory tools. Without them, the agent has tools but no guidance — like having a database without knowing the schema.

### What They Do

| Rule | Purpose |
|------|---------|
| `memory` | Core memory tools — when to store, retrieve, correct, purge |
| `session-lifecycle` | Bootstrap at conversation start, cleanup at end |
| `memory-hygiene` | Proactive governance, contradiction resolution, snapshot cleanup |
| `memory-branching-patterns` | Isolated experiments with branches |
| `goal-driven-evolution` | Track goals, plans, progress across conversations |

### Example: Conversation Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CONVERSATION START                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. memory_retrieve(query="<user's question>")  ← load context       │   │
│  │ 2. memory_search(query="GOAL ACTIVE")          ← check active goals │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  MID-CONVERSATION                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • User states preference → memory_store(type="profile")             │   │
│  │ • User corrects a fact   → memory_correct(query="...", new="...")   │   │
│  │ • Topic shifts           → memory_retrieve(query="<new topic>")     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  CONVERSATION END                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. memory_purge(topic="<task>")  ← clean up working memories        │   │
│  │ 2. memory_store(type="episodic") ← save session summary             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Example: Goal-Driven Evolution

```
You: "I want to add OAuth support to the API"

AI:  → memory_search(query="GOAL OAuth")           ← check for existing goal
     → memory_store(content="🎯 GOAL: Add OAuth support\nStatus: ACTIVE", type="procedural")
     
     ... works on implementation, stores progress as working memories ...
     
     → memory_store(content="✅ STEP 1/3: Added OAuth routes", type="working")
     → memory_store(content="❌ STEP 2/3: Token refresh failed — need to fix expiry logic", type="working")

... next conversation ...

AI:  → memory_search(query="GOAL ACTIVE")          ← finds OAuth goal
     → memory_search(query="STEP for GOAL OAuth")  ← loads progress
     "Last time we were working on OAuth. Step 2 failed on token refresh. Want to continue?"

... goal completed ...

AI:  → memory_correct(query="GOAL OAuth", new_content="🎯 GOAL: OAuth — ✅ ACHIEVED")
     → memory_store(content="💡 LESSON: Token refresh needs 5min buffer before expiry", type="procedural")
     → memory_purge(topic="STEP for GOAL OAuth")   ← clean up working memories
```

### Example: Branch for Risky Experiments

```
You: "Let's try switching from PostgreSQL to SQLite"

AI:  → memory_branch(name="eval_sqlite")
     → memory_checkout(name="eval_sqlite")
     
     ... experiments on branch, stores findings ...
     
     → memory_diff(source="eval_sqlite")     ← preview changes
     → memory_checkout(name="main")
     → memory_merge(source="eval_sqlite")    ← or delete if failed
```

### File Locations

- Kiro: `.kiro/steering/*.md`
- Cursor: `.cursor/rules/*.mdc`
- Claude: `.claude/rules/*.md`
- Codex: `AGENTS.md`

### Update Rules

After upgrading Memoria:
```bash
memoria rules --force
```

---

## API Reference

### Core Tools

| Tool | Description |
|------|-------------|
| `memory_store` | Store a new memory |
| `memory_retrieve` | Retrieve relevant memories (call at conversation start) |
| `memory_search` | Semantic search across all memories |
| `memory_correct` | Update an existing memory |
| `memory_purge` | Delete by ID or topic keyword |
| `memory_list` | List active memories |
| `memory_profile` | Get user's memory-derived profile |
| `memory_feedback` | Record relevance feedback (useful/irrelevant/outdated/wrong) |
| `memory_capabilities` | List available memory tools |

### Snapshots & Branches

| Tool | Description |
|------|-------------|
| `memory_snapshot` | Create named snapshot |
| `memory_snapshots` | List snapshots with pagination |
| `memory_snapshot_delete` | Delete snapshots by name, prefix, or age |
| `memory_rollback` | Restore to snapshot |
| `memory_branch` | Create isolated branch |
| `memory_branches` | List all branches |
| `memory_checkout` | Switch branch |
| `memory_merge` | Merge branch back |
| `memory_branch_delete` | Delete a branch |
| `memory_diff` | Preview merge changes |

### Maintenance

| Tool | Description |
|------|-------------|
| `memory_governance` | Quarantine low-confidence memories (1h cooldown) |
| `memory_consolidate` | Detect contradictions (30min cooldown) |
| `memory_reflect` | Synthesize insights (2h cooldown) |

> `memory_rebuild_index`, `memory_observe`, `memory_get_retrieval_params`, `memory_tune_params`, `memory_extract_entities`, and `memory_link_entities` are available via REST API but hidden from MCP tool listing — they are ops/debug tools not intended for agent use.

Full API details: [API Reference Skill](skills/api-reference/SKILL.md)

---

## Memory Types

| Type | Use for | Example |
|------|---------|---------|
| `semantic` | Project facts, decisions | "Uses Go 1.22 with modules" |
| `profile` | User preferences | "Prefers pytest over unittest" |
| `procedural` | Workflows, how-to | "Deploy: make build && kubectl apply" |
| `working` | Temporary task context | "Currently debugging auth module" |
| `episodic` | Session summaries | "Session: optimized DB, added indexes" |

---

## Commands

| Command | Description |
|---------|-------------|
| `memoria init -i` | Interactive setup wizard |
| `memoria status` | Show config and rule versions |
| `memoria rules` | Update steering rules (auto-detect, `--tool`, or `-i`) |
| `memoria mcp` | Start MCP server |
| `memoria serve` | Start REST API server |
| `memoria plugin init --dir <dir> --name <name>` | Scaffold a new governance plugin project |
| `memoria plugin publish --package-dir <dir>` | Publish plugin to shared repository |
| `memoria plugin dev-keygen --dir <dir>` | Generate ed25519 dev signing keypair |
| `memoria benchmark --api-url <url> --token <key> --dataset <name>` | Run benchmark against API |

---

## Benchmark Reporting

For LongMemEval and BEAM, the primary reporting path is to keep each benchmark's official
categories separate:

- LongMemEval: report by official LongMemEval category
- BEAM: report by official BEAM ability

If you need a secondary internal rollup, you can also normalize reports into a shared
6-bucket memory taxonomy:

- `Single-Session Grounding`
- `Preference Understanding`
- `Multi-Session Synthesis`
- `Temporal State Tracking`
- `Knowledge Update And Conflict Handling`
- `Abstention And Constraint Following`

Use the rollup helper after generating JSON benchmark reports:

```bash
uv run python scripts/rollup_benchmark_report.py path/to/report.json
```

Or recursively over a results directory:

```bash
uv run python scripts/rollup_benchmark_report.py benchmarks/results/
```

This optional post-processing augments each report with:

- top-level `memory_ability_taxonomy`
- top-level `by_memory_ability_bucket`
- per-result `memory_ability_bucket`
- per-result `memory_ability_bucket_label`

See [Memory Ability Taxonomy](docs/memory-ability-taxonomy.md) for the LongMemEval and BEAM mapping and the rationale behind the 6-bucket summary.

---

## Modifying the MCP Config

`memoria init` generates the config once. To change settings afterwards, edit the config file directly:

- **Kiro**: `.kiro/settings/mcp.json`
- **Cursor**: `.cursor/mcp.json`
- **Claude**: `.mcp.json`

**Switch from local DB to remote server:**
```json
{
  "mcpServers": {
    "memoria": {
      "command": "memoria",
      "args": ["mcp", "--api-url", "https://your-server:8100", "--token", "sk-your-key..."]
    }
  }
}
```

**Change embedding provider** (edit the `env` block):
```json
{
  "mcpServers": {
    "memoria": {
      "command": "memoria",
      "args": ["mcp", "--db-url", "mysql+pymysql://root:111@localhost:6001/memoria", "--user", "alice"],
      "env": {
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_BASE_URL": "https://api.siliconflow.cn/v1",
        "EMBEDDING_API_KEY": "sk-...",
        "EMBEDDING_MODEL": "BAAI/bge-m3",
        "EMBEDDING_DIM": "1024"
      }
    }
  }
}
```

**Re-run init to overwrite** (use `--force` to also overwrite customized steering rules):
```bash
memoria init --tool kiro --api-url "https://new-server:8100" --token "sk-new-key..."
# steering rules are preserved unless --force is passed
```

**Update steering rules only** (after upgrading Memoria):
```bash
memoria rules
# restart your AI tool
```

Restart your AI tool after any config change.

---

## Setup by Tool

### Kiro

```bash
cd your-project
memoria init --tool kiro
```

Or manually create `.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "memoria": {
      "command": "memoria",
      "args": ["mcp", "--db-url", "mysql+pymysql://root:111@localhost:6001/memoria", "--user", "alice"]
    }
  }
}
```

The steering rule is bundled in the binary and written automatically by `memoria init`. Restart Kiro.

### Cursor

```bash
cd your-project
memoria init --tool cursor
```

Or manually create `.cursor/mcp.json` (same structure as above). Restart Cursor.

### Claude Desktop

```bash
cd your-project
memoria init --tool claude
```

Or manually edit `claude_desktop_config.json` (same structure). Restart Claude Desktop.

---

## Configuration Options

### Embedding providers

Memoria needs an embedding model to vectorize memories for semantic search.

| Provider | Quality | Privacy | Cost | First-use latency | Ongoing latency |
|----------|---------|---------|------|-------------------|-----------------|
| **Local** (default) | Good | ✅ Data never leaves machine | Free | Model download on first query | Fast (in-process) |
| **OpenAI / SiliconFlow** | Better | ⚠️ Text sent to API | API key required | None | Network round-trip |
| **Custom service** | Varies | Depends on host | Self-hosted | None | Network round-trip |

Configure via environment variables in the MCP config `env` block:

```json
"env": {
  "EMBEDDING_PROVIDER": "openai",
  "EMBEDDING_BASE_URL": "https://api.siliconflow.cn/v1",
  "EMBEDDING_API_KEY": "sk-...",
  "EMBEDDING_MODEL": "BAAI/bge-m3",
  "EMBEDDING_DIM": "1024"
}
```

Leave all empty to use local embedding (all-MiniLM-L6-v2, dim=384).

**💡 Local Embedding Tips:**
Local embedding requires building from source with `--features local-embedding` (pre-built binaries don't include it). See [Local Embedding Guide](skills/local-embedding/SKILL.md) for build instructions, supported models, and troubleshooting.

**⚠️ CRITICAL: Configure embedding BEFORE the MCP server starts for the first time.**
 Tables are created on first startup with the configured dimension. Changing it later requires re-creating the embedding column (destructive).

---

## Manual Tuning & Optimization

Integration quality depends on your AI agent's reasoning ability and steering rules. Out-of-the-box behavior may not be optimal.

**If memory usage feels suboptimal**, edit the steering rules in `.kiro/steering/memory.md`, `.cursor/rules/memory.mdc`, or `CLAUDE.md` to be more explicit. For example, if your agent forgets to retrieve memories at conversation start:

```markdown
CRITICAL: At the start of EVERY conversation, call memory_retrieve with the user's first message.
```

## Adapting to Other Agents

Memoria uses the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) standard. Any MCP-compatible agent can integrate by pointing to the server:

```json
{
  "mcpServers": {
    "memoria": {
      "command": "memoria",
      "args": ["mcp", "--db-url", "mysql+pymysql://root:111@localhost:6001/memoria", "--user", "alice"],
      "env": {
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_API_KEY": "sk-...",
        "EMBEDDING_MODEL": "BAAI/bge-m3",
        "EMBEDDING_DIM": "1024"
      }
    }
  }
}
```

Or in remote mode (proxy to a deployed Memoria REST API):

```json
{
  "mcpServers": {
    "memoria": {
      "command": "memoria",
      "args": ["mcp", "--api-url", "https://memoria-host:8100", "--token", "sk-your-key..."]
    }
  }
}
```

---

## Troubleshooting

### "Cannot connect to database"

```bash
docker ps | grep matrixone
# If not running:
docker start matrixone
```

### "EMBEDDING_PROVIDER=local but compiled without local-embedding feature"

The pre-built binaries from GitHub Releases do not include local embedding. Use an OpenAI-compatible embedding service instead, or build from source with the feature enabled:

```bash
cd Memoria/memoria
cargo build --release -p memoria-cli --features local-embedding
```

### First query is slow

Expected with local embedding — model loads into memory on first query (~3-5s). Use an embedding service to avoid this by setting `EMBEDDING_PROVIDER=openai` in the MCP config `env` block.

### AI tool doesn't seem to use memory

1. Verify `memoria` is in PATH: `which memoria`
2. Restart the AI tool after editing the MCP config
3. Test the server directly: `memoria mcp --db-url "mysql+pymysql://root:111@localhost:6001/memoria"`

### `memory_reflect` / `memory_extract_entities` returns "LLM not configured"

These tools support a `mode` parameter:
- `auto` (default): uses server-side LLM if configured, otherwise returns raw data for the AI agent to process
- `candidates`: always returns raw data for the agent to process — no LLM needed
- `internal`: forces server-side LLM processing — fails if `LLM_API_KEY` is not set

In MCP mode, the calling agent is already an LLM, so `auto` (default) works out of the box — it falls back to `candidates` automatically. No extra LLM configuration needed.

### Episodic memory returns HTTP 503

`POST /v1/sessions/{id}/summary` requires LLM configuration. Set `LLM_API_KEY` in the MCP config `env` block (see above).

---

## Development

### Quick setup (local dev)

```bash
# Start MatrixOne + API
make up

# In another terminal, configure your AI tool for remote mode:
cd your-project
memoria init --tool kiro --api-url "http://localhost:8100" --token "test-master-key-for-docker-compose"

# Restart your AI tool
```

Or use embedded mode (direct DB, no API):
```bash
cd your-project
memoria init --tool kiro --db-url "mysql+pymysql://root:111@localhost:6001/memoria"
```

### Run tests

```bash
make test-unit          # Unit tests (no DB)
make test               # All tests (needs DB)
make test-e2e           # E2E API tests (needs DB)
```

### Bump version and publish

```bash
make release VERSION=0.2.0      # Bump version, generate CHANGELOG, tag, push
                                 # CI builds binaries + Docker image automatically
make release-rc VERSION=0.2.0-rc1  # Pre-release
```

---

## For AI Agents

If you're an AI agent helping a user set up Memoria:

1. **Load the [Setup Skill](skills/setup/SKILL.md)** — it has step-by-step instructions
2. **Ask before acting**:
   - Which AI tool? (Kiro / Cursor / Claude / Codex)
   - MatrixOne database? (Docker / Cloud / existing)
   - Embedding service? (OpenAI / SiliconFlow / local)
3. **Run `memoria init -i`** in the user's project directory
4. **Tell user to restart** their AI tool
5. **Verify** with `memory_retrieve("test")`

⚠️ **Configure embedding BEFORE first MCP server start** — dimension is locked into schema.

---

## Architecture

```
┌─────────────┐     MCP (stdio)     ┌──────────────────────────────────────┐     SQL      ┌────────────┐
│  AI Agent   │ ◄─────────────────► │  Memoria MCP Server                  │ ◄──────────► │ MatrixOne  │
│             │   store / retrieve  │  ├── Canonical Storage               │  vector +    │  Database  │
│             │                     │  ├── Retrieval (vector / semantic)   │  fulltext    │            │
│             │                     │  └── Git-for-Data (snap/branch/merge)│              │            │
└─────────────┘                     └──────────────────────────────────────┘              └────────────┘
```

For codebase details, see [Architecture Skill](skills/architecture/SKILL.md).

---

## Development

```bash
make up              # Start MatrixOne + API
make test            # Run all tests
make release VERSION=0.2.0   # Bump, tag, push
```

**Developer documentation** (for contributing to Memoria):

| Skill | Description |
|-------|-------------|
| [Architecture](skills/architecture/SKILL.md) | Codebase layout, traits, tables |
| [API Reference](skills/api-reference/SKILL.md) | REST endpoints, request/response |
| [Deployment](skills/deployment/SKILL.md) | Docker, K8s, multi-instance |
| [Plugin Development](skills/plugin-development/SKILL.md) | Governance plugins |
| [Release](skills/release/SKILL.md) | Version bump, CI/CD |
| [Local Embedding](skills/local-embedding/SKILL.md) | Offline embedding build |

---

## License

Apache-2.0 © [MatrixOrigin](https://github.com/matrixorigin)
