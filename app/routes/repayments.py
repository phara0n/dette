from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Friend, Repayment
from ..templates import templates

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
def create_repayment(
    friend_id: int,
    request: Request,
    amount_tnd: float = Form(...),
    repayment_date: str = Form(...),
    notes: str | None = Form(None),
    borrower: str = Form(...),
    paid_by: str = Form(...),
    db: Session = Depends(get_db),
):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")

    errors = []
    if amount_tnd <= 0:
        errors.append("Le montant doit être positif")
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

    repayment = Repayment(
        friend_id=friend_id,
        amount_tnd=amount_tnd,
        date=r_date,
        notes=notes.strip() if notes else None,
        borrower=borrower,
        paid_by=paid_by,
    )
    db.add(repayment)
    db.commit()

    return RedirectResponse(f"/friends/{friend_id}", 303)


@router.post("/{repayment_id}/delete")
def delete_repayment(friend_id: int, repayment_id: int, db: Session = Depends(get_db)):
    repayment = db.query(Repayment).filter(Repayment.id == repayment_id, Repayment.friend_id == friend_id).first()
    if not repayment:
        raise HTTPException(404, "Remboursement introuvable")
    db.delete(repayment)
    db.commit()
    return RedirectResponse(f"/friends/{friend_id}", 303)
