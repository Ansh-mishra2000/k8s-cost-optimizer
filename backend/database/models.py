from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime
)

from sqlalchemy.orm import declarative_base

from datetime import datetime

Base = declarative_base()


class Recommendation(Base):

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    deployment_name = Column(String)

    namespace = Column(String)

    actual_cpu = Column(Float)

    avg_cpu_24h = Column(Float)

    peak_cpu_24h = Column(Float)

    recommended_cpu = Column(Float)

    requested_cpu = Column(Float)

    actual_memory_mib = Column(Float)

    recommended_memory_mib = Column(Float)

    requested_memory_mib = Column(Float)

    instance_type = Column(String)

    monthly_total_cost_usd = Column(Float)

    optimized_monthly_total_cost_usd = Column(Float)

    monthly_total_savings_usd = Column(Float)