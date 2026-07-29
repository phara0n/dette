# 💸 Dette — Gestion de dettes entre amis

**Dette** est une application web moderne, rapide et épurée permettant de gérer facilement les emprunts, achats et remboursements entre amis avec conversion automatique de devises (**USD** / **EUR** / **CAD** / **TND** → **TND** - Dinar Tunisien).

---

## 🌟 Fonctionnalités Principales

- **💵 Conversion de devises automatique & Historique des taux** :
  - Enregistrement des achats et des remboursements en **USD ($)**, **EUR (€)**, **CAD (C$)** ou **TND (DT)**.
  - Conversion automatique en **TND** selon le taux de change interbancaire officiel du jour (via l'API Frankfurter / Banque Centrale Européenne).
  - Option de saisie d'un **taux manuel personnalisé** lors de la création d'une transaction.
  - Affichage clair du taux de conversion appliqué à la date exacte de la transaction (`1 EUR = X.XXXX TND`).
- **👥 Modèle de dette commune & Indication des acteurs** :
  - **Dette commune et indissociable** : Un solde net unique calculé par ami.
  - Badges indicatifs **`[Mehdi]`** / **`[Fayçal]`** sur chaque transaction pour savoir qui a effectué l'achat ou le remboursement et quand.
- **🔄 3 types de transactions** :
  - 🛒 **Achats** : Ce qu'un ami achète pour le groupe (augmente la dette envers l'ami).
  - 💰 **Remboursements** : Ce qui est remboursé à l'ami en toute devise (réduit la dette).
  - 🔧 **Compensations** : Services ou travaux rendus à l'ami (payés localement, réduisent la dette).
- **📊 Tableau de bord clair & synthétique** :
  - Synthèse globale : **Total Dû Global**, **Total Achats**, **Total Remboursements**.
  - Tableau récapitulatif des soldes nets par ami.
  - Fil d'actualité chronologique des 10 dernières opérations.
- **🎨 Interface Soignée** :
  - Support natif **Dark Mode / Light Mode** (bascule automatique ou manuelle).
  - Typographie comptable monospacée (`tabular-nums`) pour une lisibilité parfaite des montants.
  - Design réactif et fluide adapté aux mobiles et ordinateurs.

---

## 📐 Modèle de Calcul

```text
Solde Net (Ami) = Σ Achats (TND) - Σ Remboursements (TND) - Σ Compensations (TND)
```

- **Solde Net > 0** : Vous devez de l'argent à cet ami (+).
- **Solde Net < 0** : L'ami vous doit de l'argent / vous êtes en avance (-).
- **Total Dû Global** = Somme des soldes nets positifs envers l'ensemble des amis.

---

## 🛠️ Stack Technique

- **Backend** : Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy, SQLite
- **Frontend** : Jinja2, [HTMX](https://htmx.org/), CSS3 Custom Design System
- **Taux de Change** : [Frankfurter API](https://www.frankfurter.app/) (Taux interbancaires BCE sans clé API)
- **Déploiement** : Systemd / Uvicorn ou Docker Compose, Reverse Proxy Nginx

---

## 📂 Arborescence du Projet

```text
dette/
├── app/
│   ├── main.py              # Point d'entrée de l'application FastAPI & migrations SQLite
│   ├── database.py          # Configuration SQLite & SQLAlchemy
│   ├── models.py            # Modèles (Friend, Purchase, Repayment, Compensation, ExchangeRate)
│   ├── routes/              # Routeurs FastAPI (dashboard, friends, purchases, repayments, compensations)
│   ├── services/            # Logique métier & service de taux de change (exchange.py)
│   ├── static/              # Design System CSS (style.css, pico.min.css)
│   └── templates/           # Templates HTML Jinja2 (base, dashboard, friend_detail, forms...)
├── data/                    # Base de données SQLite (dette.db)
├── Dockerfile               # Image Docker de l'application
├── docker-compose.yml       # Configuration Docker Compose
├── requirements.txt         # Dépendances Python
└── README.md
```

---

## 🚀 Installation & Lancement en Local

### 1. Prérequis
- Python 3.10+
- `pip` & `venv`

### 2. Lancement rapide

```bash
# Cloner le dépôt
git clone git@github.com:phara0n/dette.git
cd dette

# Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur de développement
uvicorn app.main:app --reload --port 8000
```

Accédez à l'application dans votre navigateur : **`http://127.0.0.1:8000`**

---

## 🔮 Feuille de Route & Développements Futurs (Roadmap)

Les évolutions et fonctionnalités prévues pour les futures versions :

### 1. 📊 Graphiques & Statistiques
- [ ] Graphiques d'évolution temporelle du solde par ami (Chart.js / ApexCharts).
- [ ] Répartition visuelle des dépenses par catégorie ou par acheteur (`Mehdi` vs `Fayçal`).

### 2. ✏️ Édition & Gestion des Transactions
- [ ] Modification directe des transactions existantes (achats, remboursements, compensations) sans devoir supprimer et recréer.
- [ ] Ajout de catégories / tags personnalisés sur les achats (ex: *Voyage, Logement, Matériel, Nourriture*).

### 3. 📄 Export & Rapports
- [ ] Export du relevé de compte d'un ami au format **PDF** ou **Excel / CSV**.
- [ ] Relevé mensuel synthétique téléchargeable.

### 4. 🔍 Recherche & Filtres Avancés
- [ ] Barre de recherche globale par mot-clé dans les descriptions et notes.
- [ ] Filtrage des transactions par plage de dates ou par devise.

### 5. 🔐 Sécurité & Multi-utilisateurs
- [ ] Système d'authentification avec comptes utilisateurs et rôles.
- [ ] Partage d'un lien de consultation en lecture seule pour un ami.

### 6. 🔔 Notifications & Rappels
- [ ] Notification ou rappel pour les soldes impayés depuis longtemps.

---

## 📝 Licence

Projet sous licence libre — Développé pour la gestion de dettes entre amis.
