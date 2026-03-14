# UX/UI V1

## Parcours clés

1. Connexion
2. Tableau de bord trading (`Dashboard`)
  - sélection `pair`, `timeframe`, `mode`, `risk`, `compte MetaApi`
  - lancement run async
  - historique récent avec colonne `Temps running` en temps réel
3. Détail d'un run
  - étapes agents
  - décision finale
  - justification + risque + exécution
4. Ordres (`Trading`)
  - positions
  - ordres
  - comptes MetaApi
5. Control Room (`Config`)
  - état/test connecteurs
  - configuration LLM par agent
  - édition prompts versionnés par agent
  - analytics LLM + mémoire long-terme

## Navigation

- Barre latérale: Dashboard, Ordres, Backtests, Config.
- Header: session utilisateur/rôle.
- Navigation orientée "opérations d'abord": lancer, suivre, auditer.

## Écrans critiques

### Dashboard

- Carte de lancement run.
- KPIs de statut (`total`, `actifs`, `complétés`, `échecs`).
- Tableau d'historique avec:
  - `ID`, `Pair`, `TF`, `Mode`, `Status`, `Temps running`, `Decision`, `Action`.
- `Temps running` est calculé en temps réel côté UI avec interprétation UTC des timestamps backend.

### Config / Control Room

- Tableau connecteurs (`ollama`, `metaapi`, `yfinance`, `qdrant`) avec `Enable/Disable` + `Test`.
- Bloc `Modèles LLM par agent`:
  - modèle de repli global,
  - switch LLM par agent,
  - modèle spécifique par agent,
  - "LLM effectif",
  - bouton `Éditer prompt`.
- Bloc `Prompts versionnés (par agent)`:
  - sélection agent,
  - édition system/user template,
  - création + activation de version.
- Bloc `LLM réellement utilisé` (analytics).
- Bloc `Mémoire long-terme` (search).

### Ordres

- Bloc `Trades réels MT5 (MetaApi)` avec:
  - filtre compte + fenêtre (`Aujourd'hui`, `7`, `14`, `30`, `60`, `90` jours),
  - indicateur `Sync in progress` (`yes` = synchronisation historique en cours; `no` = pas de sync en cours),
  - graphe affiché avant les tables,
  - colonnes `Ticket` côté deals et historique ordres.

## Système visuel

- Thème sombre premium orienté trading.
- Contraste élevé pour données critiques (tableaux, badges, erreurs).
- Typographies: `Space Grotesk` + `IBM Plex Sans`.
- Accents:
  - bleu: navigation/état actif
  - vert: succès/completed
  - rouge: blocage/erreur
- Composants réutilisables:
  - cards
  - badges d'état
  - tableaux de supervision
  - formulaires administrables.

## Accessibilité minimale

- Contraste texte/fond renforcé sur les sections denses.
- États visuels explicites (`running`, `completed`, `failed`, `blocked`).
- Contrôles de formulaire consistants desktop/tablette.
