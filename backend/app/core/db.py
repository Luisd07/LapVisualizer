"""Database engine configuration for LapVisualizer."""

from sqlalchemy import create_engine

engine = create_engine("sqlite:///./sql_app.db", echo=True)
