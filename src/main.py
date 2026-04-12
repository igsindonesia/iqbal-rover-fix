from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.db import Base, engine, get_db
from src.core.config import settings
from src.core.auth import hash_password
from src.users.routers import router as users_router
from src.posts.routers import router as posts_router
from src.admin.routers import router as admin_router
from src.users.models import User
from src.posts.models import Post
from src.admin.models import Admin


# initial app
app = FastAPI(title="Rover Backend Developer", version="0.0.1")

# initial database
Base.metadata.create_all(bind=engine)


# Seed Superadmin on startup
@app.on_event("startup")
async def seed_superadmin():
    db = next(get_db())
    existing_admin = db.query(Admin).filter(Admin.role == "superadmin").first()

    if not existing_admin:
        superadmin = Admin(
            email=settings.SUPERADMIN_EMAIL,
            username=settings.SUPERADMIN_USERNAME,
            password=hash_password(settings.SUPERADMIN_PASSWORD),
            role="superadmin",
            is_active=True,
        )
        db.add(superadmin)
        db.commit()
        print(f"Superadmin created: {settings.SUPERADMIN_EMAIL}")


# CORS Middleware
origins = [o.strip() for o in settings.CORS_FE_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router Section
app.include_router(users_router)
app.include_router(posts_router)
app.include_router(admin_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok"}
