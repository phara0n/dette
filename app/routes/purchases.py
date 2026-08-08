from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ExchangeRate, Friend, Purchase
from ..services.exchange import get_or_fetch_rate
from ..templates import redirect_to, templates

router = APIRouter(prefix="/friends/{friend_id}/purchases", tags=["purchases"])


@router.get("/new", response_class=HTMLResponse)
def new_purchase_form(friend_id: int, request: Request, db: Session = Depends(get_db)):
    friend = db.get(Friend, friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    today = date.today().isoformat()
    return templates.TemplateResponse(request, "purchase_form.html", {
        "friend": friend,
        "today": today,
        "error": None,
    })


@router.post("")
async def create_purchase(
    friend_id: int,
    request: Request,
    description: str = Form(...),
    amount: float = Form(...),
    currency: str = Form(...),
    purchase_date: str = Form(...),
    borrower: str = Form(...),
    manual_rate: str | None = Form(None),
    db: Session = Depends(get_db),
):
    friend = db.get(Friend, friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")

    errors = []
    if not description.strip():
        errors.append("La description est requise")
    if amount <= 0:
        errors.append("Le montant doit être positif")
    if currency not in ("USD", "EUR", "CAD", "TND"):
        errors.append("Devise invalide")
    if borrower not in ("Mehdi", "Faycal"):
        errors.append("Emprunteur invalide")

    try:
        p_date = date.fromisoformat(purchase_date)
    except (ValueError, TypeError):
        errors.append("Date invalide")

    if errors:
        return templates.TemplateResponse(request, "purchase_form.html", {
            "friend": friend,
            "today": date.today().isoformat(),
            "error": " ".join(errors),
        }, status_code=400)

    parsed_rate: float | None = None
    if manual_rate and manual_rate.strip():
        try:
            parsed_rate = float(manual_rate)
        except ValueError:
            errors.append("Taux manuel invalide")
            return templates.TemplateResponse(request, "purchase_form.html", {
                "friend": friend,
                "today": date.today().isoformat(),
                "error": " ".join(errors),
            }, status_code=400)

    if parsed_rate is not None and parsed_rate > 0:
        rate = parsed_rate
    else:
        rate = await get_or_fetch_rate(currency, "TND", p_date, db)
        if rate is None:
            rate = await get_or_fetch_rate(currency, "TND", date.today(), db)
        if rate is None:
            return templates.TemplateResponse(request, "purchase_form.html", {
                "friend": friend,
                "today": date.today().isoformat(),
                "error": "Impossible de récupérer le taux de change. Saisissez-le manuellement.",
            }, status_code=400)

    db_rate = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == currency,
        ExchangeRate.to_currency == "TND",
        ExchangeRate.rate == rate,
    ).first()

    if not db_rate:
        db_rate = ExchangeRate(from_currency=currency, to_currency="TND", rate=rate, date=p_date)
        db.add(db_rate)
        db.commit()
        db.refresh(db_rate)

    amount_tnd = round(amount * rate, 3)

    purchase = Purchase(
        friend_id=friend_id,
        description=description.strip(),
        amount=amount,
        currency=currency,
        exchange_rate_id=db_rate.id,
        amount_tnd=amount_tnd,
        purchase_date=p_date,
        borrower=borrower,
    )
    db.add(purchase)
    db.commit()

    return redirect_to(f"/friends/{friend_id}")


@router.post("/{purchase_id}/delete")
def delete_purchase(friend_id: int, purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id, Purchase.friend_id == friend_id).first()
    if not purchase:
        raise HTTPException(404, "Achat introuvable")
    db.delete(purchase)
    db.commit()
    return redirect_to(f"/friends/{friend_id}")


@router.get("/{purchase_id}/edit", response_class=HTMLResponse)
def edit_purchase_form(friend_id: int, purchase_id: int, request: Request, db: Session = Depends(get_db)):
    friend = db.get(Friend, friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id, Purchase.friend_id == friend_id).first()
    if not purchase:
        raise HTTPException(404, "Achat introuvable")
    return templates.TemplateResponse(request, "purchase_form.html", {
        "friend": friend,
        "purchase": purchase,
        "today": purchase.purchase_date.isoformat(),
        "error": None,
    })


@router.post("/{purchase_id}/edit")
async def update_purchase(
    friend_id: int,
    purchase_id: int,
    request: Request,
    description: str = Form(...),
    amount: float = Form(...),
    currency: str = Form(...),
    purchase_date: str = Form(...),
    borrower: str = Form(...),
    manual_rate: str | None = Form(None),
    db: Session = Depends(get_db),
):
    friend = db.get(Friend, friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id, Purchase.friend_id == friend_id).first()
    if not purchase:
        raise HTTPException(404, "Achat introuvable")

    errors = []
    if not description.strip():
        errors.append("La description est requise")
    if amount <= 0:
        errors.append("Le montant doit être positif")
    if currency not in ("USD", "EUR", "CAD", "TND"):
        errors.append("Devise invalide")
    if borrower not in ("Mehdi", "Faycal"):
        errors.append("Emprunteur invalide")

    try:
        p_date = date.fromisoformat(purchase_date)
    except (ValueError, TypeError):
        errors.append("Date invalide")

    if errors:
        return templates.TemplateResponse(request, "purchase_form.html", {
            "friend": friend,
            "purchase": purchase,
            "today": purchase_date,
            "error": " ".join(errors),
        }, status_code=400)

    parsed_rate: float | None = None
    if manual_rate and manual_rate.strip():
        try:
            parsed_rate = float(manual_rate)
        except ValueError:
            errors.append("Taux manuel invalide")
            return templates.TemplateResponse(request, "purchase_form.html", {
                "friend": friend,
                "purchase": purchase,
                "today": purchase_date,
                "error": " ".join(errors),
            }, status_code=400)

    if parsed_rate is not None and parsed_rate > 0:
        rate = parsed_rate
    elif currency == "TND":
        rate = 1.0
    else:
        rate = await get_or_fetch_rate(currency, "TND", p_date, db)
        if rate is None:
            rate = await get_or_fetch_rate(currency, "TND", date.today(), db)
        if rate is None:
            return templates.TemplateResponse(request, "purchase_form.html", {
                "friend": friend,
                "purchase": purchase,
                "today": purchase_date,
                "error": "Impossible de récupérer le taux de change. Saisissez-le manuellement.",
            }, status_code=400)

    db_rate = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == currency,
        ExchangeRate.to_currency == "TND",
        ExchangeRate.rate == rate,
    ).first()

    if not db_rate:
        db_rate = ExchangeRate(from_currency=currency, to_currency="TND", rate=rate, date=p_date)
        db.add(db_rate)
        db.commit()
        db.refresh(db_rate)

    purchase.description = description.strip()
    purchase.amount = amount
    purchase.currency = currency
    purchase.exchange_rate_id = db_rate.id
    purchase.amount_tnd = round(amount * rate, 3)
    purchase.purchase_date = p_date
    purchase.borrower = borrower
    db.commit()

    return redirect_to(f"/friends/{friend_id}")
