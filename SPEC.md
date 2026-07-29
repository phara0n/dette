# Dette - Appli de gestion de dettes entre amis

## Concept
Gérer les emprunts/achats faits par des amis (en USD/EUR), avec conversion automatique en TND (Dinar Tunisien) au taux du jour. Chaque ami a un solde qui évolue avec :
- Les achats qu'il fait pour toi (augmente ta dette)
- Les remboursements que tu lui fais (réduit ta dette)
- Les compensations (services/bricoles que tu fais pour lui, payés par toi) (réduit ta dette)

## Stack
- **Backend** : Python FastAPI
- **Base de données** : SQLite
- **Frontend** : Jinja2 + HTMX + Pico.css
- **Taux de change** : frankfurter.dev v2 (gratuit, pas de clé API)
- **Déploiement** : Docker Compose (Nginx + Uvicorn)

## Modèle de données

### friends
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| name | TEXT | Nom de l'ami |
| created_at | DATETIME | |

### exchange_rates
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| from_currency | TEXT | USD, EUR |
| to_currency | TEXT | TND |
| rate | REAL | Taux de conversion |
| date | DATE | Date du taux |

### purchases (Ami → Toi)
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| friend_id | FK → friends | |
| description | TEXT | |
| amount | REAL | Montant en devise d'origine |
| currency | TEXT | USD ou EUR |
| exchange_rate_id | FK → exchange_rates | |
| amount_tnd | REAL | Montant converti en TND |
| purchase_date | DATE | |
| created_at | DATETIME | |

### repayments (Toi → Ami)
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| friend_id | FK → friends | |
| amount_tnd | REAL | |
| date | DATE | |
| notes | TEXT | |
| created_at | DATETIME | |

### compensations (Toi → Ami, services/bricoles)
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| friend_id | FK → friends | |
| description | TEXT | |
| amount_tnd | REAL | Ce que tu as payé |
| date | DATE | |
| created_at | DATETIME | |

## Calcul du solde
```
Solde(ami) = Σ purchases.amount_tnd - Σ repayments.amount_tnd - Σ compensations.amount_tnd
```
Solde > 0 → tu dois de l'argent à l'ami
Solde < 0 → l'ami te doit (trop remboursé / trop de compensations)

## Pages
- `/` — Dashboard (total dû global, par ami, dernières transactions)
- `/friends` — Liste des amis
- `/friends/{id}` — Détail d'un ami (achats, remboursements, compensations, solde)
- `/friends/{id}/purchase/new` — Ajouter un achat
- `/friends/{id}/repayment/new` — Ajouter un remboursement
- `/friends/{id}/compensation/new` — Ajouter une compensation
