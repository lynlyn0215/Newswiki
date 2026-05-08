---
title: Newswiki Transformation Plan - Critical Review and Rewrite
status: draft
created: 2026-05-07
reviewed: 2026-05-07
language: zh-CN
source_plan: docs/plans/newswiki-transformation-plan.md
---

# Newswiki 转型计划：批判性审查与重写版

> **核心结论：** 原计划方向是对的：Newswiki 不应该再把“通用记忆 / 技能 / wiki / MCP 集合”当作主卖点，而应该聚焦到“给 coding agents 提供当前、带来源、可评估的任务上下文包”。但原计划仍然偏“概念正确”，还不够“产品可打、工程可交付、价值可验证”。下面先做批判性审查，再给出更锋利的重写版实施计划。

---

## Part 1：批判性审查

### 1. 最大优点

#### 1.1 定位收窄是正确的

原计划识别到了一个关键事实：Claude、Codex、Hermes 等 agent 平台会越来越多地内建记忆、技能、规则、MCP、工作流和多代理能力。Newswiki 如果继续卖“我也是一个 wiki / memory / skill MCP”，很容易被平台原生能力吞掉。

更好的 wedge 是：

> Agents 本身越来越强，但它们对“最近发生了什么、哪些变化会影响当前任务、哪些旧假设已经过期”仍然不稳定。

这个痛点足够真实，尤其适合 AI/devtool/MCP/model release 这类变化快、决策依赖新事实的领域。

#### 1.2 “评估优先”是正确的

原计划把 evaluation 放在 Phase 1，而不是后置，这是很重要的。Newswiki 的价值不能靠一句“上下文更好”证明，必须展示：

- 无 Newswiki：agent 做出旧假设或泛泛回答；
- 有 Newswiki：agent 改变判断、补充来源、降低错误假设；
- 人类能看出质量提升。

这比先做 dashboard、connector、hosted service 更重要。

#### 1.3 “只读 v1”是正确约束

v1 暂停 write-back、技能生成、自动记忆更新、web control plane、billing，是正确的。写入能力会引入隐私、权限、数据污染、质量控制和产品边界问题。现在最该验证的是：只读上下文包本身是否足够有价值。

---

### 2. 主要问题

#### 2.1 ICP 仍然太抽象

原 ICP：

> Builders and operators of coding-agent workflows who use multiple agents and need current AI/devtool/MCP/model-release context before planning.

这个定义方向正确，但还不够像一个可以卖、可以访谈、可以 demo 的人群。它仍然包含太多类型：

- 独立开发者；
- agent workflow 爱好者；
- 内部平台团队；
- AI 工具创业者；
- devrel / researcher；
- 自动化工程师。

这些人的购买动机、使用频率、愿意接入 MCP 的程度不同。

建议 v1 ICP 再窄一层：

> 正在用 Claude Code / Codex / Hermes 做 AI 工具或 agent workflow 产品决策的人，他们每周都要判断“最近的模型、MCP、agent 平台变化是否会推翻当前 roadmap”。

这样 demo 任务会更尖：

- “我们还要不要做 Skill MCP？”
- “Claude 新能力是否改变我们的 agent orchestration 设计？”
- “Hermes 原生 skills/memory 是否让 Newswiki 的某个模块失去意义？”

#### 2.2 “context pack”还没有足够产品化

原计划说要 `get_context_for_task`，输出 signals、knowledge、warnings、metadata 等，但还不够说明这个东西“长什么样、agent 怎么用、用户怎么判断它有价值”。

真正的 v1 产品表面不应该只是 raw JSON，而应该是一个明确的“agent pre-plan brief”：

1. 这个任务是否需要新事实？
2. 哪些假设可能过期？
3. 最近哪些信号会影响判断？
4. 哪些信号是高置信 / 低置信？
5. agent 在回答前必须检查哪 3 个点？
6. 如果上下文不足，应该承认什么限制？

也就是说，Newswiki 不只是“检索器”，而是“任务前判断层”。

#### 2.3 评估指标还不够严格

“7/10 tasks better”方向对，但容易主观。需要更可执行的评分 rubric。

建议每个 task 用 5 个维度打分，每项 0-2 分：

