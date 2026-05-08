---
title: Newswiki Transformation Plan
status: draft
created: 2026-05-07
reviewed: 2026-05-07
---

# Newswiki Transformation Plan

## One-Line Thesis

Newswiki gives coding agents current, source-backed AI/devtool context packs so they avoid stale assumptions before planning.

## Why This Changed

Newswiki should not compete with Claude, Codex, Hermes, or future agents on native memory, native skill authoring, or self-improvement.

Those platforms are already moving quickly:

- Hermes has memory, session search, skills, skill curator, and MCP client support.
- Claude Managed Agents are adding memory, dreaming, outcomes, templates, and multi-agent orchestration.
- Codex already has repo rules, skills, plugins, MCPs, and workflow memory patterns.

Generic Wiki MCP and Skill MCP are therefore not the product wedge.

The wedge is narrower:

```text
Agents are smart, but stale.
Agents can search, but not every search becomes task-ready judgment.
Agents can remember, but memory is often private, platform-specific, stale, or unscored.
Newswiki should supply current, source-backed, provenance-rich context for a task.
```

## ICP

Initial target user:

> Builders and operators of coding-agent workflows who use multiple agents and need current AI/devtool/MCP/model-release context before planning.

Not the initial user:

- general news readers
- people who only want a private wiki
- teams looking for generic enterprise memory
- users who only use one agent and do not care about current external context

## Painful Jobs

### Job 1: Product/architecture judgment is stale

Example:

> "Should we keep building a Skill MCP if Claude/Hermes now have native skill evolution?"

Failure without Newswiki:

- agent answers from old assumptions
- misses fresh platform updates
- treats local memory as current truth
- does not distinguish verified facts from guesses

### Job 2: Coding agents are inconsistent across tools

Example:

> "Ask Hermes, Claude Code, and Codex whether Newswiki should pivot."

Failure without Newswiki:

- each agent sees different memory
- each agent retrieves different sources
- conclusions are hard to compare

### Job 3: External signals are noisy

Example:

> "What recent AI agent platform changes affect our product direction?"

Failure without Newswiki:

- RSS/search returns too much
- agent cannot tell which updates matter
- freshness and confidence are implicit
- stale or demo data may be treated as evidence

## Product Boundary

### Newswiki Is

- read-only task context pack MCP for v1
- curated external signal index for AI agents, MCP, devtools, model releases
- provenance/freshness/confidence/data-limits layer
- evaluation harness proving context changed the answer

### Newswiki Is Not

- another agent memory system
- another native skill runtime
- a replacement for Hermes skill curator
- a generic RSS product
- a general-purpose enterprise knowledge base
- an automatic write-back system in v1

## V1 Scope

V1 must prove one thing:

> A source-backed Newswiki context pack improves a coding agent's answer compared with no Newswiki context.

V1 includes only:

1. Read-only Pre-Plan Brief MCP
2. External Signal Index
3. 10-task A/B evaluation

V1 defers:

- write-back MCP
- Hermes/Codex/Claude adapter generation
- skill insight registry
- local connector expansion
- web control plane
- billing
- broad topic coverage

## V1 Product Surface

### Tool: `get_context_for_task`

V1 output should be an agent pre-plan brief, not raw search results.

Input:

- `task`
- optional `agent`
- optional `topic`
- optional `freshness_window`

Output:

- task summary
- retrieval decision
- whether the task needs fresh facts
- relevant external signals
- relevant prior durable knowledge, if available
- stale assumption warnings
- confidence and freshness metadata
- source URLs
- data limits
- suggested verification steps
- what the agent should not assume
- next best action before planning

The tool should explain why it retrieved or skipped each layer.

## Signal Index

The first paid/valuable topic should be narrow:

> AI agents / MCP / devtools / model releases.

Each signal needs:

- `title`
- `summary`
- `why_it_matters`
- `entities`
- `affected_tasks`
- `time_sensitivity`
- `source_urls`
- `source_confidence`
- `last_verified_at`
- `freshness`
- `decision_impact`
- `stale_after`
- `data_limits`

Admission criteria:

- the signal changes or could change an agent's product, architecture, workflow, or tool-choice judgment
- the signal has at least one public source URL
- the signal names affected entities or products
- the signal has a concrete `why_it_matters`
- the signal can be tied to one or more benchmark tasks or likely user tasks

Reject:

- generic AI hype
- source-free claims
- raw article dumps
- stale version announcements with no decision impact
- low-confidence rumors unless explicitly labeled as such

Quality principle:

> Fewer signals, stronger task relevance.

## Retrieval Policy

Newswiki should not retrieve everything by default.

### Retrieve External Signals When

- the task depends on current or unstable facts
- the user asks about market, competitors, recent product releases, model/API changes, ecosystem movement, laws, prices, or schedules
- a product or architecture decision may be invalidated by recent platform updates
- source verification matters

### Retrieve Wiki / Durable Knowledge When

- the task touches prior decisions, known pitfalls, project architecture, MCP contracts, pipelines, automations, or public/private boundaries
- the user refers to previous work or asks "why did we decide this?"
- the task may repeat a known mistake

### Retrieve Capability Routing Only When

- the task is about choosing tools, workflows, MCPs, CLIs, automations, or local availability
- setup/configuration depends on what is installed locally

