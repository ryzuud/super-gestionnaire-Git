# 🔄 Auto Git — Synchronisation Multi-Projets

Script Python d'automatisation Git qui scanne un répertoire parent et synchronise automatiquement tous les dépôts Git qu'il contient vers GitHub.

---

## ⚡ Fonctionnalités

- 📂 **Scan automatique** — Détecte tous les sous-dossiers qui sont des dépôts Git
- 🔍 **Vérification intelligente** — Utilise `git status` pour ne traiter que les dépôts avec des changements
- 📦 **Commit horodaté** — Crée un commit avec le message `Mise à jour auto - [Date et Heure]`
- 🚀 **Push automatique** — Envoie les changements vers le remote configuré
- 🔗 **Configuration upstream auto** — Détecte et configure `--set-upstream` si nécessaire
- 🛡️ **Gestion d'erreurs robuste** — Une erreur sur un dépôt ne bloque pas les autres
- 📊 **Récapitulatif coloré** — Affiche un tableau de synthèse en fin d'exécution

---

## 🚀 Utilisation

### Lancement rapide

```bash
python auto_git.py
```

Par défaut, le script scanne le répertoire `C:\Users\chime\Documents\programmation`.

### Avec un répertoire personnalisé

```bash
python auto_git.py "C:\chemin\vers\mes\projets"
```

---

## 📋 Exemple de sortie

```
═════════════════════════════════════════════════════════════════
  AUTO GIT — Synchronisation multi-projets
═════════════════════════════════════════════════════════════════
  Répertoire : C:\Users\chime\Documents\programmation
  GitHub      : https://github.com/ryzuud
  Date        : 16/04/2026 08:54:00
─────────────────────────────────────────────────────────────────

▶ Traitement de : Mon-Projet
  ──────────────────────────────────────────────────
  ✔  Mon-Projet — Fichiers ajoutés (git add .)
  ✔  Mon-Projet — Commit créé : "Mise à jour auto - 16/04/2026 08:54:00"
  ✔  Mon-Projet — Push effectué vers GitHub (ryzuud)

═════════════════════════════════════════════════════════════════
  RÉCAPITULATIF
═════════════════════════════════════════════════════════════════
  Projet                              Statut       Détail
  ─────────────────────────────────── ──────────── ──────────────────────
  Mon-Projet                          ✔ succès    Commit & push OK

  ✔ Succès : 1  |  – Ignorés : 0  |  ⚠ Partiels : 0  |  ✖ Erreurs : 0
═════════════════════════════════════════════════════════════════
```

---

## 🔧 Configuration

Les paramètres sont modifiables en haut du fichier `auto_git.py` :

| Variable | Description | Valeur par défaut |
|---|---|---|
| `REPERTOIRE_PARENT_DEFAUT` | Répertoire parent à scanner | `C:\Users\chime\Documents\programmation` |
| `GITHUB_USER` | Nom d'utilisateur GitHub | `ryzuud` |

---

## 📦 Prérequis

- **Python 3.10+**
- **Git** installé et accessible dans le PATH
- **Authentification Git** configurée (HTTPS token ou SSH)

---

## 🗂️ Statuts possibles

| Statut | Signification |
|---|---|
| ✔ **succès** | Commit + push effectués avec succès |
| – **ignoré** | Aucun changement détecté dans le dépôt |
| ⚠ **partiel** | Commit OK mais le push a échoué |
| ✖ **erreur** | Une erreur a empêché le traitement |

---

## 📄 Licence

Projet personnel — [ryzuud](https://github.com/ryzuud)
