# 开源模板与 Hosted Service

Newswiki 的公开 repo 应该让人和 Agent 都能看懂、clone、自己搭。

这和卖 hosted Newswiki MCP service 不冲突。相反，它会增强信任。

## 这个 Repo 提供什么

这个公开模板帮助用户或用户的 AI agent 搭建自己的 private local Newswiki：

- 本地私有实例骨架
- Wiki MCP、Capability MCP、Newsfeed MCP 模板
- public-safe export schema 和 validator
- hosted alpha REST / MCP 服务骨架
- agent-native setup manifest 和 bootstrap 脚本
- 假数据和静态 playground

目标是透明。用户应该能看懂协议、检查隐私边界，并搭出自己的版本。

## Hosted Service 卖什么

Hosted Newswiki 不应该卖“神秘代码”。

它卖的是持续维护的信息层和省心的运行体验：

- 稳定的远程 MCP endpoint
- 持续更新的 AI agent / MCP / coding agent / devtools 信号
- 维护好的公开 Knowledge Wiki 页面
- tool / skill / repo / workflow 推荐
- topic briefs 和 topic representations
- source health 和趋势监控
- API keys、usage limits、monitoring、uptime
- Email、Slack、Discord 等推送
- 可选团队/workspace 配置

客户只需要连接 MCP endpoint，然后调用：

```text
get_context_for_task
```

他们不用维护 collectors、网页抓取、摘要、翻译、分类、public-safe export validation、部署和 MCP uptime。

## 自建和 Hosted 是两件不同的工作

自建回答的是：

```text
我能不能拥有并检查这套系统？
```

Hosted 回答的是：

```text
我能不能不运维这套系统，但直接拿到有用的上下文？
```

两者应该同时存在。

## Open-Core 边界

开源模板包括：

- 协议
- 本地 setup
- MCP skeletons
- public-safe export contract
- smoke tests
- playground
- agent-native setup 文档

Hosted 层包括：

- 维护好的数据
- curated source lists
- 高质量 summaries 和 briefs
- tool catalog 更新
- background workers
- rate limits 和 monitoring
- 多用户服务运维

## 为什么要公开模板

公开模板能帮助 hosted service，因为：

- 用户能检查服务到底在做什么
- agent builders 可以先本地试用
- 隐私边界清楚，信任更高
- hosted 价值来自运营质量，不是锁定用户
- 自建用户如果不想维护，可以自然升级到 hosted

Repo 是协议和本地原型。Service 是持续维护的信息层。

## 一句话定位

介绍商业版时可以这样说：

```text
Newswiki 是一个开放、可自托管的 Agent 信息协议；Hosted Newswiki MCP 是给不想自己维护 pipeline 的用户提供的持续更新 intelligence layer。
```
