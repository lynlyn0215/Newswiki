const demo = {
  signals: [
    {
      title: "Hosted MCP services are becoming a product surface",
      summary: "Agent builders need current context, durable knowledge, and tool routing in one call.",
      source_urls: ["https://example.com/newswiki/signal"],
      topics: ["mcp", "coding-agents"],
      updated_at: "2026-05-05T09:00:00Z",
      confidence: "medium",
      source_type: "newswiki_hosted",
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
      source_type: "newswiki_curated",
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
      source_type: "recommended_template",
    },
  ],
  private_memory: [
    {
      title: "User project decision",
      summary: "Keep private wiki memory user-owned; use hosted context only as an optional layer.",
      source_urls: [],
      topics: ["mcp"],
      updated_at: "2026-05-05T09:30:00Z",
      confidence: "high",
      source_type: "user_private",
    },
  ],
  local_capabilities: [
    {
      title: "Local Wiki MCP",
      summary: "Call wiki_past_knowledge before planning or architecture work.",
      source_urls: [],
      topics: ["mcp", "coding-agents"],
      updated_at: "2026-05-05T09:40:00Z",
      confidence: "high",
      source_type: "local_capability",
    },
  ],
};

function enabledLayers() {
  return [...document.querySelectorAll("[data-layer]:checked")].map((input) => input.dataset.layer);
}

function byTopicAndLayer(items, topic, layers) {
  return items.filter((item) => item.topics.includes(topic) && layers.includes(item.source_type));
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
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = item.source_type;
    li.append(title, badge, summary);
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
  const layers = enabledLayers();
  const signals = byTopicAndLayer(demo.signals, topic, layers);
  const knowledge = byTopicAndLayer(demo.knowledge, topic, layers);
  const tools = byTopicAndLayer(demo.tools, topic, layers);
  const privateMemory = byTopicAndLayer(demo.private_memory, topic, layers);
  const localCapabilities = byTopicAndLayer(demo.local_capabilities, topic, layers);
  const all = [...signals, ...knowledge, ...tools, ...privateMemory, ...localCapabilities];
  const dataLimits = [];
  if (!layers.includes("user_private")) {
    dataLimits.push("user_private wiki layer is not connected");
  }
  if (!layers.includes("local_capability")) {
    dataLimits.push("local capability layer is not connected");
  }
  if (signals.length) {
    dataLimits.push("hosted signals in this playground are demo fixtures");
  }

  document.getElementById("answer").textContent =
    all.length > 0
      ? `Context pack for: ${task || "untitled task"}`
      : "No strong demo matches for this topic.";
  document.getElementById("freshness").textContent =
    all.map((item) => item.updated_at).sort().at(-1) || "no data";
  document.getElementById("enabled-layers").textContent = layers.join(" / ") || "none";
  renderList("signals", signals);
  renderList("knowledge", knowledge);
  renderList("tools", tools);
  renderList("private-memory", privateMemory);
  renderList("local-capabilities", localCapabilities);
  renderList(
    "data-limits",
    dataLimits.map((summary) => ({
      title: "Data limit",
      summary,
      source_type: "boundary",
      source_urls: [],
      topics: [topic],
      updated_at: "",
      confidence: "medium",
    })),
  );
  renderSources(all);
}

document.getElementById("build").addEventListener("click", buildContextPack);
for (const input of document.querySelectorAll("[data-layer]")) {
  input.addEventListener("change", buildContextPack);
}
buildContextPack();
