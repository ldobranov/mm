from .db.session import engine
from .db.base import Base
from .db import models
from .db.session import SessionLocal
from .core.security import get_password_hash

def create_tables():
    # Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if admin_user:
        if admin_user.role != "admin":
            admin_user.role = "admin"
            db.commit()
            print("Admin user role updated to 'admin'.")
    else:
        admin_user = models.User(
            username="admin",
            email="admin@admin.com",
            hashed_password=get_password_hash("admin"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created.")
    db.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created.")