Capability routing is not a default startup step.

## Context Contract

Every context item should expose:

- `source_type`
- `privacy_level`
- `freshness`
- `confidence`
- `last_verified_at`
- `source_urls`
- `why_it_matters`
- `affected_tasks`
- `decision_impact`
- `stale_warning`
- `data_limits`

This is the product's trust layer.

## Evaluation Is Phase 1

Evaluation is not a later add-on. It is the proof of value.

Benchmark format:

```text
task
answer_without_newswiki
answer_with_newswiki
context_items_used
stale_assumptions_avoided
source_citations
decision_changed
human_rating
```

Rubric:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Relevance | no useful context | partly relevant | directly changes task framing |
| Freshness | stale/unclear | date present | freshness changes decision confidence |
| Source use | no source used | source cited | source used to verify or qualify claim |
| Stale assumption avoided | no | possible | clearly avoided |
| Decision impact | none | small wording change | plan/recommendation changed |
| Data limits honesty | ignored | mentioned | materially shaped conclusion |

Minimum v1 benchmark:

1. Should Newswiki keep Skill MCP as a core feature?
2. Should a coding-agent product support Hermes?
3. Did a new Claude/Codex/Hermes release change our product plan?
4. Should we build an MCP service or a local template?
5. Is a new AI devtool relevant to agent builders?
6. Does a recent model/API update affect our workflow?
7. What stale assumptions exist in the current Newswiki plan?
8. Which external signals matter for an agent product roadmap?
9. Should a user self-host or use hosted context?
10. What evidence is missing before a product pivot?

Success criteria:

- at least 7 of 10 tasks show a better answer with Newswiki context
- at least 5 tasks avoid a stale assumption
- every used signal has source URL and freshness metadata
- demo or low-confidence data is never treated as evidence
- the agent can explain how the context changed the answer

## Phases

### Phase 0: Product Boundary And Narrative

Work:

- rewrite README first screen around source-backed pre-plan context
- downgrade Wiki MCP / Capability MCP from product identity to input layers
- keep Hermes review rewrite as review artifact, not the canonical plan

Exit criteria:

- a new reader can understand in one minute that Newswiki is not a generic wiki, RSS reader, or skill runtime

### Phase 1: Pre-Plan Brief + Eval

Work:

- update README and docs to lead with source-backed AI/devtool context packs
- define v1 benchmark tasks
- define the `get_context_for_task` pre-plan brief shape
- create `docs/specs/signal-editorial-policy.md`
- ensure current context pack schema exposes freshness, confidence, data limits, and source URLs
- create 10 evaluation fixtures
- create `eval/rubric.md`
- create `eval/manual-ab-protocol.md`

Exit criteria:

- user can understand the narrower pitch in one minute
- A/B eval can run manually with Codex, Claude Code, and Hermes

### Phase 2: Signal Quality

Work:

- curate first 15 AI agents/MCP/devtools/model-release signals
- add `why_it_matters`, `affected_tasks`, `decision_impact`, `stale_after`
- add stale-signal warnings

Exit criteria:

- signal index helps at least 7 of 10 eval tasks
- stale or irrelevant signals are visibly downranked

### Phase 3: Retrieval Policy

Work:

- implement retrieval decision output
- add tests for when to query external signals, wiki, capability routing, or nothing
- expose `retrieval_reason` in context packs

Exit criteria:

- trivial local tasks do not trigger external retrieval
- current/product tasks trigger external signals
- prior-decision tasks trigger durable knowledge
- tool-routing tasks trigger capability lookup

### Phase 4: Cross-Agent Read-Only Use

Work:

- document Hermes, Claude Code, and Codex read-only consumption
- run A/B eval with at least two agents
- compare whether the same context pack changes different agents similarly

Exit criteria:

- at least two agents can consume the same context pack
- output quality improves without per-agent prompt rewrites

## Immediate Next Steps

1. Replace README first screen with the new positioning.
2. Update `get_context_for_task` contract to return a pre-plan brief.
3. Add `docs/specs/signal-editorial-policy.md`.
4. Add `eval/rubric.md` and `eval/manual-ab-protocol.md`.
5. Create 10 eval fixtures.
6. Curate 15 high-quality AI-agent/devtool signals.
7. Run one manual A/B eval before building more product surface.

## Deferred Until Proof

Do not build these until v1 eval shows repeated value:

- automatic write-back
- skill insight registry
- Hermes skill curator integration
- Codex/Claude skill adapters
- hosted user private wiki
- team admin controls
- web control plane

## Open Questions

- What is the smallest signal set that creates visible answer improvement?
- Should the first signal pack be AI agents only, or broader AI devtools?
- How often must signals be refreshed to stay valuable?
- What human rating rubric best captures "better agent answer"?
- What context should never be sent to hosted models?

## Decision Gate

After Phase 1 and Phase 2, decide:

- Continue if context improves at least 7 of 10 benchmark tasks.
- Narrow further if only a subset of tasks improve.
- Stop productization if agents do not use or benefit from the context pack.

## Later Vision

If v1 works, Newswiki can still become a cross-agent trusted context protocol.

But do not lead with protocol.

Lead with the painful job:

> Agents are stale and inconsistent. Newswiki gives them current, source-backed context before they plan.
