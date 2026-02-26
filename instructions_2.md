# 🧠 MedMind — Projet Portfolio AI Engineer
> FastAPI · Pydantic v2 · SQLAlchemy 2.0 · OpenAI · RAG · SSE · JWT · uv

---

## 📋 Matière de tes notes couverte par ce projet

| Thème | Concepts couverts |
|---|---|
| **Python OOP** | Classes, héritage, `@classmethod`, `@staticmethod`, `@property` |
| **Python avancé** | `TypeAlias`, `ClassVar`, `StrEnum` + `auto()`, `*` keyword-only args |
| **FastAPI** | Routers, Path/Query params, CRUD complet, `UploadFile`, `BackgroundTasks`, SSE, `HTTPException`, status codes |
| **Pydantic v2** | `BaseModel`, `Field`, `@field_validator`, `@model_validator`, `ConfigDict`, `@computed_field`, `model_dump`, `from_attributes` |
| **SQLAlchemy 2.0** | Models, FK, `back_populates`, `joinedload`, DI session, `select()`, `scalar_one_or_none()` |
| **Alembic** | `init`, `autogenerate`, `upgrade head` |
| **Auth** | Argon2, JWT (PyJWT), `OAuth2PasswordBearer` |
| **LLM/GenAI** | `AsyncOpenAI`, streaming SSE, RAG pipeline, Structured Outputs, embeddings, historique de conversation |
| **Rate limiting** | slowapi |
| **DevOps** | `uv` |

---

## 💡 Trois idées de projet — Domaine médical

### Idée 1 — MedChat 🩺
**Assistant conversationnel symptômes**
Un chatbot médical multi-tours avec historique, auth utilisateur, streaming SSE. L'utilisateur décrit ses symptômes, l'IA répond en streaming avec un disclaimer médical. Trop simple : pas de RAG, pas d'ingestion de documents.

### Idée 2 — MedReport Analyzer 📄
**Analyse de comptes-rendus médicaux**
Upload de PDFs (ordonnances, analyses de sang), extraction d'entités structurées (Pydantic + Structured Outputs), résumé. Couvre bien la partie LLM mais manque la gestion des sessions utilisateurs et le RAG complet.

### Idée 3 — MedMind RAG API 🧬 ← **PROJET CHOISI**
**Plateforme RAG médicale complète**
API permettant à des professionnels de santé d'ingérer des documents médicaux (recommandations HAS, protocoles, guides cliniques), de les interroger en langage naturel avec streaming SSE, d'extraire des entités médicales structurées, et de gérer des consultations persistées en base. Couvre **la quasi-totalité** des concepts de tes notes.

---

## 🎯 Pourquoi MedMind ?

