from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from app.models import Compensation, ExchangeRate, Friend, Purchase, Repayment
from app.services.exchange import fetch_rate, get_or_fetch_rate


def test_models_balance_calculation(db):
    friend = Friend(name="Ali")
    db.add(friend)
    db.commit()
    db.refresh(friend)

    rate = ExchangeRate(from_currency="EUR", to_currency="TND", rate=3.3, date=date.today())
    db.add(rate)
    db.commit()

    # Purchase: 100 EUR = 330 TND for Mehdi
    purchase = Purchase(
        friend_id=friend.id,
        description="Hotel",
        amount=100.0,
        currency="EUR",
        exchange_rate_id=rate.id,
        amount_tnd=330.0,
        purchase_date=date.today(),
        borrower="Mehdi",
    )
    # Repayment: 100 TND paid by Mehdi
    repayment = Repayment(
        friend_id=friend.id,
        amount_tnd=100.0,
        date=date.today(),
        borrower="Mehdi",
        paid_by="Mehdi",
    )
    # Compensation: 30 TND by Mehdi
    compensation = Compensation(
        friend_id=friend.id,
        description="Reparation",
        amount_tnd=30.0,
        date=date.today(),
        borrower="Mehdi",
    )
    db.add_all([purchase, repayment, compensation])
    db.commit()
    db.refresh(friend)

    assert friend.total_purchases == 330.0
    assert friend.total_repayments == 100.0
    assert friend.total_compensations == 30.0
    assert friend.balance == 200.0
    assert friend.balance_for("Mehdi") == 200.0
    assert friend.balance_for("Faycal") == 0.0


def test_friends_routes(client, db):
    # GET dashboard
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Dette" in resp.text

    # GET friends list
    resp = client.get("/friends")
    assert resp.status_code == 200

    # POST create friend
    resp = client.post("/friends", data={"name": "Sami"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Sami" in resp.text

    # Duplicate friend creation fails
    resp = client.post("/friends", data={"name": "Sami"})
    assert resp.status_code == 400

    # GET friend detail
    friend = db.query(Friend).filter_by(name="Sami").first()
    resp = client.get(f"/friends/{friend.id}")
    assert resp.status_code == 200
    assert "Sami" in resp.text

    # Edit friend name
    resp = client.post(f"/friends/{friend.id}/edit", data={"name": "Samir"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Samir" in resp.text

    # Delete friend
    resp = client.post(f"/friends/{friend.id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert db.get(Friend, friend.id) is None


def test_transactions_crud(client, db):
    friend = Friend(name="Karim")
    db.add(friend)
    db.commit()

    # Add Purchase with manual rate
    resp = client.post(
        f"/friends/{friend.id}/purchases",
        data={
            "description": "Billets avion",
            "amount": "100",
            "currency": "EUR",
            "purchase_date": date.today().isoformat(),
            "borrower": "Mehdi",
            "manual_rate": "3.4",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    purchase = db.query(Purchase).filter_by(friend_id=friend.id).first()
    assert purchase is not None
    assert purchase.amount_tnd == 340.0

    # Edit Purchase
    resp = client.post(
        f"/friends/{friend.id}/purchases/{purchase.id}/edit",
        data={
            "description": "Billets avion mis a jour",
            "amount": "150",
            "currency": "EUR",
            "purchase_date": date.today().isoformat(),
            "borrower": "Mehdi",
            "manual_rate": "3.4",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    db.refresh(purchase)
    assert purchase.description == "Billets avion mis a jour"
    assert purchase.amount_tnd == 510.0

    # Add Repayment
    resp = client.post(
        f"/friends/{friend.id}/repayments",
        data={
            "amount_tnd": "100",
            "currency": "TND",
            "repayment_date": date.today().isoformat(),
            "paid_by": "Mehdi",
            "borrower": "Mehdi",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    repayment = db.query(Repayment).filter_by(friend_id=friend.id).first()
    assert repayment is not None
    assert repayment.amount_tnd == 100.0

    # Add Compensation
    resp = client.post(
        f"/friends/{friend.id}/compensations",
        data={
            "description": "Reparation PC",
            "amount_tnd": "50",
            "compensation_date": date.today().isoformat(),
            "borrower": "Mehdi",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    compensation = db.query(Compensation).filter_by(friend_id=friend.id).first()
    assert compensation is not None
    assert compensation.amount_tnd == 50.0

    # Check overall friend balance: 510 - 100 - 50 = 360
    db.refresh(friend)
    assert friend.balance == 360.0

    # Delete transactions
    client.post(f"/friends/{friend.id}/purchases/{purchase.id}/delete")
    client.post(f"/friends/{friend.id}/repayments/{repayment.id}/delete")
    client.post(f"/friends/{friend.id}/compensations/{compensation.id}/delete")

    db.refresh(friend)
    assert friend.balance == 0.0


@pytest.mark.anyio
async def test_exchange_rate_service_fallback(db):
    # Same currency returns 1.0
    rate = await get_or_fetch_rate("TND", "TND", date.today(), db)
    assert rate == 1.0

    # Add existing rate in DB
    past_date = date(2025, 1, 1)
    db_rate = ExchangeRate(from_currency="USD", to_currency="TND", rate=3.1, date=past_date)
    db.add(db_rate)
    db.commit()

    # Cached rate lookup
    rate = await get_or_fetch_rate("USD", "TND", past_date, db)
    assert rate == 3.1

    # When external fetch fails, fallback to DB rate
    with patch("app.services.exchange.fetch_rate", new=AsyncMock(return_value=None)):
        fallback_rate = await get_or_fetch_rate("USD", "TND", date(2025, 2, 1), db)
        assert fallback_rate == 3.1
