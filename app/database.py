from sqlalchemy import create_engine, text  
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@db/domain_db"

max_retries = 5
retry_count = 0
connected = False

while retry_count < max_retries and not connected:
    try:
        logger.info(f"Attempting to connect to database (attempt {retry_count+1}/{max_retries})")
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,  
            pool_recycle=3600    
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        connected = True
        logger.info("Successfully connected to the database")
    except Exception as e:
        retry_count += 1
        logger.error(f"Database connection failed: {str(e)}")
        if retry_count < max_retries:
            wait_time = 2 ** retry_count  
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            logger.error("Max retries reached. Could not connect to database.")
            raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
