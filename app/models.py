from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


BORROWERS = ["Mehdi", "Faycal"]


class Friend(Base):
    __tablename__ = "friends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="friend", cascade="all, delete-orphan")
    repayments: Mapped[list["Repayment"]] = relationship(back_populates="friend", cascade="all, delete-orphan")
    compensations: Mapped[list["Compensation"]] = relationship(back_populates="friend", cascade="all, delete-orphan")

    def total_purchases_for(self, borrower: str) -> float:
        return sum(p.amount_tnd for p in self.purchases if p.borrower == borrower)

    def total_repayments_for(self, borrower: str) -> float:
        return sum(r.amount_tnd for r in self.repayments if r.borrower == borrower)

    def total_compensations_for(self, borrower: str) -> float:
        return sum(c.amount_tnd for c in self.compensations if c.borrower == borrower)

    def balance_for(self, borrower: str) -> float:
        return self.total_purchases_for(borrower) - self.total_repayments_for(borrower) - self.total_compensations_for(borrower)

    @property
    def total_purchases(self) -> float:
        return sum(p.amount_tnd for p in self.purchases) if self.purchases else 0.0

    @property
    def total_repayments(self) -> float:
        return sum(r.amount_tnd for r in self.repayments) if self.repayments else 0.0

    @property
    def total_compensations(self) -> float:
        return sum(c.amount_tnd for c in self.compensations) if self.compensations else 0.0

    @property
    def balance(self) -> float:
        return self.total_purchases - self.total_repayments - self.total_compensations


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="exchange_rate")


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    friend_id: Mapped[int] = mapped_column(ForeignKey("friends.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate_id: Mapped[int] = mapped_column(ForeignKey("exchange_rates.id"), nullable=False)
    amount_tnd: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    borrower: Mapped[str] = mapped_column(String(20), nullable=False, default="Mehdi")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    friend: Mapped["Friend"] = relationship(back_populates="purchases")
    exchange_rate: Mapped["ExchangeRate"] = relationship(back_populates="purchases")


class Repayment(Base):
    __tablename__ = "repayments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    friend_id: Mapped[int] = mapped_column(ForeignKey("friends.id"), nullable=False)
    amount_tnd: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    borrower: Mapped[str] = mapped_column(String(20), nullable=False, default="Mehdi")
    paid_by: Mapped[str] = mapped_column(String(20), nullable=False, default="Mehdi")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    friend: Mapped["Friend"] = relationship(back_populates="repayments")


class Compensation(Base):
    __tablename__ = "compensations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    friend_id: Mapped[int] = mapped_column(ForeignKey("friends.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount_tnd: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    borrower: Mapped[str] = mapped_column(String(20), nullable=False, default="Mehdi")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    friend: Mapped["Friend"] = relationship(back_populates="compensations")