C'est le projet qui coche le plus de cases :
- **RAG** : ingestion → embedding → retrieval → generation
- **Streaming SSE** : réponse token par token comme ChatGPT
- **Auth complète** : inscription, login, JWT
- **SQLAlchemy** avec relations réelles : `User → Document` et `User → Consultation → Message`
- **BackgroundTasks** : embeddings générés après la réponse HTTP (le client n'attend pas)
- **Structured Outputs** : extraction d'entités médicales en JSON typé et validé par Pydantic
- **UploadFile** : ingestion de PDF et TXT

---

# 🏗️ Architecture & Structure du projet

```
medmind-api/
├── pyproject.toml              ← uv : dépendances & metadata
├── .env                        ← variables d'environnement (jamais committé)
├── .env.example                ← template public
│
├── app/
│   ├── __init__.py
│   ├── main.py                 ← Point d'entrée, lifespan, include_router
│   ├── config.py               ← Settings Pydantic (lit le .env)
│   ├── database.py             ← Engine SQLAlchemy, SessionLocal, Base
│   ├── dependencies.py         ← get_db, get_current_user (DI)
│   │
│   ├── models/                 ← Tables SQLAlchemy (= structure DB)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── consultation.py
│   │
│   ├── schemas/                ← Modèles Pydantic (= validation JSON)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── consultation.py
│   │
│   ├── routers/                ← Endpoints FastAPI
│   │   ├── __init__.py
│   │   ├── auth.py             ← POST /auth/register, POST /auth/token
│   │   ├── documents.py        ← POST /documents/upload, GET, DELETE
│   │   └── chat.py             ← POST /chat/query, /chat/stream, /chat/extract
│   │
│   └── services/               ← Logique métier (jamais d'HTTP ici)
│       ├── __init__.py
│       ├── auth_service.py     ← Argon2, création/décodage JWT
│       ├── rag_service.py      ← ChromaDB, embeddings, pipeline RAG
│       └── llm_service.py      ← Wrapper AsyncOpenAI (chat, stream, extract)
│
└── alembic/
    ├── env.py
    └── versions/
```

---

## 🔄 Relations entre les tables

```
User (1) ──────────< Document (N)       Un user possède plusieurs documents
User (1) ──────────< Consultation (N)   Un user a plusieurs consultations
Consultation (1) ──< Message (N)        Une consultation contient plusieurs messages
```

---

## 🗺️ Flux global de l'application

```
[Client]
   │
   ├─ POST /auth/register     → créer un compte (hash Argon2)
   ├─ POST /auth/token        → login → retourne un JWT
   │
   ├─ POST /documents/upload  → UploadFile → extraction texte → sauvegarde DB
   │                            └── BackgroundTask → embedding → ChromaDB (status: INDEXED)
   ├─ GET  /documents/        → lister ses documents + status
   ├─ DELETE /documents/{id}  → supprimer de DB + de ChromaDB
   │
   ├─ POST /chat/query        → RAG complet → réponse JSON
   ├─ POST /chat/stream       → RAG complet → réponse SSE token par token
   ├─ POST /chat/extract      → Structured Output → entités médicales en JSON
   └─ GET  /chat/consultations→ historique avec messages (joinedload)
```

---

# 📖 Guide Étape par Étape

> **Convention utilisée dans chaque section :**
> - 📌 **Consigne** : ce que tu dois implémenter
> - 💡 **Indices** : des pistes concrètes pour y arriver
> - ✅ **Solution** : le code complet à consulter après avoir essayé

---

## PHASE 0 — Setup du projet avec uv

### Pourquoi on commence ici ?
Avant d'écrire une ligne de code, il faut une base solide : structure de dossiers claire, dépendances déclarées et reproductibles. `uv` remplace `pip + venv` en une seule commande et est significativement plus rapide.

---

### 📌 Consigne — `pyproject.toml` + structure

1. Installe uv si ce n'est pas fait : `curl -Lsf https://astral.sh/uv/install.sh | sh`
2. Crée le projet : `uv init medmind-api && cd medmind-api`
3. Crée manuellement toute l'arborescence décrite dans la section **Architecture** ci-dessus (tous les dossiers + les fichiers `__init__.py` vides)
4. Remplis le `pyproject.toml` avec les dépendances suivantes, puis lance `uv sync` :
   - **API** : `fastapi[standard]`, `python-multipart`
   - **DB** : `sqlalchemy`, `alembic`
   - **Config** : `pydantic-settings`
   - **Auth** : `argon2-cffi`, `PyJWT`
   - **LLM** : `openai`
   - **Vector DB** : `chromadb`
   - **PDF** : `pypdf`
   - **Rate limiting** : `slowapi`
   - **Dev** : `pytest`, `pytest-asyncio`, `httpx` (en dépendances optionnelles)
5. Crée le fichier `.env` à la racine en t'appuyant sur le `.env.example` de la solution ci-dessous, puis renseigne ta clé OpenAI et une `SECRET_KEY` aléatoire

💡 **Indices :**
- `uv add fastapi[standard]` ajoute une dépendance et met à jour `pyproject.toml` automatiquement
- `uv add --dev pytest pytest-asyncio httpx` pour les dépendances de test
- `uv sync` installe tout ce qui est déclaré dans `pyproject.toml`
- `uv run uvicorn app.main:app --reload` lance le serveur sans activer de venv manuellement
- Le fichier `.env` ne doit jamais être committé — ajoute-le à ton `.gitignore`

---

### ✅ Solution — `pyproject.toml`

```toml
[project]
name = "medmind-api"
version = "0.1.0"
description = "Medical RAG API — Portfolio project"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.115.0",
    "python-multipart>=0.0.9",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "pydantic-settings>=2.0.0",
    "argon2-cffi>=23.1.0",
    "PyJWT>=2.8.0",
    "openai>=1.30.0",
    "chromadb>=0.5.0",
    "pypdf>=4.0.0",
    "slowapi>=0.1.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

### ✅ Solution — `.env.example`

```env
# OpenAI
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Auth
SECRET_KEY=change_me_with_a_long_random_string_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de données
DATABASE_URL=sqlite:///./medmind.db
```

---

## PHASE 1 — Configuration & Base de données

### Pourquoi avant les routes ?
La config et la base de données sont la fondation de tout. Tous les autres modules (services, routers, dépendances) en dépendent. On construit toujours de bas en haut.

---

### 📌 Consigne — `app/config.py`

Crée une classe `Settings` qui lit automatiquement les variables depuis le fichier `.env`.

💡 **Indices :**
- Hérite de `pydantic_settings.BaseSettings` (pas de `pydantic.BaseModel`)
- `model_config = SettingsConfigDict(env_file=".env")` pour pointer vers le fichier
- Les noms des champs doivent correspondre exactement aux clés du `.env` (en minuscules)
- Les champs sans valeur par défaut (`openai_api_key`, `secret_key`) sont obligatoires : Pydantic lèvera une erreur au démarrage s'ils manquent dans le `.env`
- Crée une instance singleton `settings = Settings()` en bas du fichier pour l'importer partout

---

### ✅ Solution — `app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # OpenAI — champs obligatoires (pas de valeur par défaut)
    openai_api_key: str
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Auth
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # DB
    database_url: str = "sqlite:///./medmind.db"


# Instance unique importée dans toute l'application
settings = Settings()
```

---

### 📌 Consigne — `app/database.py`

Crée le moteur SQLAlchemy 2.0, la `SessionLocal` (fabrique de sessions), et la classe `Base` dont hériteront tous tes modèles.

💡 **Indices :**
- Pour SQLite uniquement, ajouter `connect_args={"check_same_thread": False}` (FastAPI est multi-threadé)
- `sessionmaker(autocommit=False, autoflush=False, bind=engine)` : désactive les écritures automatiques pour contrôler les transactions manuellement avec `db.commit()`
- En SQLAlchemy 2.0, `Base` s'écrit avec `DeclarativeBase` (et non l'ancienne `declarative_base()`)
- Importe `settings` depuis `app.config` pour lire l'URL de la base

---

### ✅ Solution — `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# SQLite nécessite check_same_thread=False car FastAPI est multi-threadé
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

# SessionLocal est une fabrique : chaque appel à SessionLocal() crée une nouvelle session isolée
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe mère de tous les modèles SQLAlchemy."""
    pass
```

---

## PHASE 2 — Modèles SQLAlchemy (Tables)

### Pourquoi maintenant ?
Les modèles définissent la structure physique de ta base de données. Alembic en a besoin pour générer les migrations, et les services en ont besoin pour manipuler les données. Ils viennent donc avant tout le reste.

---

### 📌 Consigne — `app/models/user.py`

Crée le modèle `User` avec les colonnes : `id`, `email` (unique), `username` (unique), `hashed_password`, `is_active`, `created_at`. Ajoute les relations vers `Document` et `Consultation`.

💡 **Indices :**
- Hérite de `Base` importé depuis `app.database`
- `__tablename__ = "users"` définit le nom exact de la table SQL
- `Column(Integer, primary_key=True, index=True)` pour l'id
- `relationship("Document", back_populates="owner")` crée le lien logique bidirectionnel côté Python (pas de colonne SQL créée)
- `cascade="all, delete-orphan"` : quand on supprime un user, ses documents et consultations sont supprimés automatiquement
- Utilise `datetime.now(timezone.utc)` et non `datetime.utcnow()` (déprécié en Python 3.12)

---

### ✅ Solution — `app/models/user.py`

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Un user possède plusieurs documents et plusieurs consultations
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    consultations = relationship("Consultation", back_populates="user", cascade="all, delete-orphan")
```

---

### 📌 Consigne — `app/models/document.py`

Crée le modèle `Document`. Colonnes : `id`, `filename`, `content` (texte extrait), `status` (chaîne : PENDING / INDEXED / FAILED), `owner_id` (FK vers `users.id`), `created_at`.

💡 **Indices :**
- `status` est stocké comme une `String` simple en base — le `StrEnum` sera dans les schemas, pas ici
- `ForeignKey("users.id")` crée le lien physique en base (contrainte d'intégrité référentielle)
- `relationship("User", back_populates="documents")` crée le lien logique côté Python

---

### ✅ Solution — `app/models/document.py`

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)         # Texte brut extrait du fichier uploadé
    status = Column(String, default="PENDING")     # PENDING | INDEXED | FAILED
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="documents")
```

---

### 📌 Consigne — `app/models/consultation.py`

Crée deux modèles dans le même fichier : `Consultation` (une session de chat) et `Message` (un échange dans une session). Une consultation appartient à un `User` et contient plusieurs `Message`.

💡 **Indices :**
- `Consultation` : `id`, `title`, `user_id` (FK vers `users.id`), `created_at` + relation vers `Message`
- `Message` : `id`, `role` (string : "user" ou "assistant"), `content`, `consultation_id` (FK vers `consultations.id`), `created_at`
- N'oublie pas `cascade="all, delete-orphan"` sur la relation `Consultation → Message`

---

### ✅ Solution — `app/models/consultation.py`

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Nouvelle consultation")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="consultations")
    messages = relationship("Message", back_populates="consultation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)    # "user" | "assistant"
    content = Column(Text, nullable=False)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    consultation = relationship("Consultation", back_populates="messages")
```

---

### 📌 Consigne — Alembic (migrations)

Initialise Alembic, configure `env.py` pour qu'il connaisse tes modèles et ta base, puis génère et applique la première migration.

💡 **Indices :**
- `uv run alembic init alembic` génère le dossier `alembic/` et le fichier `alembic.ini`
- Dans `alembic/env.py` : ajouter le dossier racine au `sys.path`, importer `Base` **et tous les modèles** (sinon Alembic ne les voit pas), définir `target_metadata = Base.metadata`
- Lire l'URL DB depuis `settings.database_url` plutôt que de la coder en dur dans `alembic.ini`
- `uv run alembic revision --autogenerate -m "init"` : compare tes modèles Python avec la DB et génère un script de migration dans `alembic/versions/`
- `uv run alembic upgrade head` : applique toutes les migrations en attente

---

### ✅ Solution — `alembic/env.py` (parties à modifier)

```python
# Ajouter ces lignes au tout début du fichier, avant les imports alembic
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.config import settings
# CRUCIAL : importer tous les modèles pour qu'Alembic puisse les détecter
from app.models import user, document, consultation  # noqa: F401

# Remplacer la ligne : target_metadata = None
# Par :
target_metadata = Base.metadata

# Dans la fonction run_migrations_online(), remplacer la récupération de l'URL par :
config.set_main_option("sqlalchemy.url", settings.database_url)
```

---

## PHASE 3 — Schémas Pydantic (Validation)

### Pourquoi maintenant ?
Les schémas font le pont entre le monde HTTP (JSON brut) et le monde Python typé. Ils valident ce qui entre dans l'API et formatent ce qui en sort. Ils dépendent des modèles SQLAlchemy (via `from_attributes=True`), donc ils viennent après.

---

### 📌 Consigne — `app/schemas/user.py`

Crée trois schémas : `UserCreate` (inscription), `UserResponse` (réponse sans mot de passe), `Token` (réponse JWT).

💡 **Indices :**
- `UserCreate` : valide que le password fait au moins 8 caractères avec `Field(min_length=8)`, et l'email avec un `@field_validator`
- `UserResponse` : doit avoir `model_config = ConfigDict(from_attributes=True)` pour que Pydantic sache lire un objet ORM SQLAlchemy
- `Token` : deux champs simples — `access_token: str` et `token_type: str = "bearer"`
- Le `@field_validator` est un `@classmethod` en Pydantic v2 : n'oublie pas le décorateur

---

### ✅ Solution — `app/schemas/user.py`

```python
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class UserCreate(BaseModel):
    email: str = Field(description="Adresse email unique")
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Email invalide")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Username : lettres, chiffres et _ uniquement")
        return v.lower()


class UserResponse(BaseModel):
    # from_attributes=True permet à Pydantic de lire les attributs d'un objet ORM SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

---

### 📌 Consigne — `app/schemas/document.py`

Crée un `StrEnum` pour le status du document, le schéma `DocumentResponse` avec un champ calculé, et `ExtractedMedicalEntities` (structure pour les Structured Outputs du LLM).

💡 **Indices :**
- `class DocumentStatus(StrEnum): PENDING = auto()` etc. — `auto()` utilise le nom de la variable comme valeur string
- `DocumentResponse` avec un `@computed_field` qui calcule `is_ready: bool` à partir du `status` — retourne `True` si `status == DocumentStatus.INDEXED`
- `ExtractedMedicalEntities` : des listes de strings pour `symptoms`, `medications`, `diagnoses`, `recommendations`, plus un `urgency_level`
- `@computed_field` nécessite aussi `@property` juste en dessous

---

### ✅ Solution — `app/schemas/document.py`

```python
from datetime import datetime
from enum import StrEnum, auto
from typing import List
from pydantic import BaseModel, ConfigDict, computed_field


class DocumentStatus(StrEnum):
    PENDING = auto()    # Document reçu, en attente d'indexation
    INDEXED = auto()    # Indexé dans ChromaDB, prêt pour le RAG
    FAILED = auto()     # Échec lors de l'indexation


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: str
    owner_id: int
    created_at: datetime

    @computed_field
    @property
    def is_ready(self) -> bool:
        """Champ calculé : indique si le document peut être interrogé."""
        return self.status == DocumentStatus.INDEXED


class ExtractedMedicalEntities(BaseModel):
    """
    Schéma de validation pour les Structured Outputs du LLM.
    Le LLM est contraint à retourner un JSON qui respecte exactement cette structure.
    """
    symptoms: List[str] = []
    medications: List[str] = []
    diagnoses: List[str] = []
    recommendations: List[str] = []
    urgency_level: str = "non déterminé"    # faible | modéré | élevé | critique
```

---

### 📌 Consigne — `app/schemas/consultation.py`

Crée les schémas : `MessageSchema`, `ConsultationResponse`, et `ChatRequest` (le corps de la requête de chat).

💡 **Indices :**
- `MessageSchema` : `id`, `role` avec `Literal["user", "assistant"]`, `content`, `created_at` + `from_attributes=True`
- `ConsultationResponse` : inclut `messages: List[MessageSchema] = []` (la relation chargée par joinedload)
- `ChatRequest` : `message: str`, `consultation_id: Optional[int] = None`, `top_k: int = Field(default=3, ge=1, le=10)`
- Ajoute un `@model_validator(mode="after")` sur `ChatRequest` pour vérifier que le message n'est pas blanc après `strip()` — exemple concret de validation croisée multi-champs

---

### ✅ Solution — `app/schemas/consultation.py`

```python
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    user_id: int
    created_at: datetime
    messages: List[MessageSchema] = []


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    consultation_id: Optional[int] = None
    top_k: int = Field(default=3, ge=1, le=10, description="Nombre de chunks RAG à récupérer")

    @model_validator(mode="after")
    def message_not_blank(self) -> "ChatRequest":
        """
        Validation croisée (mode='after') : s'exécute APRÈS que chaque champ
        a été validé individuellement. Ici on nettoie et on vérifie le message.
        """
        if not self.message.strip():
            raise ValueError("Le message ne peut pas être vide ou contenir uniquement des espaces")
        self.message = self.message.strip()
        return self
```

---

## PHASE 4 — Services (Logique métier)

### Pourquoi une couche services ?
Les routers doivent rester légers : recevoir une requête, déléguer le travail, renvoyer une réponse. La logique complexe (appels LLM, embeddings, hachage, RAG) va dans les services. C'est le principe **Single Responsibility** : chaque module a une seule raison de changer.

---

### 📌 Consigne — `app/services/auth_service.py`

Implémente quatre fonctions : `hash_password`, `verify_password`, `create_access_token`, `decode_access_token`.

💡 **Indices :**
- `from argon2 import PasswordHasher` → instancie `ph = PasswordHasher()` au niveau module (singleton)
- `ph.hash(password)` → retourne le hash ; `ph.verify(hashed, plain)` → retourne `True` ou lève `VerifyMismatchError`
- Pour JWT : `import jwt` (PyJWT) → `jwt.encode(payload, key, algorithm)` et `jwt.decode(token, key, algorithms=[...])`
- Le payload JWT doit contenir `"sub"` (username) et `"exp"` (expiration) : `datetime.now(timezone.utc) + timedelta(minutes=...)`

---

### ✅ Solution — `app/services/auth_service.py`

```python
from datetime import datetime, timezone, timedelta
from typing import Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.config import settings

# Singleton : une seule instance partagée pour tout le service
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hache le mot de passe avec Argon2 (algorithme recommandé en 2024-2025)."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe contre son hash Argon2.
    Retourne False si invalide, au lieu de propager l'exception.
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée et signe un JWT contenant les données fournies + une expiration."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """
    Décode et valide un JWT.
    Lève jwt.ExpiredSignatureError si expiré, jwt.InvalidTokenError si invalide.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
```

---

### 📌 Consigne — `app/services/llm_service.py`

Crée le wrapper autour du client `AsyncOpenAI`. Implémente : `chat_complete`, `chat_stream` (générateur async SSE), `extract_structured` (JSON mode), et `get_embedding`.

💡 **Indices :**
- `AsyncOpenAI(api_key=settings.openai_api_key)` — le client est instancié **une seule fois** au niveau module (singleton)
- `chat_stream` doit être une `async def` qui `yield` des chaînes au format SSE : `f"data: {json.dumps({'token': delta})}\n\n"`
- N'oublie pas `yield "data: [DONE]\n\n"` à la fin du stream pour signaler la fin au client
- Pour `extract_structured` : utilise `response_format={"type": "json_object"}` + `json.loads()` sur la réponse — le schéma attendu est décrit dans le system prompt

---

### ✅ Solution — `app/services/llm_service.py`

```python
import json
from typing import AsyncGenerator, List
from openai import AsyncOpenAI
from app.config import settings

# Client unique réutilisé par tous les appels (pattern Singleton)
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def chat_complete(messages: List[dict]) -> str:
    """Appel LLM standard — attend la réponse complète avant de la retourner."""
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
    )
    return response.choices[0].message.content


