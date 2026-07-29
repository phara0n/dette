from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./data/dette.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(repayments);")).fetchall()
        col_names = [row[1] for row in result]
        if "amount" not in col_names:
            conn.execute(text("ALTER TABLE repayments ADD COLUMN amount FLOAT NULL;"))
        if "currency" not in col_names:
            conn.execute(text("ALTER TABLE repayments ADD COLUMN currency VARCHAR(3) NULL;"))
        if "exchange_rate_id" not in col_names:
            conn.execute(text("ALTER TABLE repayments ADD COLUMN exchange_rate_id INTEGER NULL REFERENCES exchange_rates(id);"))
        conn.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

