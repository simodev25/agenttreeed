# Project Skills

Cette zone contient les skills spécifiques au repository courant, générés (ou mis à jour) via:

```text
/generate-project-skills
```

## Objectif

Compléter les skills génériques du kit avec un petit set de skills opérationnels ancrés dans les conventions locales du projet.

## Structure attendue

- Petit projet:
  - `.opencode/skills/project/<skill-name>/SKILL.md`
- Gros projet ou monorepo:
  - `.opencode/skills/project/<domain>/<skill-name>/SKILL.md`
- Nommage en `kebab-case`
- Pas plus de 3 skills générés par passe ciblée
- Pas de limite globale à 3 skills pour tout le projet

## Barre de qualité

Chaque skill projet doit:

1. être concret (commandes, chemins, checks),
2. citer des sources locales (`README`, `docs`, `scripts`, `CI`, etc.),
3. éviter les formulations génériques sans ancrage repo,
4. rester court et exploitable par un agent en exécution réelle.

## Relation avec les skills génériques

- Les skills dans `.opencode/skills/*` restent la base comportementale transversale.
- Les skills dans `.opencode/skills/project/**` ajoutent le contexte local.
- Un skill projet ne doit pas dupliquer un skill générique sans adaptation concrète.
- Un skill projet n'est pas une commande slash. Il ne doit pas créer de fichier
  sous `.opencode/command/**` et ne doit pas être documenté comme exécutable via
  `/<skill-name>`.

## Génération par domaine

Pour un projet complexe, génère plusieurs petits lots:

```text
/generate-project-skills domain=backend max=3 focus=test,debug
/generate-project-skills domain=frontend max=3 focus=build,review
/generate-project-skills domain=ci max=3 focus=ci,run
/generate-project-skills domain=security max=3 focus=review,migration
```

Le plafond de 3 skills sert à garder chaque passe relisible. Il ne signifie pas que le projet entier doit se limiter à 3 skills.

## Activation dans le workflow

Les skills projet sont appliqués automatiquement par:

- `/run-plan`
- `/review`
- `/check`
- `/check-fix`

Chaque commande:

1. scanne `.opencode/skills/project/**/SKILL.md`,
2. sélectionne jusqu’à 2 skills pertinents,
3. applique ces skills pendant l’exécution.
