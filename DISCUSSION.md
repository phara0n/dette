# Discussion — Projet Dette

## Contexte
L'utilisateur a besoin d'une appli web pour gérer ses dettes entre amis, à déployer sur son VPS.

## Concept métier
- Des amis achètent des choses pour l'utilisateur en **USD** ou **EUR**
- L'utilisateur les rembourse **petit à petit** en **TND** (Dinar Tunisien)
- Les achats sont convertis **au taux du jour de l'achat** (USD/EUR → TND)
- L'utilisateur peut aussi rendre des **services / bricoles** à ses amis (qu'il paye localement) → ces compensations réduisent la dette

### Calcul du solde
```
Solde(ami) = Σ achats(ami).montant_tnd − Σ remboursements(ami).montant_tnd − Σ compensations(ami).montant_tnd
```

## Décisions techniques

| Décision | Choix |
|----------|-------|
| Backend | Python FastAPI |
| Base de données | SQLite |
| Frontend | Jinja2 + HTMX + Pico.css |
| Taux de change | frankfurter.app (gratuit, pas de clé API) |
| Utilisateurs | Solo (pas d'auth) |
| Interface | Web classique + API |
| Déploiement | Docker Compose |
| Emplacement | `~/Projects/active/dette/` |

## Transactions

| Type | Sens | Devise | Effet sur la dette |
|------|------|--------|--------------------|
| Achat | Ami → Moi | USD/EUR → TND | ↑ (augmente) |
| Remboursement | Moi → Ami | TND | ↓ (réduit) |
| Compensation | Moi → Ami (service) | TND | ↓ (réduit) |

## Modèle de données
- **friends** — id, name, created_at
- **exchange_rates** — id, from_currency, to_currency, rate, date
- **purchases** — id, friend_id, description, amount, currency, exchange_rate_id, amount_tnd, purchase_date
- **repayments** — id, friend_id, amount_tnd, date, notes
- **compensations** — id, friend_id, description, amount_tnd, date

## Fichier des specs
Voir `SPEC.md` pour le détail complet.
