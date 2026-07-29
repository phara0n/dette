# 💸 Dette — Gestion de dettes entre amis

**Dette** est une application web moderne, rapide et épurée permettant de gérer facilement les emprunts, achats et remboursements entre amis avec conversion automatique de devises (**USD** / **EUR** → **TND** - Dinar Tunisien).

---

## 🌟 Fonctionnalités Principales

- **💵 Conversion de devises automatique** :
  - Saisie des achats en **USD ($)** ou **EUR (€)**.
  - Conversion automatique en **TND** selon le taux de change du jour (via l'API Frankfurter).
  - Option de saisie d'un taux manuel en cas de besoin.
- **👥 Gestion multi-emprunteurs** :
  - Suivi distinct des comptes et dettes pour **Mehdi** et **Fayçal**.
  - Modification rapide du nom d'un ami à tout moment.
- **🔄 3 types de transactions** :
  - 🛒 **Achats** : Ce qu'un ami achète pour vous (augmente la dette).
  - 💰 **Remboursements** : Ce que vous remboursez à l'ami en TND (réduit la dette).
  - 🔧 **Compensations** : Services ou bricoles rendus à l'ami (payés localement, réduisent la dette).
- **📊 Tableau de bord clair & synthétique** :
  - Vision immédiate du total dû global et des part respectives (Mehdi / Fayçal).
  - Fil d'actualité chronologique des dernières opérations.
- **🎨 Interface Soignée & Anti-IA-Slop** :
  - Support natif **Dark Mode / Light Mode** (bascule automatique ou manuelle).
  - Typographie comptable monospacée (`tabular-nums`) pour une lisibilité parfaite des montants.
  - Design réactif adapté aux mobiles et ordinateurs.

---

## 🛠️ Stack Technique

- **Backend** : Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy, SQLite
- **Frontend** : Jinja2, [HTMX](https://htmx.org/), CSS3 Custom Design System
- **Services** : [Frankfurter API](https://www.frankfurter.app/) (Taux de change gratuit sans clé API)
- **Déploiement** : Docker, Docker Compose, Uvicorn

---

## 📂 Arborescence du Projet

```text
dette/
├── app/
│   ├── main.py              # Point d'entrée de l'application FastAPI
│   ├── database.py          # Configuration SQLite & SQLAlchemy
│   ├── models.py            # Modèles de données (Friend, Purchase, Repayment, Compensation, ExchangeRate)
│   ├── routes/              # Handlers API / HTML (dashboard, friends, purchases, repayments, compensations)
│   ├── services/            # Logique métier & service de taux de change (exchange.py)
│   ├── static/              # Fichiers statiques (style.css, pico.min.css)
│   └── templates/           # Templates Jinja2 (base, dashboard, friend_detail, forms...)
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

## 🐳 Déploiement avec Docker Compose

L'application est entièrement conteneurisée pour un déploiement simple sur VPS.

```bash
# Lancer le conteneur en arrière-plan
docker-compose up -d --build
```

L'application sera accessible sur le port `8000`.

### 🌐 Déploiement sous un sous-dossier (Subpath VPS)

Si l'application est hébergée sous un sous-dossier (ex: `https://domain.com/dette/`), définissez la variable d'environnement `ROOT_PATH` lors du lancement ou dans votre fichier `.env` / `docker-compose.yml` :

```bash
ROOT_PATH=/dette docker-compose up -d --build
```

**Configuration Nginx minimale pour un sous-dossier :**
```nginx
location /dette/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Prefix /dette;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## 📝 Licence

Projet sous licence libre — Développé pour la gestion de dettes entre amis.
