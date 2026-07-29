from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ExchangeRate, Friend, Repayment
from ..services.exchange import get_or_fetch_rate
from ..templates import redirect_to, templates

router = APIRouter(prefix="/friends/{friend_id}/repayments", tags=["repayments"])


@router.get("/new", response_class=HTMLResponse)
def new_repayment_form(friend_id: int, request: Request, db: Session = Depends(get_db)):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    today = date.today().isoformat()
    return templates.TemplateResponse(request, "repayment_form.html", {
        "friend": friend,
        "today": today,
        "error": None,
    })


@router.post("")
async def create_repayment(
    friend_id: int,
    request: Request,
    amount: float | None = Form(None),
    amount_tnd: float | None = Form(None),
    currency: str = Form("TND"),
    repayment_date: str = Form(...),
    notes: str | None = Form(None),
    paid_by: str = Form(...),
    borrower: str | None = Form(None),
    manual_rate: str | None = Form(None),
    db: Session = Depends(get_db),
):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")

    if not borrower:
        borrower = paid_by

    amount_val = amount if amount is not None else amount_tnd
    errors = []
    if amount_val is None or amount_val <= 0:
        errors.append("Le montant doit être positif")
    if currency not in ("USD", "EUR", "CAD", "TND"):
        errors.append("Devise invalide")
    if borrower not in ("Mehdi", "Faycal"):
        errors.append("Emprunteur invalide")
    if paid_by not in ("Mehdi", "Faycal"):
        errors.append("Payeur invalide")

    try:
        r_date = date.fromisoformat(repayment_date)
    except (ValueError, TypeError):
        errors.append("Date invalide")

    if errors:
        return templates.TemplateResponse(request, "repayment_form.html", {
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
            return templates.TemplateResponse(request, "repayment_form.html", {
                "friend": friend,
                "today": date.today().isoformat(),
                "error": " ".join(errors),
            }, status_code=400)

    if parsed_rate is not None and parsed_rate > 0:
        rate = parsed_rate
    elif currency == "TND":
        rate = 1.0
    else:
        rate = await get_or_fetch_rate(currency, "TND", r_date, db)
        if rate is None:
            rate = await get_or_fetch_rate(currency, "TND", date.today(), db)
        if rate is None:
            return templates.TemplateResponse(request, "repayment_form.html", {
                "friend": friend,
                "today": date.today().isoformat(),
                "error": "Impossible de récupérer le taux de change. Saisissez-le manuellement.",
            }, status_code=400)

    db_rate = None
    if currency != "TND":
        db_rate = db.query(ExchangeRate).filter(
            ExchangeRate.from_currency == currency,
            ExchangeRate.to_currency == "TND",
            ExchangeRate.rate == rate,
        ).first()

        if not db_rate:
            db_rate = ExchangeRate(from_currency=currency, to_currency="TND", rate=rate, date=r_date)
            db.add(db_rate)
            db.commit()
            db.refresh(db_rate)

    calc_amount_tnd = round(amount_val * rate, 3)

    repayment = Repayment(
        friend_id=friend_id,
        amount=amount_val,
        currency=currency,
        exchange_rate_id=db_rate.id if db_rate else None,
        amount_tnd=calc_amount_tnd,
        date=r_date,
        notes=notes.strip() if notes else None,
        borrower=borrower,
        paid_by=paid_by,
    )
    db.add(repayment)
    db.commit()

    return redirect_to(f"/friends/{friend_id}")


@router.post("/{repayment_id}/delete")
def delete_repayment(friend_id: int, repayment_id: int, db: Session = Depends(get_db)):
    repayment = db.query(Repayment).filter(Repayment.id == repayment_id, Repayment.friend_id == friend_id).first()
    if not repayment:
        raise HTTPException(404, "Remboursement introuvable")
    db.delete(repayment)
    db.commit()
    return redirect_to(f"/friends/{friend_id}")


@router.get("/{repayment_id}/edit", response_class=HTMLResponse)
def edit_repayment_form(friend_id: int, repayment_id: int, request: Request, db: Session = Depends(get_db)):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    repayment = db.query(Repayment).filter(Repayment.id == repayment_id, Repayment.friend_id == friend_id).first()
    if not repayment:
        raise HTTPException(404, "Remboursement introuvable")
    return templates.TemplateResponse(request, "repayment_form.html", {
        "friend": friend,
        "repayment": repayment,
        "today": repayment.date.isoformat(),
        "error": None,
    })


@router.post("/{repayment_id}/edit")
async def update_repayment(
    friend_id: int,
    repayment_id: int,
    request: Request,
    amount: float | None = Form(None),
    amount_tnd: float | None = Form(None),
    currency: str = Form("TND"),
    repayment_date: str = Form(...),
    notes: str | None = Form(None),
    paid_by: str = Form(...),
    borrower: str | None = Form(None),
    manual_rate: str | None = Form(None),
    db: Session = Depends(get_db),
):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    repayment = db.query(Repayment).filter(Repayment.id == repayment_id, Repayment.friend_id == friend_id).first()
    if not repayment:
        raise HTTPException(404, "Remboursement introuvable")

    if not borrower:
        borrower = paid_by

    amount_val = amount if amount is not None else amount_tnd
    errors = []
    if amount_val is None or amount_val <= 0:
        errors.append("Le montant doit être positif")
    if currency not in ("USD", "EUR", "CAD", "TND"):
        errors.append("Devise invalide")

    try:
        r_date = date.fromisoformat(repayment_date)
    except (ValueError, TypeError):
        errors.append("Date invalide")

    if errors:
        return templates.TemplateResponse(request, "repayment_form.html", {
            "friend": friend,
            "repayment": repayment,
            "today": repayment_date,
            "error": " ".join(errors),
        }, status_code=400)

    parsed_rate: float | None = None
    if manual_rate and manual_rate.strip():
        try:
            parsed_rate = float(manual_rate)
        except ValueError:
            errors.append("Taux manuel invalide")
            return templates.TemplateResponse(request, "repayment_form.html", {
                "friend": friend,
                "repayment": repayment,
                "today": repayment_date,
                "error": " ".join(errors),
            }, status_code=400)

    if parsed_rate is not None and parsed_rate > 0:
        rate = parsed_rate
    elif currency == "TND":
        rate = 1.0
    else:
        rate = await get_or_fetch_rate(currency, "TND", r_date, db)
        if rate is None:
            rate = await get_or_fetch_rate(currency, "TND", date.today(), db)
        if rate is None:
            return templates.TemplateResponse(request, "repayment_form.html", {
                "friend": friend,
                "repayment": repayment,
                "today": repayment_date,
                "error": "Impossible de récupérer le taux de change. Saisissez-le manuellement.",
            }, status_code=400)

    db_rate = None
    if currency != "TND":
        db_rate = db.query(ExchangeRate).filter(
            ExchangeRate.from_currency == currency,
            ExchangeRate.to_currency == "TND",
            ExchangeRate.rate == rate,
        ).first()

        if not db_rate:
            db_rate = ExchangeRate(from_currency=currency, to_currency="TND", rate=rate, date=r_date)
            db.add(db_rate)
            db.commit()
            db.refresh(db_rate)

    calc_amount_tnd = round(amount_val * rate, 3)

    repayment.amount = amount_val
    repayment.currency = currency
    repayment.exchange_rate_id = db_rate.id if db_rate else None
    repayment.amount_tnd = calc_amount_tnd
    repayment.date = r_date
    repayment.notes = notes.strip() if notes else None
    repayment.paid_by = paid_by
    repayment.borrower = borrower
    db.commit()

    return redirect_to(f"/friends/{friend_id}")
