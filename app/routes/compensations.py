from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Compensation, Friend
from ..templates import templates

router = APIRouter(prefix="/friends/{friend_id}/compensations", tags=["compensations"])


@router.get("/new", response_class=HTMLResponse)
def new_compensation_form(friend_id: int, request: Request, db: Session = Depends(get_db)):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    today = date.today().isoformat()
    return templates.TemplateResponse(request, "compensation_form.html", {
        "friend": friend,
        "today": today,
        "error": None,
    })


@router.post("")
def create_compensation(
    friend_id: int,
    request: Request,
    description: str = Form(...),
    amount_tnd: float = Form(...),
    compensation_date: str = Form(...),
    borrower: str = Form(...),
    db: Session = Depends(get_db),
):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")

    errors = []
    if not description.strip():
        errors.append("La description est requise")
    if amount_tnd <= 0:
        errors.append("Le montant doit être positif")
    if borrower not in ("Mehdi", "Faycal"):
        errors.append("Emprunteur invalide")

    try:
        c_date = date.fromisoformat(compensation_date)
    except (ValueError, TypeError):
        errors.append("Date invalide")

    if errors:
        return templates.TemplateResponse(request, "compensation_form.html", {
            "friend": friend,
            "today": date.today().isoformat(),
            "error": " ".join(errors),
        }, status_code=400)

    compensation = Compensation(
        friend_id=friend_id,
        description=description.strip(),
        amount_tnd=amount_tnd,
        date=c_date,
        borrower=borrower,
    )
    db.add(compensation)
    db.commit()

    return RedirectResponse(f"/friends/{friend_id}", 303)


@router.post("/{compensation_id}/delete")
def delete_compensation(friend_id: int, compensation_id: int, db: Session = Depends(get_db)):
    compensation = db.query(Compensation).filter(Compensation.id == compensation_id, Compensation.friend_id == friend_id).first()
    if not compensation:
        raise HTTPException(404, "Compensation introuvable")
    db.delete(compensation)
    db.commit()
    return RedirectResponse(f"/friends/{friend_id}", 303)
