"""
Database initialization script for Hive platform.
Creates all tables and sets up initial data.
"""

import logging
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.auth import Base as AuthBase, User, API_SCOPES
from app.models.auth import APIKey

# Import other model bases here as they're created
# from app.models.workflows import Base as WorkflowsBase
# from app.models.agents import Base as AgentsBase

def create_tables():
    """Create all database tables."""
    try:
        # Create auth tables
        AuthBase.metadata.create_all(bind=engine)
        
        # Add other model bases here
        # WorkflowsBase.metadata.create_all(bind=engine)
        # AgentsBase.metadata.create_all(bind=engine)
        
        logging.info("Database tables created successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to create database tables: {e}")
        return False


def create_initial_user(db: Session):
    """Create initial admin user if none exists."""
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        if user_count > 0:
            logging.info("Users already exist, skipping initial user creation")
            return True
        
        # Create initial admin user
        admin_user = User(
            username="admin",
            email="admin@hive.local",
            full_name="Hive Administrator",
            hashed_password=User.hash_password("admin123"),  # Change this!
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logging.info("Initial admin user created: admin/admin123")
        logging.warning("SECURITY: Please change the default admin password!")
        
        # Create initial API key for the admin user
        from app.core.security import APIKeyManager
        plain_key, hashed_key, prefix = APIKeyManager.generate_api_key()
        
        admin_api_key = APIKey(
            user_id=admin_user.id,
            name="Default Admin API Key",
            key_hash=hashed_key,
            key_prefix=prefix,
            is_active=True
        )
        admin_api_key.set_scopes(["admin"])
        
        db.add(admin_api_key)
        db.commit()
        
        logging.info(f"Initial admin API key created: {plain_key}")
        logging.warning("SECURITY: Save this API key securely, it won't be shown again!")
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to create initial user: {e}")
        db.rollback()
        return False


def initialize_database():
    """Initialize the complete database."""
    logging.info("Starting database initialization...")
    
    # Create tables
    if not create_tables():
        return False
    
    # Create initial data
    db = SessionLocal()
    try:
        # Create initial admin user
        if not create_initial_user(db):
            return False
        
        logging.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize database
    success = initialize_database()
    if success:
        print("✅ Database initialization completed successfully")
        print("🔑 Default admin credentials: admin/admin123")
        print("⚠️  SECURITY: Please change the default password immediately!")
    else:
        print("❌ Database initialization failed")
        exit(1)