async def chat_stream(messages: List[dict]) -> AsyncGenerator[str, None]:
    """
    Générateur async qui yield les tokens un par un au format SSE.
    Chaque chunk : 'data: {"token": "..."}\n\n'
    Signal de fin : 'data: [DONE]\n\n'
    """
    stream = await client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield f"data: {json.dumps({'token': delta})}\n\n"

    yield "data: [DONE]\n\n"


async def extract_structured(text: str, schema_description: str) -> dict:
    """
    Force le LLM à répondre uniquement avec un JSON valide.
    response_format={"type": "json_object"} garantit un JSON parseable.
    Le schéma attendu est décrit dans le system prompt.
    """
    system_prompt = (
        "Tu es un assistant médical expert en extraction d'information clinique. "
        "Analyse le texte fourni et réponds UNIQUEMENT avec un objet JSON valide "
        "respectant exactement ce format :\n"
        f"{schema_description}\n"
        "Ne réponds rien d'autre que le JSON. Pas d'explication, pas de markdown."
    )
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


async def get_embedding(text: str) -> List[float]:
    """Génère un vecteur d'embedding pour un texte donné."""
    response = await client.embeddings.create(
        input=text,
        model=settings.embedding_model,
    )
    return response.data[0].embedding
```

---

### 📌 Consigne — `app/services/rag_service.py`

Le cœur du projet. Implémente :
- `index_document(doc_id, content, filename)` → découpe en chunks → embedding → stockage ChromaDB
- `search_similar(query, top_k)` → embed la question → recherche dans ChromaDB
- `rag_pipeline(question, top_k)` → search → construction du prompt avec contexte → `chat_complete`
- `delete_document_vectors(doc_id)` → supprime tous les vecteurs d'un document

💡 **Indices :**
- `chromadb.PersistentClient(path="./chroma_db")` → la DB vectorielle survit aux redémarrages
- `client.get_or_create_collection("medmind_docs", metadata={"hnsw:space": "cosine"})` → similarité cosinus, meilleure pour le texte
- Pour le chunking : découpe le texte en morceaux de ~500 mots avec un overlap de 50 mots. L'overlap évite de couper une information en plein milieu : les 50 derniers mots d'un chunk réapparaissent au début du suivant
- `collection.add(documents=[chunk], embeddings=[embedding], ids=[f"doc_{doc_id}_chunk_{i}"], metadatas=[{...}])`
- `collection.query(query_embeddings=[q_emb], n_results=top_k)` pour la recherche
- Pour supprimer : `collection.get(where={"doc_id": doc_id})` puis `collection.delete(ids=[...])`
- Protège contre l'erreur si la collection est vide (`collection.count() == 0`)

---

### ✅ Solution — `app/services/rag_service.py`

```python
import chromadb
from typing import List, Tuple
from app.services.llm_service import get_embedding, chat_complete