1. Freshness：是否纳入最近相关变化；
2. Source grounding：是否引用可检查来源；
3. Stale-assumption avoidance：是否明确避免旧假设；
4. Decision usefulness：是否改变或强化决策；
5. Uncertainty handling：是否说明缺口、置信度和需验证项。

每题满分 10。成功标准可以改成：

- Newswiki 版本平均分至少比 baseline 高 25%；
- 至少 7/10 题有明确可解释提升；
- 至少 5/10 题出现“避免旧假设”证据；
- 所有使用的外部信号必须有 source URL、last_verified_at、confidence、data_limits。

#### 2.4 信号采集和信号质量之间缺少“编辑标准”

原计划说 first 30 signals，但没有定义什么信号应该入选。结果可能变成“RSS 摘要集合”。

需要明确 editorial bar：

一个 signal 只有在满足以下至少 2 条时才入库：

- 改变 agent product / workflow / architecture 决策；
- 影响 MCP / tool integration / agent memory / skill strategy；
- 改变某个模型、API、平台能力边界；
- 能帮助 agent 避免一个已知 stale assumption；
- 有一手来源或可信二手来源；
- 在未来 30-90 天内仍有决策价值。

反过来，以下不该入 v1：

- 泛 AI 新闻；
- 没有任务影响的发布；
- 纯营销内容；
- 无来源的传言；
- 不影响 coding-agent workflow 的模型榜单噪音。

#### 2.5 当前 repo 叙事和新定位仍有冲突

我检查了 README 和 contract 文档。README 当前仍把 Newswiki 描述为：

> local-first personal agent information system template and hosted MCP alpha skeleton

这和转型计划里的新 wedge 不完全一致。README 还在强调三层 MCP：Wiki / Newsfeed / Capability，而转型计划已经说 “Generic Wiki MCP and Skill MCP are therefore not the product wedge”。

这不是代码问题，是叙事优先级问题。建议：

- README 第一屏改成“source-backed context packs for coding agents”；
- Wiki MCP / Capability MCP 降级为可选输入层；
- Newsfeed / curated signal index / evaluation harness 升级为主线；
- hosted alpha 不要先讲 skeleton，而要先讲“agent planning quality improved with context packs”。

#### 2.6 “多 agent 一致性”是好点，但 v1 可能太重

让 Hermes、Claude Code、Codex 都消费相同 context pack 是有价值的，但如果一开始就要求多 agent A/B，工作量会上升。建议：

- Phase 1 先用一个主 agent 做 10-task eval；
- Phase 2 再用第二个 agent 做复验；
- Phase 3 才强调 cross-agent consistency。

否则项目容易卡在接入细节，而不是验证核心价值。

---

### 3. 战略判断

#### 应该保留的方向

- “agents are stale”作为主痛点；
- read-only context pack MCP 作为 v1；
- AI agents / MCP / devtools / model releases 作为第一个窄领域；
- provenance / freshness / confidence / data_limits 作为信任层；
- A/B evaluation 作为第一阶段核心。

#### 应该弱化的方向

- 通用 private wiki；
- generic Skill MCP；
- hosted alpha skeleton 叙事；
- capability routing 作为默认启动步骤；
- web UI、billing、team admin；
- connector 大扩展。

#### 应该新增的方向

- “pre-plan brief”产品形态；
- editorial bar / signal admission criteria；
- scoring rubric；
- baseline-vs-context fixture 格式；
- README 第一屏改写；
- 一个可复制的 demo：同一任务，无 context vs 有 context，答案明显不同。

---

## Part 2：重写版实施计划

# Newswiki Source-Backed Agent Context Pack Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 把 Newswiki 从“local-first wiki/MCP template”重新定位并实现为“给 coding agents 的当前、来源支撑、可评估的任务前上下文包”。

**Architecture:** v1 只做只读上下文包。数据来自 curated public signals、可选 durable knowledge、可选 local capability metadata。核心产物是 `get_context_for_task` 返回的 pre-plan brief，而不是通用搜索结果。所有输出必须带 freshness、confidence、source URLs、data limits 和 retrieval reasoning。

**Tech Stack:** Markdown docs、现有 Newswiki MCP/service skeleton、JSON fixtures、Python validation/tests、manual A/B evaluation with Hermes / Claude Code / Codex。

