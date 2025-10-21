from app.db.session import engine, SessionLocal
from app.db.base import Base


def init_db() -> None:
    # Import all models so they are registered with Base
    import app.models.user
    import app.models.role
    import app.models.setting
    import app.models.notification
    import app.models.sale
    import app.models.inventory_item
    import app.models.refresh_token
    import app.models.login_attempt
    import app.models.two_fa_code
    import app.models.gl_models
    import app.models.ar_ap

    Base.metadata.create_all(bind=engine)

    # Seed default roles
    db = SessionLocal()
    try:
        from app.services.role_service import ensure_default_roles
        from app.models.role import Role
        ensure_default_roles(db)
        # Create an admin user if none exists
        from app.models.user import User
        admin_role = db.query(Role).filter(Role.name == 'Admin').first()
        if not db.query(User).filter(User.email == 'admin@local').first():
            from app.core.security import get_password_hash
            u = User(email='admin@local', name='Administrator', hashed_password=get_password_hash('admin123'), is_active=True, is_verified=True, role=admin_role)
            db.add(u)
            db.commit()

        # Seed sample sales if none
        from app.models.sale import Sale
        if db.query(Sale).count() == 0:
            sample_sales = [1200,1500,1100,2000,2300,2100,2500,2700,3000,3200,3500,3800]
            for amt in sample_sales:
                s = Sale(amount=amt)
                db.add(s)
            db.commit()

        # Seed sample inventory if none
        from app.models.inventory_item import InventoryItem
        if db.query(InventoryItem).count() == 0:
            items = [
                ('Laptop', 25),
                ('Mouse', 150),
                ('Keyboard', 80),
                ('Monitor', 40)
            ]
            for name, qty in items:
                it = InventoryItem(name=name, quantity=qty)
                db.add(it)
            db.commit()

        # Seed some notifications for admin
        from app.models.notification import Notification
        admin_user = db.query(User).filter(User.email == 'admin@local').first()
        if admin_user and db.query(Notification).count() == 0:
            n1 = Notification(title='Welcome', message='Admin account created', type='info', user_id=admin_user.id)
            n2 = Notification(title='Stock Low', message='Laptop stock below threshold', type='warning', user_id=admin_user.id)
            db.add_all([n1, n2])
            db.commit()

    finally:
        db.close()
