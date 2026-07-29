from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BORROWERS, Compensation, Friend, Purchase, Repayment
from ..templates import templates

router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    friends = db.query(Friend).order_by(Friend.name).all()

    friend_balances = []
    for f in friends:
        friend_balances.append({
            "friend": f,
            "balance": f.balance,
            "borrower_balances": {b: f.balance_for(b) for b in BORROWERS},
            "purchases_count": len(f.purchases),
        })

    borrower_totals = {}
    for borrower in BORROWERS:
        owed = 0.0
        for f in friends:
            bal = f.balance_for(borrower)
            if bal > 0:
                owed += bal
        borrower_totals[borrower] = owed

    total_owed = sum(borrower_totals.values())

    recent_items = []
    recent_purchases = db.query(Purchase).order_by(Purchase.created_at.desc()).limit(5).all()
    for p in recent_purchases:
        if p.currency != "TND":
            rate = p.exchange_rate.rate if p.exchange_rate else (p.amount_tnd / p.amount if p.amount > 0 else 0)
            amt_str = f"{p.amount} {p.currency} → {p.amount_tnd:.3f} TND (1 {p.currency} = {rate:.4f} TND)"
        else:
            amt_str = f"{p.amount_tnd:.3f} TND"
        recent_items.append({
            "type": "achat",
            "date": p.purchase_date,
            "friend": p.friend.name,
            "description": p.description,
            "amount": amt_str,
            "icon": "🛒",
            "borrower": p.borrower,
        })

    recent_repayments = db.query(Repayment).order_by(Repayment.created_at.desc()).limit(5).all()
    for r in recent_repayments:
        if r.amount and r.currency and r.currency != "TND":
            rate = r.exchange_rate.rate if r.exchange_rate else (r.amount_tnd / r.amount if r.amount > 0 else 0)
            amt_str = f"{r.amount} {r.currency} → {r.amount_tnd:.3f} TND (1 {r.currency} = {rate:.4f} TND)"
        else:
            amt_str = f"{r.amount_tnd:.3f} TND"
        recent_items.append({
            "type": "remboursement",
            "date": r.date,
            "friend": r.friend.name,
            "description": r.notes or "Remboursement",
            "amount": amt_str,
            "icon": "💰",
            "borrower": r.borrower,
        })

    recent_compensations = db.query(Compensation).order_by(Compensation.created_at.desc()).limit(5).all()
    for c in recent_compensations:
        recent_items.append({
            "type": "compensation",
            "date": c.date,
            "friend": c.friend.name,
            "description": c.description,
            "amount": f"{c.amount_tnd:.3f} TND",
            "icon": "🔧",
            "borrower": c.borrower,
        })

    recent_items.sort(key=lambda x: x["date"], reverse=True)
    recent_items = recent_items[:10]

    return templates.TemplateResponse(request, "dashboard.html", {
        "friend_balances": friend_balances,
        "total_owed": total_owed,
        "borrower_totals": borrower_totals,
        "recent_items": recent_items,
    })
