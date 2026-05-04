CREATE TABLE IF NOT EXISTS articles (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source TEXT NOT NULL,
  source_url TEXT,
  category TEXT,
  published_at TEXT,
  summary TEXT,
  summary_zh TEXT,
  tags TEXT DEFAULT '[]',
  show_on_website INTEGER DEFAULT 1,
  wiki_candidate INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