---

## Phase 0：明确产品边界

### Task 1：改写一句话定位

**Objective:** 用一句话统一 README、plan、demo 的核心叙事。

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/plans/newswiki-transformation-plan.md` 或新增替代计划

**New positioning:**

```text
Newswiki gives coding agents current, source-backed context packs before they plan, so they avoid stale assumptions about AI tools, agent platforms, MCPs, and model releases.
```

**中文定位：**

```text
Newswiki 在 coding agent 开始规划前，提供当前、带来源、可评估的任务上下文包，帮助它避免对 AI 工具、agent 平台、MCP 和模型发布的过期假设。
```

**Verification:**

读 README 第一屏时，用户应该在 60 秒内明白：

- Newswiki 不是通用新闻阅读器；
- 不是另一个私有 wiki；
- 不是技能运行时；
- 它解决的是 agent 做计划前上下文过期的问题。

---

### Task 2：降级旧三层 MCP 叙事

**Objective:** 把 Wiki MCP、Newsfeed MCP、Capability MCP 从“产品本体”改成“context pack 输入层”。

**Files:**
- Modify: `README.md`
- Modify: `docs/core-mcps.md`
- Modify: `docs/specs/context-layer-contract.md`

**Required wording:**

```text
Newswiki's product surface is the context pack. Wiki, newsfeed, and capability layers are optional inputs. The agent should not query every layer by default; it should query only the layers justified by the task.
```

**Verification:**

README 中不能再给人感觉 Newswiki 的核心价值是“三个 MCP server 模板”。核心价值必须是 `get_context_for_task` 生成的 pre-plan context pack。

---

## Phase 1：定义 Context Pack 产品形态

### Task 3：定义 `get_context_for_task` v1 输出 schema

**Objective:** 把 context pack 从 generic JSON 搜索结果升级为 agent pre-plan brief。

**Files:**
- Modify: `docs/specs/mcp-contract.md`
- Modify: `docs/specs/context-layer-contract.md`
- Test: schema validator / fixture tests if present

**Proposed output shape:**

```json
{
  "ok": true,
  "task": "Should Newswiki keep Skill MCP as a core feature?",
  "retrieval_decision": {
    "external_signals": {
      "used": true,
      "reason": "The task depends on recent agent-platform and skill/memory capabilities."
    },
    "durable_knowledge": {
      "used": true,
      "reason": "The task references prior Newswiki product direction."
    },
    "capability_routing": {
      "used": false,
      "reason": "The task is product strategy, not local tool routing."
    }
  },
  "pre_plan_brief": {
    "short_answer": "Do not keep generic Skill MCP as the core wedge for v1.",
    "stale_assumptions_to_avoid": [
      "Assuming coding agents lack native memory or skill systems.",
      "Assuming a generic MCP wrapper is differentiated by itself."
    ],
    "decision_impact": "Reposition Newswiki around source-backed current context packs instead of skill runtime."
  },
  "context_items": [
    {
      "id": "signal-001",
      "title": "Agent platforms are adding native memory and skills",
      "summary": "Multiple coding-agent platforms now expose or are developing memory, skill, and workflow primitives.",
      "why_it_matters": "This weakens Newswiki's differentiation as a generic skill/wiki MCP.",
      "affected_tasks": ["product positioning", "roadmap prioritization"],
      "source_type": "newswiki_curated",
      "privacy_level": "public",
      "freshness": "recent",
      "confidence": "medium",
      "last_verified_at": "2026-05-07T00:00:00Z",
      "source_urls": [],
      "data_limits": "Needs direct source verification before public claim."
    }
  ],
  "suggested_verification_steps": [
    "Check latest Claude Code, Codex, and Hermes docs for native memory/skill changes.",
    "Compare whether a generic Skill MCP changes the answer in the 10-task eval."
  ],
  "context_limits": [
    "This pack summarizes curated signals; it is not a complete market scan."
  ]
}
```

**Verification:**

A coding agent should be able to paste this output before planning and produce a visibly better answer without additional explanation.

---

### Task 4：定义 signal 入库标准

**Objective:** 防止 signal index 退化成 RSS 摘要。

**Files:**
- Create: `docs/specs/signal-editorial-policy.md`

**Admission criteria:**

A signal can enter v1 only if it satisfies at least two:

1. It changes an agent product, workflow, or architecture decision.
2. It affects MCP, tool integration, agent memory, skills, or orchestration.
3. It changes a model/API/platform capability boundary.
4. It helps avoid a named stale assumption.
5. It has a primary source or credible secondary source.
6. It remains decision-relevant for at least 30 days.

**Reject:**

- Generic AI news;
- Pure marketing announcements;
- Unsourced rumors;
- Benchmark noise without workflow impact;
- Items with no affected task.

**Verification:**

Every curated signal must explain `why_it_matters` and `affected_tasks`; otherwise it fails validation.

---

## Phase 2：建立评估系统

### Task 5：创建 10 个 evaluation fixtures

**Objective:** 用固定任务证明 Newswiki context 是否改变 agent 答案。

**Files:**
- Create: `eval/tasks/*.json`
- Create: `eval/README.md`

**Fixture shape:**

```json
{
  "id": "eval-001",
  "task": "Should Newswiki keep Skill MCP as a core feature?",
  "baseline_prompt": "Answer without Newswiki context.",
  "context_prompt": "Answer using the provided Newswiki context pack.",
  "expected_improvement_signals": [
    "mentions native skill/memory capabilities in competing agents",
    "does not treat generic Skill MCP as differentiated by default",
    "recommends narrower source-backed context pack wedge"
  ]
}
```

**Initial 10 tasks:**

1. Should Newswiki keep Skill MCP as a core feature?
2. Should Newswiki lead with private wiki or current context packs?
3. Should a coding-agent product support Hermes in v1?
4. Should Newswiki build an MCP service or local template first?
5. Did a recent Claude/Codex/Hermes release invalidate a roadmap assumption?
6. Does a recent model/API update affect an agent workflow?
7. What stale assumptions exist in the current Newswiki README?
8. Which external AI agent signals matter for Newswiki's roadmap?
9. Should users self-host context or consume hosted context?
10. What evidence is missing before committing to this product pivot?

**Verification:**

Each task must be answerable in two modes: no-context baseline and Newswiki-context version.

---

### Task 6：定义评分 rubric

**Objective:** 把“better answer”变成可重复评分。

**Files:**
- Create: `eval/rubric.md`

**Rubric:**

Each answer gets 0-2 points for each dimension:

1. Freshness: uses recent relevant changes.
2. Source grounding: cites checkable sources or admits missing sources.
3. Stale assumption avoidance: names outdated assumptions.
4. Decision usefulness: changes, narrows, or strengthens a product decision.
5. Uncertainty handling: states confidence, limits, and verification steps.

**Success criteria:**

- Newswiki-context answers improve average score by at least 25% over baseline.
- At least 7/10 tasks show explainable improvement.
- At least 5/10 tasks avoid a stale assumption.
- 100% of used signals include source URL, freshness, confidence, and data limits.

---

### Task 7：创建手动 A/B eval protocol

**Objective:** 先不自动化，先让 eval 可手动运行。

**Files:**
- Create: `eval/manual-ab-protocol.md`

**Protocol:**

For each task:

1. Ask agent to answer without Newswiki context.
2. Save output as `answer_without_newswiki`.
3. Call or paste `get_context_for_task` output.
4. Ask the same agent to answer again using the context pack.
5. Score both outputs with `eval/rubric.md`.
6. Record whether the decision changed and why.

**Verification:**

A third-party agent should be able to run the protocol from docs alone.

---

## Phase 3：填充最小可用信号集

### Task 8：创建 first 15 curated signals, not 30

**Objective:** 先用 15 个高质量 signal 验证价值，不追求数量。

**Files:**
- Create or modify: `examples/signals/*.json` or existing public-safe export fixtures

**Required fields:**

```json
{
  "id": "signal-agent-platform-memory-001",
  "title": "Agent platforms are adding native memory and skill primitives",
  "summary": "Agent platforms increasingly include native memory, skills, rules, and workflow primitives.",
  "why_it_matters": "This weakens the case for Newswiki as a generic memory or skill MCP.",
  "entities": ["Claude", "Codex", "Hermes", "MCP"],
  "affected_tasks": ["product positioning", "roadmap prioritization", "agent workflow design"],
  "time_sensitivity": "medium",
  "source_urls": [],
  "source_confidence": "medium",
  "last_verified_at": "2026-05-07T00:00:00Z",
  "freshness": "recent",
  "decision_impact": "Shift v1 toward source-backed context packs.",
  "stale_after": "2026-06-07T00:00:00Z",
  "data_limits": "Needs direct source URLs before being used as public marketing evidence."
}
```

**Verification:**

At least 10/15 signals must map to one or more eval tasks.

---

## Phase 4：更新 product docs

### Task 9：Rewrite README first screen

**Objective:** 让新用户一分钟内理解产品。

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Proposed README opening:**

```markdown
# Newswiki

Newswiki gives coding agents current, source-backed context packs before they plan.

Agents are increasingly capable, but their answers can still be stale when a task depends on recent AI tools, MCPs, model releases, or agent-platform changes. Newswiki supplies a compact pre-plan brief with sources, freshness, confidence, stale-assumption warnings, and verification steps.

V1 focuses on one use case: helping coding agents make better product and architecture decisions in fast-moving AI/devtool ecosystems.
```

**Verification:**

README 第一屏不应再把 hosted alpha skeleton 或三 MCP 模板当作第一卖点。

---

### Task 10：创建 demo doc

**Objective:** 用一个任务展示 Newswiki 的前后差异。

**Files:**
- Create: `docs/demo/context-pack-before-after.md`

**Demo task:**

```text
Should Newswiki keep Skill MCP as a core feature?
```

**Doc sections:**

1. Baseline prompt;
2. Baseline answer;
3. Newswiki context pack;
4. Context-aware answer;
5. What changed;
6. Which stale assumptions were avoided;
7. Which sources or limits mattered.

**Verification:**

读者不需要运行代码，也能看出 Newswiki 的价值。

---

## Phase 5：Decision Gate

### Task 11：运行 Phase 1 eval 并记录结果

**Objective:** 用数据决定是否继续产品化。

**Files:**
- Create: `eval/results/YYYY-MM-DD-manual-ab.md`

**Record:**

```markdown
# Manual A/B Eval Results

| Task | Baseline Score | Newswiki Score | Improvement | Stale Assumption Avoided | Decision Changed | Notes |
|---|---:|---:|---:|---|---|---|
```

**Continue if:**

- Average score improves by >= 25%;
- 7/10 tasks improve;
- 5/10 tasks avoid stale assumptions;
- sources and data limits are preserved.

**Narrow if:**

- Only product-strategy tasks improve;
- Only MCP-related tasks improve;
- Only one agent benefits.

**Stop or pivot if:**

- Agents ignore the context pack;
- Better answers come from generic web search alone;
- Signal curation cost is too high for visible quality gain;
- Users do not repeat the workflow.

---

## Final Recommended Product Shape

### What Newswiki is in v1

Newswiki is a read-only pre-plan context service for coding agents.

It answers:

```text
Before this agent plans, what current, source-backed context should it know, and which stale assumptions should it avoid?
```

### What Newswiki is not in v1

- not a generic private wiki;
- not a generic RSS reader;
- not a skill runtime;
- not a memory replacement;
- not a team knowledge base;
- not an automatic write-back system;
- not a dashboard-first product.

### The wedge

```text
Coding agents are powerful, but stale and inconsistent.
Newswiki gives them a current, source-backed pre-plan brief so product and architecture decisions do not rely on outdated assumptions.
```

### The proof

```text
Run 10 tasks with and without Newswiki context.
If the context-aware answers are measurably better, Newswiki has a product wedge.
If not, do not build more infrastructure.
```

---

## Immediate next steps

1. Replace README first screen with the new positioning.
2. Update `get_context_for_task` contract to return a pre-plan brief.
3. Add `docs/specs/signal-editorial-policy.md`.
4. Add `eval/rubric.md` and `eval/manual-ab-protocol.md`.
5. Create 10 eval fixtures.
6. Curate 15 high-quality AI-agent/devtool signals.
7. Run one manual A/B eval before building more product surface.
