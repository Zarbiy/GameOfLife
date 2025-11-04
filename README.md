# 🧬 Life is a Game — Jeu de la Vie (PyQt6)

Une implémentation interactive et visuelle du célèbre **Jeu de la Vie de Conway**, développée en **Python (PyQt6)**.  
Le projet permet de créer, importer et observer des motifs vivants évoluer selon les règles du jeu, avec des contrôles de vitesse, zoom et affichage.

---

## Fonctionnalités

- **Play / Pause** : Lance ou arrête la simulation.  
- **Clear** : Réinitialise la grille.  
- **Import Pattern** : Importe un fichier `.txt` contenant un motif (`1` ou `O` = cellule vivante).  
- **Grille affichable / masquable** : Affiche ou masque les lignes de la grille.  
- **Contrôle de la vitesse** :  
  - `+` : accélère la simulation
  - `-` : ralentit la simulation  
- **Zoom à la molette**
- **Déplacement** : clique gauche + glisser pour déplacer la vue.  
- **Clic droit** : ajoute / supprime une cellule vivante.  

---

## Installation

```bash
cd life-is-a-game
python3 -m venv venv
source venv/bin/activate
pip install -r req.txt
python main.py
