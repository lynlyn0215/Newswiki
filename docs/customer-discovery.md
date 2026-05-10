# Customer Discovery

Newswiki v1 has product-value evidence from the 2026-05-09 A/B eval, but hosted productization still needs customer and demand evidence.

This document records early demand signals, target users, discovery questions, and decision gates for a hosted or open-core Newswiki service.

## Current Evidence

### Internal Product-Value Evidence

The 10-task A/B eval showed `get_context_for_task` improving agent answers:

- Context wins: 10 / 10
- Average context score: 12.7 / 14
- Average control score: 5.1 / 14
- Average lift: +7.6

This proves the brief can improve agent judgment on curated benchmark tasks. It does not prove willingness to adopt or pay for a hosted service.

Tracked summary: [Product-value eval](eval-product-value-2026-05-09.md).

### External Demand Signals

These are adjacent market signals, not direct customer commitments:

1. **Remote MCP is becoming a production surface.**
   Vercel documents an official OAuth-based remote MCP server for project, deployment, log, and documentation workflows.
   Source: [Vercel MCP docs](https://vercel.com/docs/agent-resources/vercel-mcp)

2. **Context loading cost is a real agent-platform problem.**
   Cursor describes dynamic context discovery for MCP and reports token reduction from loading only relevant tool context.
   Source: [Cursor dynamic context discovery](https://cursor.com/blog/dynamic-context-discovery)

3. **Large MCP/API surfaces need server-side composition.**
   Cloudflare's Code Mode pattern reduces MCP context cost by exposing compact search/execute flows instead of dumping large tool definitions into the model.
   Source: [Cloudflare Code Mode MCP](https://blog.cloudflare.com/code-mode-mcp/)

4. **MCP production deployment needs enterprise controls.**
   Cloudflare's enterprise MCP write-up frames production MCP around safer deployment, security architecture, and operational controls.
   Source: [Cloudflare enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/)

5. **The MCP roadmap emphasizes remote transport and enterprise readiness.**
   The MCP roadmap describes transport scalability and enterprise readiness as protocol priorities.
   Source: [MCP roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

## Target Users

Primary:

- Builders of AI coding-agent workflows.
- Developer-tool founders deciding whether recent model, MCP, or agent-platform changes affect roadmap.
- Teams using more than one agent client and needing shared pre-plan context.

Secondary:

- Agent platform operators evaluating remote MCP surface design.
- Open-core maintainers who need public-safe context packs without exposing private wiki or feed data.

## Discovery Questions

Ask users:

1. What recent AI/devtool/model/MCP changes have changed your roadmap in the last 30 days?
2. Before planning a coding-agent task, where do you currently check current facts?
3. Do stale assumptions cause rework, wrong tool choices, or bad product decisions?
4. Would you connect a hosted read-only MCP for source-backed pre-plan briefs?
5. Would you prefer self-hosted exports, hosted MCP, or both?
6. Which topics are valuable enough to pay for: AI agents, MCP, model releases, devtools, infra, open-core?
7. What data cannot leave your machine?
8. What proof would make you trust a context brief?

## Evidence Needed Before Hosted SaaS

Do not build billing, write-back, tenant admin UI, or client-specific adapters until at least one gate is met:

- 5+ target users report a recurring stale-assumption or current-context pain.
- 3+ users say they would connect a hosted read-only MCP to an agent client.
- 2+ users share real tasks where a Newswiki brief changes a plan or avoids rework.
- At least one user prefers hosted MCP over self-hosted templates despite privacy tradeoffs.

## Current Gaps

- No direct customer interviews yet.
- No pricing or willingness-to-pay evidence.
- No hosted trust evidence beyond public-safe export validation.
- No proof that non-Newswiki users understand the brief format without guidance.

## Next Discovery Batch

Run 5 interviews or async tests with:

- 2 coding-agent power users.
- 1 developer-tool founder.
- 1 open-source maintainer.
- 1 platform or infra engineer using MCP or agent tools.

For each, collect:

- Task they tried.
- Whether Newswiki context changed the answer.
- Sources they trusted or ignored.
- Adoption preference: hosted MCP, self-hosted, or no.
- Blocking concerns.
