const demo = {
  signals: [
    {
      title: "Hosted MCP services are becoming a product surface",
      summary: "Agent builders need current context, durable knowledge, and tool routing in one call.",
      source_urls: ["https://example.com/newswiki/signal"],
      topics: ["mcp", "coding-agents"],
      updated_at: "2026-05-05T09:00:00Z",
      confidence: "medium",
    },
  ],
  knowledge: [
    {
      title: "Public-safe export boundary",
      summary: "Only summaries, source links, topics, freshness, and confidence should cross into hosted service data.",
      source_urls: ["https://example.com/newswiki/public-export"],
      topics: ["mcp"],
      updated_at: "2026-05-05T09:10:00Z",
      confidence: "high",
    },
  ],
  tools: [
    {
      title: "Capability MCP",
      summary: "Route agents to relevant skills, plugins, MCP servers, and workflow chains before work starts.",
      source_urls: ["https://example.com/newswiki/capability-mcp"],
      topics: ["mcp", "coding-agents"],
      updated_at: "2026-05-05T09:20:00Z",
      confidence: "high",
    },
  ],
};

function byTopic(items, topic) {
  return items.filter((item) => item.topics.includes(topic));
}

function renderList(id, items) {
  const list = document.getElementById(id);
  list.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("li");
    empty.textContent = "No matching demo items.";
    list.appendChild(empty);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    const title = document.createElement("strong");
    title.textContent = item.title;
    const summary = document.createTextNode(item.summary);
    li.append(title, summary);
    list.appendChild(li);
  }
}

function renderSources(items) {
  const list = document.getElementById("sources");
  list.replaceChildren();
  const urls = [...new Set(items.flatMap((item) => item.source_urls))];
  for (const url of urls) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = url;
    link.textContent = url;
    link.rel = "noreferrer";
    li.appendChild(link);
    list.appendChild(li);
  }
}

function buildContextPack() {
  const task = document.getElementById("task").value.trim();
  const topic = document.getElementById("topic").value;
  const signals = byTopic(demo.signals, topic);
  const knowledge = byTopic(demo.knowledge, topic);
  const tools = byTopic(demo.tools, topic);
  const all = [...signals, ...knowledge, ...tools];

  document.getElementById("answer").textContent =
    all.length > 0
      ? `Context pack for: ${task || "untitled task"}`
      : "No strong demo matches for this topic.";
  document.getElementById("freshness").textContent =
    all.map((item) => item.updated_at).sort().at(-1) || "no data";
  renderList("signals", signals);
  renderList("knowledge", knowledge);
  renderList("tools", tools);
  renderSources(all);
}

document.getElementById("build").addEventListener("click", buildContextPack);
buildContextPack();
