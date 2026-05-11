# Inventaire des Composants Frontend

## Vue d'ensemble

Application React monopage (SPA) construite avec React 18, Material UI, et Vite. L'architecture repose sur des hooks personnalisés pour la gestion des données, sans store global centralisé.

---

## Pages

L'application expose 9 pages accessibles via React Router.

| Page | Route | Description |
|------|-------|-------------|
| PortfolioPage | `/` | Tableau de bord portefeuille en temps réel : KPIs financiers, courbe d'équité, budget de risque, exposition par devise, stress test |
| TerminalPage | `/terminal` | Terminal principal de trading : création de runs d'analyse, monitoring de l'exécution des agents, historique des runs, graphique TradingView intégré |
| OrdersPage | `/orders` | Vue complète des ordres : positions ouvertes, ordres en attente, deals MetaApi, ordres plateforme, graphiques associés |
| StrategiesPage | `/strategies` | Gestion des stratégies : génération IA par interface chat, validation par scoring, promotion du cycle de vie (DRAFT → LIVE), monitoring des performances |
| BacktestsPage | `/backtests` | Module de backtesting : création de backtests, courbe d'équité, table des trades, validations par agents, résultats détaillés |
| ConnectorsPage | `/connectors` | Configuration système : connecteurs externes, prompts des agents, modèles LLM, serveurs MCP externes, symboles financiers, comptes MetaApi, configuration trading, règles de gouvernance |
| RunDetailPage | `/runs/:id` | Détail d'un run d'analyse : streaming temps réel des résultats, cartes des 8 agents IA, descripteur d'instrument, sessions et événements du runtime |
| GovernanceRunDetailPage | `/governance/:id` | Détail d'un run de gouvernance : cartes des agents Phase 1, scores de conviction et d'urgence, boutons d'approbation et de rejet |
| LoginPage | `/login` | Page de connexion : formulaire email/mot de passe, redirection post-authentification |

---

## Composants par catégorie

### Layout

| Composant | Description |
|-----------|-------------|
| Layout | Barre latérale avec 6 éléments de navigation, mode rétractable (collapsible), bouton de déconnexion |

### Graphiques (Charts)

| Composant | Taille | Description |
|-----------|--------|-------------|
| TradingViewChart | ~432 lignes | Graphique en bougies avec overlays techniques et signaux temps réel via WebSocket |
| OpenOrdersChart | ~773 lignes | Graphique en bougies avec niveaux Stop Loss / Take Profit superposés |
| RealTradesCharts | ~1000 lignes | Suite de 5 graphiques répartis dans des onglets MUI Charts (performance, distribution, etc.) |
| EquityCurveChart | - | Courbe d'évolution de l'équité du portefeuille |
| CurrencyExposureChart | - | Graphique d'exposition par devise |

### Tables

| Composant | Description |
|-----------|-------------|
| OpenPositionsTable | Table des positions actuellement ouvertes |
| OpenPendingOrdersTable | Table des ordres en attente d'exécution |
| DealsTable | Table des deals MetaApi avec pagination |
| PlatformOrdersTable | Table des ordres plateforme avec pagination |
| StressTestTable | Table des résultats de stress test du portefeuille |

### KPI / Tableau de bord

| Composant | Description |
|-----------|-------------|
| PortfolioKPIs | Ensemble de 6 cartes affichant les indicateurs clés de performance du portefeuille |
| RiskBudgetBars | 5 barres de progression représentant la consommation du budget de risque |

### Panneaux (Panels)

| Composant | Taille | Description |
|-----------|--------|-------------|
| ExpansionPanel | - | Panneau extensible générique pour regrouper du contenu |
| GovernanceMonitorPanel | ~438 lignes | Panneau de monitoring de la gouvernance avec flux WebSocket en temps réel |
| ExternalMcpPanel | - | Panneau de gestion des serveurs MCP externes configurés |

### Modales

| Composant | Description |
|-----------|-------------|
| AddExternalMcpModal | Modale d'ajout d'un serveur MCP externe avec découverte automatique des outils disponibles |

### Composants de chargement (Loading)

| Composant | Description |
|-----------|-------------|
| LoadingSpinner | Indicateur de chargement circulaire générique |
| SectionSkeleton | Squelette de chargement pour une section entière |
| TableSkeleton | Squelette de chargement pour une table complète |
| ChartSkeleton | Squelette de chargement pour un graphique |
| ButtonSpinner | Indicateur de chargement intégré dans un bouton |
| TableSkeletonRows | Squelette de chargement pour des lignes individuelles de table |

### Utilitaires

| Fichier | Description |
|---------|-------------|
| formatters.ts | Fonctions de formatage : dates, symboles financiers, messages d'erreur |

---

## Hooks personnalisés

L'application expose 6 hooks personnalisés pour la logique métier et les flux de données.

| Hook | Description |
|------|-------------|
| `useAuth` | Fournisseur d'authentification JWT. Gère le token dans le localStorage, expose l'état de connexion et les méthodes login/logout via React Context |
| `usePortfolioStream` | Connexion WebSocket au flux portefeuille avec fallback automatique vers l'API REST et stratégie de reconnexion à backoff exponentiel |
| `useMetaTradingData` | Récupération des données MetaApi complexes : comptes, deals, positions, ordres. Expose plus de 18 valeurs d'état distinctes |
| `useOpenOrdersMarketChart` | Gestion des données pour le graphique de marché : bougies historiques, ticks WebSocket en temps réel, compte à rebours de la bougie courante |
| `useMarketSymbols` | Récupération des symboles de marché disponibles avec fallback vers des constantes prédéfinies |
| `usePlatformOrders` | Récupération et gestion des ordres d'exécution de la plateforme |

---

## Gestion d'état

L'application adopte une architecture légère sans store global :

- **Pas de store centralisé** : aucune dépendance à Redux, Zustand ou autre gestionnaire d'état global
- **React Context** : utilisé uniquement pour l'authentification (token JWT, état utilisateur)
- **État local + hooks personnalisés** : chaque composant ou page gère ses propres données via `useState` / `useReducer` combinés aux hooks personnalisés listés ci-dessus

---

## Feature Flags

Drapeaux de fonctionnalité contrôlant le comportement de l'application :

| Flag | Valeur par défaut | Description |
|------|-------------------|-------------|
| `enableMetaApiRealTradesDashboard` | `false` | Active le tableau de bord des trades réels MetaApi |
| `metaApiRealTradesDefaultDays` | `14` | Nombre de jours d'historique de trades à charger par défaut |
| `metaApiRealtimePricesPollMs` | `4000` ms | Intervalle de rafraîchissement des prix en temps réel (en millisecondes) |
