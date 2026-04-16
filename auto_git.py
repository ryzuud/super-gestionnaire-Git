#!/usr/bin/env python3
"""
=============================================================================
  AUTO GIT — Script d'automatisation Git multi-projets
=============================================================================
  Scanne un répertoire parent et, pour chaque dépôt Git contenant des
  changements non commités, exécute automatiquement :
      git add .  →  git commit  →  git push

  Remote GitHub : https://github.com/ryzuud
  Usage : python auto_git.py [chemin_du_répertoire_parent]
=============================================================================
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Forcer la sortie en UTF-8 sur Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
REPERTOIRE_PARENT_DEFAUT = r"C:\Users\chime\Documents\programmation"
GITHUB_USER = "ryzuud"

# Codes couleur ANSI pour un affichage lisible dans le terminal
class Couleurs:
    VERT    = "\033[92m"
    JAUNE   = "\033[93m"
    ROUGE   = "\033[91m"
    CYAN    = "\033[96m"
    GRAS    = "\033[1m"
    RESET   = "\033[0m"


# ──────────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ──────────────────────────────────────────────────────────────────────────────
def log_info(msg: str) -> None:
    print(f"  {Couleurs.CYAN}ℹ{Couleurs.RESET}  {msg}")

def log_succes(msg: str) -> None:
    print(f"  {Couleurs.VERT}✔{Couleurs.RESET}  {msg}")

def log_erreur(msg: str) -> None:
    print(f"  {Couleurs.ROUGE}✖{Couleurs.RESET}  {msg}")

def log_avertissement(msg: str) -> None:
    print(f"  {Couleurs.JAUNE}⚠{Couleurs.RESET}  {msg}")


def executer_commande(commande: list[str], cwd: str) -> subprocess.CompletedProcess:
    """Exécute une commande shell et retourne le résultat."""
    return subprocess.run(
        commande,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )


def est_depot_git(chemin: str) -> bool:
    """Vérifie si un dossier est un dépôt Git (présence de .git)."""
    return os.path.isdir(os.path.join(chemin, ".git"))


def a_des_changements(chemin: str) -> bool:
    """Vérifie via `git status --porcelain` si le dépôt a des changements."""
    resultat = executer_commande(["git", "status", "--porcelain"], cwd=chemin)
    # Si la sortie n'est pas vide → il y a des changements
    return bool(resultat.stdout.strip())


def traiter_depot(chemin: str) -> dict:
    """
    Traite un dépôt Git :
      1. Vérifie les changements
      2. git add .
      3. git commit avec message horodaté
      4. git push

    Retourne un dictionnaire récapitulatif du traitement.
    """
    nom_projet = os.path.basename(chemin)
    resultat = {
        "projet": nom_projet,
        "chemin": chemin,
        "statut": "ignoré",
        "message": "Aucun changement détecté",
    }

    # ── Étape 1 : Vérifier les changements ────────────────────────────────
    try:
        if not a_des_changements(chemin):
            log_info(f"{nom_projet} — Aucun changement, passage au suivant.")
            return resultat
    except subprocess.TimeoutExpired:
        resultat["statut"] = "erreur"
        resultat["message"] = "Timeout lors de git status"
        log_erreur(f"{nom_projet} — Timeout lors de la vérification du statut.")
        return resultat
    except Exception as e:
        resultat["statut"] = "erreur"
        resultat["message"] = f"Erreur git status : {e}"
        log_erreur(f"{nom_projet} — Erreur git status : {e}")
        return resultat

    # ── Étape 2 : git add . ───────────────────────────────────────────────
    try:
        add_result = executer_commande(["git", "add", "."], cwd=chemin)
        if add_result.returncode != 0:
            raise RuntimeError(add_result.stderr.strip())
        log_succes(f"{nom_projet} — Fichiers ajoutés (git add .)")
    except Exception as e:
        resultat["statut"] = "erreur"
        resultat["message"] = f"Erreur git add : {e}"
        log_erreur(f"{nom_projet} — Erreur git add : {e}")
        return resultat

    # ── Étape 3 : git commit ──────────────────────────────────────────────
    horodatage = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message_commit = f"Mise à jour auto - {horodatage}"

    try:
        commit_result = executer_commande(
            ["git", "commit", "-m", message_commit], cwd=chemin
        )
        if commit_result.returncode != 0:
            raise RuntimeError(commit_result.stderr.strip())
        log_succes(f"{nom_projet} — Commit créé : \"{message_commit}\"")
    except Exception as e:
        resultat["statut"] = "erreur"
        resultat["message"] = f"Erreur git commit : {e}"
        log_erreur(f"{nom_projet} — Erreur git commit : {e}")
        return resultat

    # ── Étape 4 : git push ────────────────────────────────────────────────
    try:
        push_result = executer_commande(["git", "push"], cwd=chemin)
        if push_result.returncode != 0:
            stderr_msg = push_result.stderr.strip()
            # Si pas d'upstream configuré, on réessaie avec --set-upstream
            if "no upstream branch" in stderr_msg or "has no upstream" in stderr_msg:
                log_info(f"{nom_projet} — Pas d'upstream, configuration automatique...")
                # Détecter la branche courante
                branch_result = executer_commande(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=chemin
                )
                branche = branch_result.stdout.strip() or "main"
                push_result = executer_commande(
                    ["git", "push", "--set-upstream", "origin", branche], cwd=chemin
                )
                if push_result.returncode != 0:
                    raise RuntimeError(push_result.stderr.strip())
            elif "error" in stderr_msg.lower() or "fatal" in stderr_msg.lower():
                raise RuntimeError(stderr_msg)
        log_succes(f"{nom_projet} — Push effectué vers GitHub ({GITHUB_USER})")
    except Exception as e:
        resultat["statut"] = "partiel"
        resultat["message"] = f"Commit OK mais erreur push : {e}"
        log_avertissement(f"{nom_projet} — Commit OK mais push échoué : {e}")
        return resultat

    resultat["statut"] = "succès"
    resultat["message"] = f"Commit & push OK — {message_commit}"
    return resultat


# ──────────────────────────────────────────────────────────────────────────────
# Fonction principale
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    # Déterminer le répertoire parent à scanner
    if len(sys.argv) > 1:
        repertoire_parent = sys.argv[1]
    else:
        repertoire_parent = REPERTOIRE_PARENT_DEFAUT

    repertoire_parent = os.path.abspath(repertoire_parent)

    if not os.path.isdir(repertoire_parent):
        log_erreur(f"Le répertoire '{repertoire_parent}' n'existe pas.")
        sys.exit(1)

    # ── En-tête ───────────────────────────────────────────────────────────
    print()
    print(f"{Couleurs.GRAS}{'═' * 65}{Couleurs.RESET}")
    print(f"{Couleurs.GRAS}  AUTO GIT — Synchronisation multi-projets{Couleurs.RESET}")
    print(f"{Couleurs.GRAS}{'═' * 65}{Couleurs.RESET}")
    print(f"  Répertoire : {repertoire_parent}")
    print(f"  GitHub      : https://github.com/{GITHUB_USER}")
    print(f"  Date        : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{Couleurs.GRAS}{'─' * 65}{Couleurs.RESET}")
    print()

    # ── Scanner les sous-dossiers ─────────────────────────────────────────
    resultats: list[dict] = []
    sous_dossiers = sorted([
        os.path.join(repertoire_parent, d)
        for d in os.listdir(repertoire_parent)
        if os.path.isdir(os.path.join(repertoire_parent, d))
    ])

    if not sous_dossiers:
        log_avertissement("Aucun sous-dossier trouvé dans le répertoire parent.")
        return

    depots_trouves = 0

    for chemin in sous_dossiers:
        nom = os.path.basename(chemin)

        if not est_depot_git(chemin):
            log_avertissement(f"{nom} — Pas un dépôt Git, ignoré.")
            continue

        depots_trouves += 1
        print(f"\n{Couleurs.GRAS}▶ Traitement de : {nom}{Couleurs.RESET}")
        print(f"  {'─' * 50}")

        resultat = traiter_depot(chemin)
        resultats.append(resultat)

    # ── Log récapitulatif ─────────────────────────────────────────────────
    print()
    print(f"{Couleurs.GRAS}{'═' * 65}{Couleurs.RESET}")
    print(f"{Couleurs.GRAS}  RÉCAPITULATIF{Couleurs.RESET}")
    print(f"{Couleurs.GRAS}{'═' * 65}{Couleurs.RESET}")
    print(f"  Dossiers scannés  : {len(sous_dossiers)}")
    print(f"  Dépôts Git trouvés: {depots_trouves}")
    print()

    if not resultats:
        log_info("Aucun dépôt Git trouvé dans le répertoire.")
        return

    # Compteurs par statut
    nb_succes  = sum(1 for r in resultats if r["statut"] == "succès")
    nb_ignores = sum(1 for r in resultats if r["statut"] == "ignoré")
    nb_erreurs = sum(1 for r in resultats if r["statut"] == "erreur")
    nb_partiel = sum(1 for r in resultats if r["statut"] == "partiel")

    # Tableau récapitulatif
    print(f"  {'Projet':<35} {'Statut':<12} {'Détail'}")
    print(f"  {'─' * 35} {'─' * 12} {'─' * 40}")

    for r in resultats:
        statut = r["statut"]
        if statut == "succès":
            icone = f"{Couleurs.VERT}✔ succès {Couleurs.RESET}"
        elif statut == "ignoré":
            icone = f"{Couleurs.CYAN}– ignoré {Couleurs.RESET}"
        elif statut == "partiel":
            icone = f"{Couleurs.JAUNE}⚠ partiel{Couleurs.RESET}"
        else:
            icone = f"{Couleurs.ROUGE}✖ erreur {Couleurs.RESET}"

        print(f"  {r['projet']:<35} {icone}  {r['message']}")

    print()
    print(f"  {Couleurs.VERT}✔ Succès : {nb_succes}{Couleurs.RESET}  |  "
          f"{Couleurs.CYAN}– Ignorés : {nb_ignores}{Couleurs.RESET}  |  "
          f"{Couleurs.JAUNE}⚠ Partiels : {nb_partiel}{Couleurs.RESET}  |  "
          f"{Couleurs.ROUGE}✖ Erreurs : {nb_erreurs}{Couleurs.RESET}")
    print(f"\n{Couleurs.GRAS}{'═' * 65}{Couleurs.RESET}\n")


if __name__ == "__main__":
    main()
