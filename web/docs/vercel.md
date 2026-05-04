# Vercel

Vercel is optional.

Safe pattern:

1. Export public-safe JSON into `web/src/data`.
2. Build the frontend.
3. Deploy only the web folder.
4. Never deploy private wiki, state, sessions, or database files.

Do not commit `.vercel/project.json` into the public template.