# Client ChromaDB persistant — les données restent entre les redémarrages
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="medmind_docs",
    metadata={"hnsw:space": "cosine"},
)

SYSTEM_DISCLAIMER = (
    "Tu es MedMind, un assistant médical de référence.\n"
    "Réponds uniquement en te basant sur les documents fournis dans le contexte.\n"
    "⚠️ Ces informations sont à titre éducatif uniquement et ne remplacent "
    "pas l'avis d'un professionnel de santé qualifié."
)


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Découpe un texte en chunks de 'chunk_size' mots avec un overlap.
    L'overlap évite de couper une information en plein milieu entre deux chunks :
    les 'overlap' derniers mots d'un chunk réapparaissent au début du suivant.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


async def index_document(doc_id: int, content: str, filename: str) -> int:
    """
    Indexe un document dans ChromaDB :
    1. Découpe le texte en chunks
    2. Génère un embedding pour chaque chunk via l'API OpenAI
    3. Stocke les chunks + embeddings + métadonnées dans la collection
    Retourne le nombre de chunks créés.
    """
    chunks = _chunk_text(content)
    for i, chunk in enumerate(chunks):
        embedding = await get_embedding(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[f"doc_{doc_id}_chunk_{i}"],
            metadatas=[{"doc_id": doc_id, "filename": filename, "chunk_index": i}],
        )
    return len(chunks)


