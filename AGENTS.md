# Kairos Mesh — Agent Entry Point

> Ce fichier est le point d'entrée de compatibilité pour les outils qui auto-découvrent `AGENTS.md` à la racine.
> Les instructions complètes se trouvent dans **`.samourai/AGENTS.md`**.

---

**Langue des agents : Français.** Tous les agents communiquent exclusivement en français.

**Projet** : Kairos Mesh — système de trading multi-agents gouverné (8 agents, pipeline 4 phases).

**Stack** : Python 3.12 · FastAPI · React 18 · TypeScript · PostgreSQL · Redis · Celery · Docker.

**Instructions complètes** → [`.samourai/AGENTS.md`](.samourai/AGENTS.md)

**Profil opérationnel** → [`.samourai/ai/agent/project-profile.md`](.samourai/ai/agent/project-profile.md)

---

> ⚠️ **Règle de désambiguïsation** : quand le développeur parle d'un « agent », « prompt » ou « skill », il désigne **toujours un des 9 agents de trading du projet** (`technical-analyst`, `news-analyst`, `market-context-analyst`, `bullish-researcher`, `bearish-researcher`, `trader-agent`, `risk-manager`, `execution-manager`, `governance-trader`) — leurs prompts en base de données et leurs skills dans `backend/config/skills/` — **jamais** les agents Samourai (`.opencode/`) ni les skills OpenCode. Voir `.samourai/AGENTS.md` pour le détail complet.
