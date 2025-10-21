from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db

from app.api.routes import auth, users, roles, settings as settings_router, notifications, dashboard, finance_gl, ar_ap, treasury, payroll

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_STR + "/users", tags=["users"])
app.include_router(roles.router, prefix=settings.API_V1_STR + "/roles", tags=["roles"])
app.include_router(settings_router.router, prefix=settings.API_V1_STR + "/settings", tags=["settings"])
app.include_router(notifications.router, prefix=settings.API_V1_STR + "/notifications", tags=["notifications"])
app.include_router(dashboard.router, prefix=settings.API_V1_STR + "/dashboard", tags=["dashboard"])
app.include_router(finance_gl.router, prefix=settings.API_V1_STR + "/finance", tags=["finance"])
app.include_router(ar_ap.router, prefix=settings.API_V1_STR + "/arap", tags=["arap"])
app.include_router(treasury.router, prefix=settings.API_V1_STR + "/treasury", tags=["treasury"])
app.include_router(payroll.router, prefix=settings.API_V1_STR + "/payroll", tags=["payroll"])
app.include_router(hr.router, prefix=settings.API_V1_STR + "/hr", tags=["hr"])

@app.on_event("startup")
def on_startup():
    # Initialize DB (create tables)
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
