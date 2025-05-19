from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from database.models import Base  # Import Base


def get_database_url():
    """Constructs the database URL from configuration."""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def create_database():
    """Creates the PostgreSQL database and tables."""
    engine = create_engine(get_database_url())
    # Drop all tables and recreate.  Useful for development, REMOVE for production
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database and tables created.")
    return engine


def get_db_session():
    """Returns a sessionmaker instance."""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    create_database()