async def search_similar(query: str, top_k: int = 3) -> List[Tuple[str, dict]]:
    """
    Recherche les chunks les plus proches sémantiquement de la question.
    Retourne une liste de tuples (texte_du_chunk, métadonnées).
    """
    if collection.count() == 0:
        return []

    q_embedding = await get_embedding(query)
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=min(top_k, collection.count()),
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    return list(zip(results["documents"][0], results["metadatas"][0]))


async def rag_pipeline(question: str, top_k: int = 3) -> dict:
    """
    Pipeline RAG complet :
    1. Embed la question
    2. Récupère les chunks les plus pertinents
    3. Construit le prompt avec le contexte trouvé
    4. Appelle le LLM
    5. Retourne la réponse + la liste des sources utilisées
    """
    similar_chunks = await search_similar(question, top_k)

    if not similar_chunks:
        context = "Aucun document pertinent trouvé dans la base de connaissances."
        sources = []
    else:
        context = "\n\n---\n\n".join(chunk for chunk, _ in similar_chunks)
        sources = list({meta["filename"] for _, meta in similar_chunks})

    messages = [
        {"role": "system", "content": f"{SYSTEM_DISCLAIMER}\n\nCONTEXTE :\n{context}"},
        {"role": "user", "content": question},
    ]

    answer = await chat_complete(messages)
    return {"answer": answer, "sources": sources, "chunks_used": len(similar_chunks)}


def delete_document_vectors(doc_id: int) -> None:
    """Supprime tous les vecteurs associés à un document dans ChromaDB."""
    result = collection.get(where={"doc_id": doc_id})
    if result["ids"]:
        collection.delete(ids=result["ids"])
```

---

## PHASE 5 — Dépendances FastAPI

### Pourquoi une couche de dépendances ?
Sans ce pattern, chaque endpoint devrait ouvrir et fermer manuellement sa session DB et vérifier le JWT lui-même. Avec la **Dependency Injection** de FastAPI, on déclare la dépendance une seule fois et FastAPI l'injecte automatiquement — et la nettoie après usage grâce à `yield`.

---

### 📌 Consigne — `app/dependencies.py`

Implémente `get_db()` (générateur de session DB) et `get_current_user()` (extrait et valide le JWT, retourne l'utilisateur). Crée aussi les alias typés `DbDependency` et `CurrentUser`.

💡 **Indices :**
- `get_db` : `db = SessionLocal()` → `try: yield db` → `finally: db.close()` — le `finally` garantit la fermeture même en cas d'exception dans l'endpoint
- `get_current_user` : utilise `OAuth2PasswordBearer(tokenUrl="/auth/token")` pour extraire le token du header `Authorization: Bearer <token>`
- Décode le token avec `decode_access_token(token)` → récupère `payload["sub"]` (le username)
- Cherche l'user en DB avec `select(User).where(User.username == username)` → `scalar_one_or_none()`
- `Annotated[Session, Depends(get_db)]` crée un alias de type réutilisable directement dans les signatures d'endpoints

---

### ✅ Solution — `app/dependencies.py`

```python
from typing import Annotated, Generator
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session DB.
    Le code avant 'yield' s'exécute au début de la requête (ouverture).
    Le code dans 'finally' s'exécute après la réponse (fermeture garantie).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Alias typés — évitent de répéter Annotated[..., Depends(...)] dans chaque endpoint
