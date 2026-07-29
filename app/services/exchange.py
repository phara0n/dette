from datetime import date

import httpx

FRANKFURTER_URL = "https://api.frankfurter.dev/v2"


async def fetch_rate(from_currency: str, to_currency: str, rate_date: date | None = None) -> float | None:
    if from_currency == to_currency:
        return 1.0
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {}
            if rate_date:
                params["date"] = rate_date.isoformat()
            resp = await client.get(
                f"{FRANKFURTER_URL}/rate/{from_currency}/{to_currency}",
                params=params,
            )

            if resp.status_code == 200:
                data = resp.json()
                return data["rate"]
    except Exception:
        pass
    return None


async def get_or_fetch_rate(from_currency: str, to_currency: str, rate_date: date, db) -> float | None:
    if from_currency == to_currency:
        return 1.0

    from ..models import ExchangeRate

    existing = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == from_currency,
        ExchangeRate.to_currency == to_currency,
        ExchangeRate.date == rate_date,
    ).first()

    if existing:
        return existing.rate

    rate = await fetch_rate(from_currency, to_currency, rate_date)
    if rate is None:
        return None

    db_rate = ExchangeRate(from_currency=from_currency, to_currency=to_currency, rate=rate, date=rate_date)
    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)
    return db_rate.rate
