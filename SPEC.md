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
| from_currency | TEXT | USD, EUR, CAD, TND |
| to_currency | TEXT | TND |
| rate | REAL | Taux de conversion |
| date | DATE | Date du taux |

### purchases (Ami → Groupe)
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| friend_id | FK → friends | |
| description | TEXT | |
| amount | REAL | Montant en devise d'origine |
| currency | TEXT | USD, EUR, CAD, TND |
| exchange_rate_id | FK → exchange_rates | |
| amount_tnd | REAL | Montant converti en TND |
| purchase_date | DATE | |
| borrower | TEXT | Mehdi ou Faycal (indicatif) |
| created_at | DATETIME | |

### repayments (Groupe → Ami)
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| friend_id | FK → friends | |
| amount | REAL | Montant en devise d'origine (optionnel) |
| currency | TEXT | USD, EUR, CAD, TND (optionnel) |
| exchange_rate_id | FK → exchange_rates | Taux de change (optionnel) |
| amount_tnd | REAL | Montant converti en TND |
| date | DATE | |
| notes | TEXT | |
| paid_by | TEXT | Mehdi ou Faycal (indicatif) |
| borrower | TEXT | Mehdi ou Faycal (indicatif) |
| created_at | DATETIME | |

### compensations (Groupe → Ami, services/bricoles)
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PK | |
| friend_id | FK → friends | |
| description | TEXT | |
| amount_tnd | REAL | Ce que tu as payé |
| date | DATE | |
| borrower | TEXT | Mehdi ou Faycal (indicatif) |
| created_at | DATETIME | |

## Calcul du solde
```
Solde Net (ami) = Σ purchases.amount_tnd - Σ repayments.amount_tnd - Σ compensations.amount_tnd
```
Solde > 0 → le groupe doit de l'argent à l'ami
Solde < 0 → l'ami doit au groupe (en avance / trop remboursé)

## Pages & Routes
- `/` — Dashboard (total dû global, soldes par ami, dernières transactions)
- `/friends` — Liste des amis & création d'ami
- `/friends/{id}` — Fiche détaillée d'un ami (achats, remboursements, compensations, solde)
- `/friends/{id}/purchases/new` — Ajouter un achat
- `/friends/{id}/purchases/{id}/edit` — Modifier un achat
- `/friends/{id}/repayments/new` — Ajouter un remboursement
- `/friends/{id}/repayments/{id}/edit` — Modifier un remboursement
- `/friends/{id}/compensations/new` — Ajouter une compensation
- `/friends/{id}/compensations/{id}/edit` — Modifier une compensation
