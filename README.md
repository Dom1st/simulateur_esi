# 🏠 Simulateur de Vente Immobilière

## 🎯 Objectif

Cette application permet de simuler le coût d’acquisition d’un bien immobilier en fonction :

* du **prix net vendeur (PNV)**
* des **honoraires d’agence**
* des **frais de notaire**

Elle est conçue pour être utilisée en situation réelle par un agent immobilier avec son client, en intégrant des logiques de **négociation commerciale**.

---

## ⚙️ Fonctionnement général

L’application repose sur un principe simple :

> Le **prix net vendeur (PNV)** est la donnée principale,
> les **honoraires** et les **coûts acquéreur** sont recalculés dynamiquement.

---

## 💼 Modes de calcul des honoraires

Trois modes sont disponibles :

### 1. 📊 Barème agence

* Les honoraires sont calculés automatiquement selon un barème défini.
* Le résultat peut être :

  * un **forfait en euros**
  * ou un **taux (%)**

#### Comportement

* Si le **PNV change** :

  * les **honoraires (€)** sont recalculés
  * le **taux (%)** est recalculé

#### UI

* Taux : affiché (non éditable)
* Montant : affiché (non éditable)

---

### 2. 📈 Taux fixe (négocié)

* L’agent (ou le client) fixe un **taux (%)**
* Les honoraires sont calculés à partir de ce taux

#### Comportement

* Si le **PNV change** :

  * les **honoraires (€)** sont recalculés
* Si le **taux change** :

  * les **honoraires (€)** sont recalculés

#### UI

* Taux : éditable
* Montant : calculé automatiquement (non éditable)

---

### 3. 💰 Forfait (négocié)

* L’agent fixe un **montant en euros**
* Le taux est uniquement indicatif

#### Comportement

* Si le **montant change** :

  * le **taux affiché** est calculé à partir du PNV courant
* Si le **PNV change** :

  * le **montant reste fixe**
  * le **taux affiché reste figé**

#### ⚠️ Important

Le taux affiché en mode forfait est une **valeur mémorisée**,
et **ne reflète pas nécessairement le taux réel sur le nouveau PNV**.

#### UI

* Montant : éditable
* Taux : affiché (non éditable, figé)

---

## 🔄 Règles de recalcul

| Action utilisateur          | Barème         | Taux fixe  | Forfait                   |
| --------------------------- | -------------- | ---------- | ------------------------- |
| Modification du PNV         | recalcul € + % | recalcul € | aucun recalcul            |
| Modification du taux (%)    | —              | recalcul € | —                         |
| Modification du montant (€) | —              | —          | recalcul % (figé ensuite) |

---

## 📊 Données calculées

Pour chaque simulation, l’application calcule :

* Prix net vendeur
* Honoraires (€)
* Taux honoraires (%)
* Prix FAI (Frais d’Agence Inclus)
* Coût acquéreur total
* Coût avec frais de notaire réduits

---

## 📈 Visualisation

Un graphique permet de visualiser l’impact de variations du prix vendeur :

* de 0% à -5%
* avec affichage :

  * Prix net vendeur
  * Prix FAI
  * Coût total acquéreur
  * Version avec réduction des frais de notaire

---

## 📄 Export PDF

L’application permet de générer un PDF incluant :

* le graphique
* les informations client
* le mode d’honoraires utilisé

---

## 🧾 Gestion des configurations

### 🔹 Fichier profil

Le fichier `.streamlit/profile.toml` contient :

* le titre de l’application
* le fichier de configuration chargé au démarrage
* le barème des honoraires

### 🔹 Fichiers client

Les configurations client sont stockées dans `configs/*.txt` :

* identifiant client
* mandat
* paramètres financiers
* mode d’honoraires

---

## 🤝 Logique métier (négociation)

L’application reflète la réalité terrain :

> **Tout est négociable.**

* Le client peut accepter :

  * le **barème standard**
* ou négocier :

  * un **taux**
  * un **forfait**

L’outil permet de simuler ces scénarios en direct avec le client.

---

## 🚀 Philosophie

* Simple à utiliser
* Réactif en rendez-vous client
* Transparent sur les coûts
* Adapté à la négociation commerciale

---

## 🛠️ Améliorations possibles

* édition du barème dans l’UI
* gestion multi-profils
* historique des simulations
* export Excel
* signature client

---

## 📌 Remarque

Le mode **forfait** introduit volontairement une dissociation entre :

* le montant réel
* le taux affiché

Cela correspond à un usage métier réel où le **forfait est prioritaire sur le taux**.

---
