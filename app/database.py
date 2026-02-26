from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQL_Light_URL="""////sqlite:/Users/oussa/Desktop/Github_perso/FastAPI_medical_RAG/app"""

engine=create_engine(SQL_Light_URL, 
                     connect_args={"autocommit": False}) # important car FastAPI est multi-threadé

LocalSession=sessionmaker( 
    autoflush=False,     # désactive les écritures automatiques 
    autocommit=False ,   # pour contrôler les transactions manuellement avec db.commit()
    bind=engine
)

class Base(DeclarativeBase): # nouvelle norme SQLAlchemy 2.0
    """Classe mère de tous les modèles SQLAlchemy."""
    pass

