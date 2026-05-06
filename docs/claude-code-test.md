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

## Product-Value MCP Test

After Claude Code has connected the three local MCP servers, use this prompt to test whether it actually uses Newswiki context during real work:

```text
I want to decide whether a hosted Newswiki MCP service is worth continuing as a SaaS product.

Follow the Newswiki startup protocol:

1. Use Capability MCP to find the relevant skill, tool, or workflow chain for this task.
2. Use Wiki MCP to retrieve past knowledge about Newswiki, MCP, hosted service, open-core positioning, prior decisions, patterns, pitfalls, and gaps.
3. Use Newsfeed MCP to check recent signals or source health. If the Newsfeed data is only demo data, say that clearly.

Then give me a product judgment:

- the 3 user scenarios most worth validating
- how to test each scenario
- success criteria for each test
- which MCP tools you actually called
- how each MCP result changed your conclusion

Do not answer from general knowledge alone. Do not pretend demo news is market evidence.
```

Pass if Claude Code:

- calls at least one Capability MCP tool and one Wiki MCP tool
- calls Newsfeed MCP or explicitly explains why current signals are unavailable
- distinguishes empty fresh-instance data from real prior knowledge
- distinguishes demo news from market evidence
- changes or qualifies its recommendation based on MCP results

Fail if Claude Code:

- gives a generic product strategy answer without MCP calls
- claims the demo newsfeed is real market validation
- ignores an empty wiki or generic capability catalog
- cannot explain how MCP context affected the answer
