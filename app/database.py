from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Float, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings
connect_args={'check_same_thread':False} if settings.database_url.startswith('sqlite') else {}
engine=create_engine(settings.database_url,connect_args=connect_args)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase): pass
class UserPlan(Base):
    __tablename__='user_plans'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    age: Mapped[int]=mapped_column(Integer)
    weight: Mapped[float]=mapped_column(Float)
    goal: Mapped[str]=mapped_column(String(80))
    intensity: Mapped[str]=mapped_column(String(40))
    plan_json: Mapped[str]=mapped_column(Text)
    nutrition_tip: Mapped[str]=mapped_column(Text)
    feedback: Mapped[str]=mapped_column(Text,default='')
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
def init_db(): Base.metadata.create_all(bind=engine)
