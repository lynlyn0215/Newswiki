# Open Core And Hosted Service

Newswiki is designed to be understandable, cloneable, and self-hostable.

That does not conflict with a hosted Newswiki MCP service. It makes the hosted service easier to trust.

## What This Repository Gives You

This public template helps a user or their AI agent build a private local Newswiki:

- local private instance skeleton
- Wiki MCP, Capability MCP, and Newsfeed MCP templates
- public-safe export schema and validator
- hosted alpha REST and MCP service skeleton
- agent-native setup manifest and bootstrap scripts
- fake examples and a static playground

The goal is transparency. A user should be able to see the protocol, inspect the boundaries, and build their own version.

## What A Hosted Service Would Sell

A hosted Newswiki service should not sell mystery code.

It should sell maintained intelligence and operational relief:

- a stable remote MCP endpoint
- curated AI agent, MCP, coding agent, and devtools signals
- maintained public Knowledge Wiki pages
- tool, skill, repo, and workflow recommendations
- topic briefs and topic representations
- source health and trend monitoring
- API keys, usage limits, monitoring, and uptime
- push delivery by email, Slack, Discord, or other channels
- optional team/workspace configuration

The customer connects an MCP endpoint and asks:

```text
get_context_for_task
```

They do not need to maintain collectors, scraping, summarization, translation, classification, public-safe export validation, deployment, or MCP uptime.

## Self-Host And Hosted Are Different Jobs

Self-hosting answers:

```text
Can I own and inspect the system?
```

Hosted service answers:

```text
Can I get useful, maintained context without operating the system?
```

Both should exist.

## Open-Core Boundary

Open template:

- protocol
- local setup
- MCP skeletons
- public-safe export contract
- smoke tests
- playground
- docs for agent-native setup

Hosted layer:

- maintained data
- curated source lists
- high-quality summaries and briefs
- tool catalog updates
- background workers
- rate limits and monitoring
- multi-user service operations

## Why Publish The Template

Publishing the template helps the hosted service because:

- users can inspect what the service is doing
- agent builders can prototype locally
- trust is higher because the privacy boundary is visible
- hosted value becomes operational quality, not lock-in
- users who outgrow self-hosting have a clear upgrade path

The repo is the protocol and local prototype. The service is the maintained intelligence layer.

## Positioning Sentence

Use this when explaining the commercial version:

```text
Newswiki is an open, self-hostable agent information protocol with a hosted MCP intelligence layer for people who want maintained signals, knowledge, and tool routing without running the pipeline themselves.
```