DbDependency = Annotated[Session, Depends(get_db)]
TokenDependency = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenDependency, db: DbDependency) -> User:
    """
    Dépendance protégée : extrait le JWT du header Authorization,
    le décode, et retourne l'utilisateur correspondant depuis la DB.
    Lève une HTTPException 401 si le token est invalide, expiré, ou l'user introuvable.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user


# Alias pour les routes protégées
CurrentUser = Annotated[User, Depends(get_current_user)]
```

---

## PHASE 6 — Routers (Endpoints FastAPI)

### Pourquoi on fait les routers en dernier ?
Les routers dépendent de tout le reste (modèles, schémas, services, dépendances). C'est l'assemblage final. Construire les routers en premier forcerait à gérer des imports incomplets et du code cassé.

---

### 📌 Consigne — `app/routers/auth.py`

Crée deux endpoints :
- `POST /auth/register` → crée un utilisateur (vérifie l'unicité de l'email et du username)
- `POST /auth/token` → login OAuth2 (form-data) → retourne un JWT

💡 **Indices :**
- `router = APIRouter(prefix="/auth", tags=["Authentication"])`
- `POST /register` : reçoit `UserCreate`, hash le password, insère en DB, retourne `UserResponse` avec `status_code=201`
- `POST /token` : utilise `OAuth2PasswordRequestForm` — c'est un **form-data**, pas du JSON (important pour la compatibilité avec le flow OAuth2 standard)
- Vérifie l'unicité de l'email ET du username en une seule requête SQL avec `|` (OR)
- Si déjà utilisé → `HTTPException(409 Conflict)` ; si password incorrect → `HTTPException(401 Unauthorized)`

---

### ✅ Solution — `app/routers/auth.py`

```python
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.dependencies import DbDependency
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: DbDependency):
    """Inscription d'un nouvel utilisateur."""
    existing = db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ou username déjà utilisé",
        )

    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)   # Recharge depuis la DB pour obtenir l'id généré
    return db_user


@router.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbDependency,
):
    """Login OAuth2 — reçoit form-data (pas JSON), retourne un JWT."""
    user = db.execute(
        select(User).where(User.username == form_data.username)
    ).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username, "id": user.id})
    return Token(access_token=token)
```

---

### 📌 Consigne — `app/routers/documents.py`

Crée trois endpoints :
- `POST /documents/upload` → `UploadFile` → extrait le texte → sauvegarde en DB → `BackgroundTasks` pour l'indexation
- `GET /documents/` → liste les documents de l'utilisateur connecté
- `DELETE /documents/{doc_id}` → supprime de DB + de ChromaDB

💡 **Indices :**
- `UploadFile` : `await file.read()` pour lire les bytes, `file.filename` pour le nom
- Pour un PDF : `pypdf.PdfReader(io.BytesIO(content_bytes))` puis `page.extract_text()` sur chaque page
- Pour un `.txt` : `content_bytes.decode("utf-8", errors="ignore")`
- La background task doit créer sa **propre session DB** (voir la note dans la solution) — ne jamais passer la session du router
- `DELETE` : vérifie `doc.owner_id != current_user.id` → `HTTPException(403 Forbidden)`
- Note sur la signature : `DbDependency` et `CurrentUser` n'ont pas de valeur par défaut ; `file: UploadFile = File(...)` vient en dernier

---

### ✅ Solution — `app/routers/documents.py`

```python
import io
from typing import List
import pypdf
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy import select
from app.dependencies import DbDependency, CurrentUser
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentStatus
from app.services import rag_service

router = APIRouter(prefix="/documents", tags=["Documents"])


def _extract_text(content_bytes: bytes, filename: str) -> str:
    """Extrait le texte brut d'un PDF ou d'un fichier texte."""
    if filename.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(content_bytes))
        return " ".join(page.extract_text() or "" for page in reader.pages)
    return content_bytes.decode("utf-8", errors="ignore")


async def _index_document_task(doc_id: int, content: str, filename: str) -> None:
    """
    Tâche de fond : indexe le document dans ChromaDB et met à jour le status en DB.
    S'exécute APRÈS que la réponse HTTP 201 a été envoyée au client.

    ⚠️ On crée une NOUVELLE session DB ici — ne jamais réutiliser celle du router.
    Pourquoi ? La session du router est fermée dès que la réponse HTTP est envoyée
    (le 'finally db.close()' de get_db() s'est déjà exécuté). Passer cette session
    à la background task provoquerait une erreur 'session already closed'.
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        await rag_service.index_document(doc_id, content, filename)
        doc = db.get(Document, doc_id)
        if doc:
            doc.status = DocumentStatus.INDEXED
            db.commit()
    except Exception:
        db.rollback()
        doc = db.get(Document, doc_id)
        if doc:
            doc.status = DocumentStatus.FAILED
            db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    db: DbDependency,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    """
    Upload d'un document PDF ou TXT.
    Retourne immédiatement un 201 avec status=PENDING.
    L'indexation (embeddings → ChromaDB) se fait en arrière-plan.
    """
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Fichier vide")

    text_content = _extract_text(content_bytes, file.filename)
    if len(text_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="Contenu trop court pour être indexé")

    db_doc = Document(
        filename=file.filename,
        content=text_content,
        status=DocumentStatus.PENDING,
        owner_id=current_user.id,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # Lance l'indexation en arrière-plan — le 201 est renvoyé immédiatement
    background_tasks.add_task(_index_document_task, db_doc.id, text_content, file.filename)

    return db_doc


@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: DbDependency, current_user: CurrentUser):
    """Liste tous les documents de l'utilisateur connecté."""
    docs = db.execute(
        select(Document).where(Document.owner_id == current_user.id)
    ).scalars().all()
    return docs


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: int, db: DbDependency, current_user: CurrentUser):
    """Supprime un document de la DB et ses vecteurs de ChromaDB."""
    doc = db.execute(
        select(Document).where(Document.id == doc_id)
    ).scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    if doc.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action non autorisée")

    rag_service.delete_document_vectors(doc_id)
    db.delete(doc)
    db.commit()
