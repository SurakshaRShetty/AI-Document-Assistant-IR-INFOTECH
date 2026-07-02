from dotenv import load_dotenv
load_dotenv()

from app.database import engine, Base
from app.models import *  # noqa: F401,F403 - import all models so create_all sees them
from app.migrations import run_migrations


def create_tables():
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    print("Tables created / migrated successfully")

if __name__ == "__main__":
    create_tables()
