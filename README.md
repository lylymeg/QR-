# 📲 Générateur & Lecteur de QR Code (PyQt5)

Un outil complet de génération et de décodage de QR Codes avec une interface graphique moderne sous thème Dark.

---

## 🌟 Fonctionnalités

- **Génération personnalisée** :
  - Conversion de texte brut ou d'URL en QR code.
  - Personnalisation des couleurs du code et du fond via un sélecteur de couleurs (`QColorDialog`).
  - Exportation directe en format `PNG` ou `JPG`.
- **Lecture et Décodage** :
  - Importation d'images (`PNG`, `JPG`, `BMP`).
  - Décodage automatique du contenu hébergé dans le QR code via `pyzbar`.
  - Affichage propre du texte extrait.

---

## 🛠️ Prérequis et Dépendances

L'application nécessite les bibliothèques Python suivantes :

```bash
pip install PyQt5 qrcode Pillow pyzbar