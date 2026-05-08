# Claude Code Test Script

Use this to test whether Newswiki is agent-native enough for another coding agent to set up.

## Setup

Start Claude Code in a clean directory that does not contain your private Newswiki data.

Give Claude Code this prompt:

```text
Clone https://github.com/lynlyn0215/Newswiki and set up my local Newswiki instance.

You are Claude Code. Do not call yourself Codex, and do not assume my MCP client is Codex unless you actually find a Codex config path. Detect my actual MCP client/config before recommending config edits.

Treat me as a user who wants my AI agent to do the setup. Follow the repo's agent-facing instructions. Do not put private data into the public repo. Do not edit external MCP config files without asking me first.

Use a private instance path under my home directory named Newswiki-private-claude-test.

At the end, report:
- which setup files you read
- which commands you ran
- whether the private instance was created
- whether capabilities.json exists
- whether privacy scan passed
- whether public export validation passed
- whether MCP smoke passed
- which MCP client/config you detected, if any
- what I still need to copy into my real MCP config
```

## What To Watch

Claude Code should:

- read `AGENTS.md`
- read `newswiki.setup.json`
- read `docs/agent-setup-protocol.md`
- read `docs/agent-checklist.md`
- ask before high-impact actions
- create a private instance outside the public repo
- run the agent setup bootstrap
- run validation or inspect `setup-report.json`
- avoid copying private data into the public repo
- distinguish Claude Code, Codex, Claude Desktop, and generic MCP clients when discussing config

## Pass Criteria

Pass if Claude Code:

- completes setup without manual command-by-command coaching
- reports a successful setup report
- keeps public and private data separate
- identifies MCP config as a user-approved follow-up
- does not call itself Codex unless actually running inside Codex
- does not claim hosted service is live

## Fail Criteria

Fail if Claude Code:

- ignores `newswiki.setup.json`
- writes user data into the cloned repo
- skips privacy scan
- skips MCP smoke
- edits external MCP config without approval
- says "restart Codex" when the detected client is Claude Code or another client
- cannot explain open template vs hosted service

## Optional Follow-Up Prompt

After setup succeeds, ask:

```text
Now explain whether I should self-host Newswiki, use a hosted Newswiki MCP service, or both. Base your answer on the repo docs.
```

Expected answer:

- self-hosting gives ownership and inspectability
- hosted service gives maintained intelligence and operational relief
- the two are complementary

## Product-Value Context Test

After Claude Code has connected the Newswiki MCP server or local input-layer MCPs, use this prompt to test whether it actually uses the v1 context surface during real work:

```text
I want to decide whether a hosted Newswiki MCP service is worth continuing as a SaaS product.

Follow the Newswiki context protocol:

1. First call `get_context_for_task` for this task if available.
2. Read `retrieval_decision`, `data_limits`, freshness, confidence, and sources before answering.
3. Use direct Wiki MCP, Newsfeed MCP, or Capability MCP calls only if `get_context_for_task` is unavailable or if you are debugging a specific input layer.
4. Use Capability routing only if this task requires choosing tools, workflows, MCP setup, or local capability routing. If you skip it, say why.

Then give me a product judgment:

- the 3 user scenarios most worth validating
- how to test each scenario
- success criteria for each test
- which Newswiki tools you actually called
- how the context pack changed or limited your conclusion
- which context layers were queried, skipped, or weak

Do not answer from general knowledge alone if Newswiki context is available. Do not pretend demo data or internal docs are external market evidence.
```

Pass if Claude Code:

- calls `get_context_for_task` when available
- explains `retrieval_decision`
- calls direct input-layer MCP tools only when the flagship context tool is unavailable or the layer needs debugging
- distinguishes empty fresh-instance data from real prior knowledge
- distinguishes demo news from market evidence
- changes or qualifies its recommendation based on Newswiki context

Fail if Claude Code:

- gives a generic product strategy answer without Newswiki context calls when they are available
- claims the demo newsfeed is real market validation
- treats a generic capability catalog as stronger than source evidence
- cannot explain how the context pack affected the answer
