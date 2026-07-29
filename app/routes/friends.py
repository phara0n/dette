from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BORROWERS, Compensation, Friend, Purchase, Repayment
from ..templates import redirect_to, templates

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("", response_class=HTMLResponse)
def list_friends(request: Request, db: Session = Depends(get_db)):
    friends = db.query(Friend).order_by(Friend.name).all()
    friend_data = []
    for f in friends:
        friend_data.append({
            "friend": f,
            "balance": f.balance,
        })
    total_owed = sum(d["balance"] for d in friend_data if d["balance"] > 0)
    return templates.TemplateResponse(request, "friends.html", {
        "friends": friend_data,
        "total_owed": total_owed,
    })


@router.post("", response_class=HTMLResponse)
def create_friend(name: str = Form(...), db: Session = Depends(get_db)):
    friend = Friend(name=name.strip())
    if not friend.name:
        raise HTTPException(400, "Le nom est requis")
    existing = db.query(Friend).filter(Friend.name == friend.name).first()
    if existing:
        raise HTTPException(400, "Cet ami existe déjà")
    db.add(friend)
    db.commit()
    return redirect_to("/friends")


@router.post("/{friend_id}/delete")
def delete_friend(friend_id: int, db: Session = Depends(get_db)):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    db.delete(friend)
    db.commit()
    return redirect_to("/friends")


@router.post("/{friend_id}/edit")
def update_friend(friend_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")
    new_name = name.strip()
    if not new_name:
        raise HTTPException(400, "Le nom est requis")
    existing = db.query(Friend).filter(Friend.name == new_name, Friend.id != friend_id).first()
    if existing:
        raise HTTPException(400, "Un autre ami porte déjà ce nom")
    friend.name = new_name
    db.commit()
    return redirect_to(f"/friends/{friend_id}")




@router.get("/{friend_id}", response_class=HTMLResponse)
def friend_detail(friend_id: int, request: Request, db: Session = Depends(get_db)):
    friend = db.query(Friend).get(friend_id)
    if not friend:
        raise HTTPException(404, "Ami introuvable")

    purchases = db.query(Purchase).filter(Purchase.friend_id == friend_id).order_by(Purchase.purchase_date.desc()).all()
    repayments = db.query(Repayment).filter(Repayment.friend_id == friend_id).order_by(Repayment.date.desc()).all()
    compensations = db.query(Compensation).filter(Compensation.friend_id == friend_id).order_by(Compensation.date.desc()).all()

    return templates.TemplateResponse(request, "friend_detail.html", {
        "friend": friend,
        "purchases": purchases,
        "repayments": repayments,
        "compensations": compensations,
        "balance": friend.balance,
        "borrower_balances": {b: friend.balance_for(b) for b in BORROWERS},
        "BORROWERS": BORROWERS,
    })