```

---

### 📌 Consigne — `app/routers/chat.py`

Le router principal. Crée quatre endpoints :
- `POST /chat/query` → RAG pipeline complet, réponse JSON
- `POST /chat/stream` → même pipeline mais réponse SSE (streaming token par token)
- `POST /chat/extract` → Structured Output : extraction d'entités médicales
- `GET /chat/consultations` → liste les consultations de l'user avec leurs messages

💡 **Indices :**
- `/chat/stream` retourne `StreamingResponse(generate(), media_type="text/event-stream")` avec les headers `Cache-Control: no-cache` et `X-Accel-Buffering: no`
- Le générateur async du stream : appelle `rag_service.search_similar()`, construit le prompt, puis itère sur `llm_service.chat_stream()`
- Pour persister les messages après le stream : la session du router est fermée à ce moment-là — utilise une fonction dédiée `_persist_messages` qui crée sa propre `SessionLocal()`
- `/chat/extract` : appelle `llm_service.extract_structured()` puis valide avec `ExtractedMedicalEntities(**result)`
- `/chat/consultations` : `joinedload(Consultation.messages)` + `.unique().scalars().all()` charge les messages en une seule requête SQL (évite le problème N+1)
- Applique `@limiter.limit("20/minute")` sur les endpoints qui appellent OpenAI (coûteux)

---

### ✅ Solution — `app/routers/chat.py`

```python
import json
from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.dependencies import DbDependency, CurrentUser
from app.models.consultation import Consultation, Message
from app.schemas.consultation import ChatRequest, ConsultationResponse
from app.schemas.document import ExtractedMedicalEntities
from app.services import rag_service, llm_service

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])
limiter = Limiter(key_func=get_remote_address)


def _get_or_create_consultation(db, user_id: int, consultation_id=None) -> Consultation:
    """Retourne une consultation existante ou en crée une nouvelle."""
    if consultation_id:
        consult = db.execute(
            select(Consultation).where(
                Consultation.id == consultation_id,
                Consultation.user_id == user_id,
            )
        ).scalar_one_or_none()
        if not consult:
            raise HTTPException(status_code=404, detail="Consultation introuvable")
        return consult

    consult = Consultation(user_id=user_id)
    db.add(consult)
    db.commit()
    db.refresh(consult)
    return consult


def _persist_messages(consultation_id: int, user_msg: str, assistant_msg: str) -> None:
    """
    Persiste la paire user/assistant en base avec sa propre session DB.
    Utilisée dans les générateurs SSE où la session du router est déjà fermée.
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        db.add(Message(role="user", content=user_msg, consultation_id=consultation_id))
        db.add(Message(role="assistant", content=assistant_msg, consultation_id=consultation_id))
        db.commit()
    finally:
        db.close()


@router.post("/query")
@limiter.limit("20/minute")
async def query(
    request: Request,
    chat_req: ChatRequest,
    db: DbDependency,
    current_user: CurrentUser,
):
    """RAG pipeline complet — retourne la réponse JSON en une seule fois."""
    try:
        result = await rag_service.rag_pipeline(chat_req.message, chat_req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur LLM : {str(e)}")

    consult = _get_or_create_consultation(db, current_user.id, chat_req.consultation_id)
    _persist_messages(consult.id, chat_req.message, result["answer"])

    return {**result, "consultation_id": consult.id}


@router.post("/stream")
@limiter.limit("10/minute")
async def stream(
    request: Request,
    chat_req: ChatRequest,
    db: DbDependency,
    current_user: CurrentUser,
):
    """
    RAG pipeline + streaming SSE.
    Premier événement SSE : métadonnées (sources, consultation_id).
    Événements suivants : tokens du LLM un par un.
    Dernier événement : 'data: [DONE]'
    """
    consult = _get_or_create_consultation(db, current_user.id, chat_req.consultation_id)
    similar_chunks = await rag_service.search_similar(chat_req.message, chat_req.top_k)

    context = (
        "\n\n---\n\n".join(chunk for chunk, _ in similar_chunks)
        if similar_chunks else "Aucun contexte disponible."
    )
    sources = list({meta["filename"] for _, meta in similar_chunks})

    messages = [
        {"role": "system", "content": f"{rag_service.SYSTEM_DISCLAIMER}\n\nCONTEXTE :\n{context}"},
        {"role": "user", "content": chat_req.message},
    ]

    # Capture les valeurs avant que la session du router soit fermée
    consultation_id = consult.id
    user_message = chat_req.message
    full_response: List[str] = []

    async def generate():
        # Premier événement : métadonnées
        yield f"data: {json.dumps({'sources': sources, 'consultation_id': consultation_id})}\n\n"

        # Stream des tokens du LLM
        async for chunk in llm_service.chat_stream(messages):
            if chunk != "data: [DONE]\n\n":
                token_data = json.loads(chunk.replace("data: ", "").strip())
                full_response.append(token_data["token"])
            yield chunk

        # Persiste les messages une fois le stream terminé
        # La session du router est fermée ici → _persist_messages crée la sienne
        _persist_messages(consultation_id, user_message, "".join(full_response))

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/extract", response_model=ExtractedMedicalEntities)
@limiter.limit("10/minute")
async def extract_entities(
    request: Request,
    text: str,
    current_user: CurrentUser,
):
    """
    Structured Output : extrait des entités médicales d'un texte clinique.
    Le LLM est contraint à retourner un JSON validé par ExtractedMedicalEntities.
    """
    schema_desc = json.dumps({
        "symptoms": ["liste des symptômes mentionnés"],
        "medications": ["liste des médicaments"],
        "diagnoses": ["liste des diagnostics"],
        "recommendations": ["liste des recommandations"],
        "urgency_level": "faible | modéré | élevé | critique",
    }, ensure_ascii=False, indent=2)

    try:
        result = await llm_service.extract_structured(text, schema_desc)
        return ExtractedMedicalEntities(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction échouée : {str(e)}")


@router.get("/consultations", response_model=List[ConsultationResponse])
def list_consultations(db: DbDependency, current_user: CurrentUser):
    """
    Liste toutes les consultations de l'utilisateur avec leurs messages.
    joinedload charge les messages avec un JOIN SQL en une seule requête (évite le N+1).
    .unique() est obligatoire après joinedload : le JOIN peut dupliquer les lignes parentes.
    """
    consultations = db.execute(
        select(Consultation)
        .where(Consultation.user_id == current_user.id)
        .options(joinedload(Consultation.messages))
        .order_by(Consultation.created_at.desc())
    ).unique().scalars().all()
    return consultations
```

---

## PHASE 7 — Point d'entrée

### 📌 Consigne — `app/main.py`

Assemble tout : crée l'app FastAPI avec un `lifespan`, inclus les trois routers, configure le rate limiter.

💡 **Indices :**
- `lifespan` est un context manager async (`@asynccontextmanager`) : le code avant `yield` s'exécute au démarrage, le code après à l'arrêt
- `Base.metadata.create_all(bind=engine)` dans le lifespan crée les tables si elles n'existent pas encore (pratique en dev si tu n'as pas encore lancé Alembic)
- `app.state.limiter = limiter` + `app.add_exception_handler(RateLimitExceeded, ...)` sont obligatoires pour que slowapi fonctionne
- `SlowAPIMiddleware` s'ajoute avec `app.add_middleware(SlowAPIMiddleware)`
- Ajoute un endpoint `GET /health` pour vérifier que l'API tourne

---

### ✅ Solution — `app/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.database import engine, Base
from app.routers import auth, documents, chat

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Exécuté au démarrage et à l'arrêt de l'application.
    create_all crée les tables manquantes sans toucher aux existantes.
    En production, préfère Alembic pour gérer les migrations proprement.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="MedMind RAG API",
    description="Plateforme RAG médicale — FastAPI + OpenAI + ChromaDB",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuration du rate limiter (protection des endpoints OpenAI)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Inclusion des routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["Health"])
def health():
    """Endpoint de vérification — confirme que l'API est opérationnelle."""
    return {"status": "ok", "version": "1.0.0"}
