from app.database import engine

def test_db():
    with engine.connect() as conn:
        print("✅ Database connected successfully")

if __name__ == "__main__":
    test_db()
