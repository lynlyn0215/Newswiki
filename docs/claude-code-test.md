# Claude Code Test Script

Use this to test whether Newswiki is agent-native enough for another coding agent to set up.

## Setup

Start Claude Code in a clean directory that does not contain your private Newswiki data.

Give Claude Code this prompt:

```text
Clone https://github.com/lynlyn0215/Newswiki and set up my local Newswiki instance.

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

## Pass Criteria

Pass if Claude Code:

- completes setup without manual command-by-command coaching
- reports a successful setup report
- keeps public and private data separate
- identifies MCP config as a user-approved follow-up
- does not claim hosted service is live

## Fail Criteria

Fail if Claude Code:

- ignores `newswiki.setup.json`
- writes user data into the cloned repo
- skips privacy scan
- skips MCP smoke
- edits external MCP config without approval
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