```

---

## 🚀 Démarrage du projet

```bash
# 1. Créer le projet et installer les dépendances
uv init medmind-api && cd medmind-api
# Créer toute l'arborescence (dossiers + __init__.py vides)
uv sync

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env : renseigner OPENAI_API_KEY et SECRET_KEY

# 3. Initialiser Alembic
uv run alembic init alembic
# Modifier alembic/env.py comme décrit en Phase 2
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head

# 4. Lancer l'API
uv run uvicorn app.main:app --reload

# 5. Explorer
# Swagger UI : http://localhost:8000/docs
# ReDoc      : http://localhost:8000/redoc
# Health     : http://localhost:8000/health
```

---

## ✅ Checklist des concepts couverts

| Concept | Fichier |
|---|---|
| `@classmethod` dans les validateurs | `schemas/user.py`, `schemas/document.py` |
| `@property` + `@computed_field` | `schemas/document.py` |
| Héritage Python | Tous les schemas héritent de `BaseModel` |
| `StrEnum` + `auto()` | `schemas/document.py` |
| `TypeAlias` via `Annotated` | `dependencies.py` (`DbDependency`, `CurrentUser`) |
| Path params | `routers/documents.py` (`/{doc_id}`) |
| Query params | `routers/chat.py` (`top_k`) |
| `UploadFile` | `routers/documents.py` |
| `BackgroundTasks` | `routers/documents.py` |
| SSE + `StreamingResponse` | `routers/chat.py` |
| `HTTPException` + status codes | Tous les routers |
| `APIRouter` + prefix + tags | Tous les routers |
| `BaseModel` + `Field` | Tous les schemas |
| `@field_validator` | `schemas/user.py` |
| `@model_validator` | `schemas/consultation.py` |
| `ConfigDict(from_attributes=True)` | Tous les schemas Response |
| `model_dump()` | `services/llm_service.py` |
| SQLAlchemy 2.0 (`select`, `where`) | `routers/*.py`, `dependencies.py` |
| FK + `back_populates` | `models/*.py` |
| `joinedload` + `.unique()` | `routers/chat.py` |
| `scalar_one_or_none()` | `dependencies.py`, routers |
| Dependency Injection + `yield` | `dependencies.py` |
| Alembic migrations | Phase 2 |
| JWT (PyJWT) | `services/auth_service.py` |
| Argon2 hashing | `services/auth_service.py` |
| `OAuth2PasswordBearer` | `dependencies.py` |
| `AsyncOpenAI` | `services/llm_service.py` |
| Streaming SSE | `services/llm_service.py`, `routers/chat.py` |
| RAG pipeline | `services/rag_service.py` |
| Structured Outputs (JSON mode) | `services/llm_service.py` |
| Embeddings + ChromaDB | `services/rag_service.py` |
| Historique de conversation | `routers/chat.py`, `models/consultation.py` |
| Rate limiting (slowapi) | `routers/chat.py`, `main.py` |
| `uv` | Phase 0 |

---

## 💡 Idées d'extension pour aller plus loin

- **Pagination** sur `GET /documents/` et `GET /chat/consultations` (query params `skip` et `limit`)
- **WebSocket** (`/ws/chat/{consultation_id}`) : chat bidirectionnel en temps réel
- **Token counting** avant chaque appel OpenAI pour estimer le coût et éviter les dépassements de contexte
- **Tests** avec `pytest-asyncio` + `httpx.AsyncClient` sur l'app FastAPI
- **PostgreSQL** : remplacer SQLite par PostgreSQL pour un projet plus production-ready
