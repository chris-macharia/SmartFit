# 👕 SmartFit

SmartFit is a web-based virtual fitting system designed to improve the online clothing shopping experience by helping users estimate their body measurements, generate personalized digital avatars, and receive clothing size recommendations.

The system uses a React frontend, FastAPI backend, PostgreSQL database, SQLAlchemy ORM, and computer vision technologies.

---

## 🚀 Current Development Status

### 🗄️ Milestone 1 — Database and Persistence Layer

**Status: ✅ Complete**

The current version of SmartFit includes:

* 🐘 PostgreSQL database integration
* 🔗 SQLAlchemy ORM configuration
* 🧩 Database session management
* ⚙️ Database initialization
* 🆔 UUID-based primary keys
* 👤 User model
* 🎥 Video model
* 📏 Body Measurement model
* 🧍 Avatar model
* 👕 Garment model
* 🪞 Virtual Fitting model
* 🔗 Foreign key relationships between entities
* 🔄 One-to-one relationships for body measurements and avatars
* 🧪 CRUD persistence tests
* 🔍 Database model validation tests

### 🔐 Milestone 2 — API Foundation

**Status: ✅ Complete**

The SmartFit backend API foundation has been implemented and tested. It currently includes:

* ⚡ FastAPI API structure
* 👤 User registration API
* 📧 Email uniqueness validation
* 🔐 Secure password hashing using bcrypt
* 🔑 Password verification
* 🔓 User login API
* 🎟️ JWT access token generation
* 🛡️ JWT authentication and validation
* 👤 Protected current-user profile endpoint
* 🔗 Shared database session dependency
* 🧪 Isolated PostgreSQL test database
* 🔄 Repeatable automated API tests
* 🔒 Secure API responses that do not expose password hashes

### 📊 Test Status

**55 automated tests — ✅ All Passing**

The automated test suite covers database models, CRUD operations, API endpoints, password security, user authentication, JWT authentication, and protected endpoints.

---

## 🛠️ Technology Stack

### ⚙️ Backend

* 🐍 Python
* ⚡ FastAPI
* 🔗 SQLAlchemy
* 🐘 PostgreSQL
* 📦 Pydantic
* 🔐 Passlib
* 🔑 JWT
* 🧪 Pytest

### 💻 Frontend

* ⚛️ React

### 🔧 Development Tools

* 📂 Git
* 🐙 GitHub
* 📝 Visual Studio Code

---

## 📁 Project Structure

```text
SmartFit/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── main.py
│   │   └── __init__.py
│   │
│   ├── tests/
│   ├── uploads/
│   ├── .env.example
│   ├── requirements.txt
│   └── pytest.ini
│
├── docs/
│   └── uml/
│
├── .gitignore
└── README.md
```

---

# 🖥️ Backend Setup

## 📋 Requirements

Before setting up the SmartFit backend, install the following:

* 🐍 Python 3.12 or later
* 🐘 PostgreSQL
* 📂 Git

---

## 1️⃣ Clone the Repository

Clone the SmartFit repository from GitHub:

```powershell
git clone https://github.com/chris-macharia/SmartFit
```

Navigate into the project:

```powershell
cd SmartFit
```

---

## 2️⃣ Navigate to the Backend

```powershell
cd backend
```

---

## 3️⃣ Create a Python Virtual Environment

Create a virtual environment named `.venv`:

```powershell
python -m venv .venv
```

---

## 4️⃣ Activate the Virtual Environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

The terminal should now display:

```text
(.venv)
```

before the current directory.

---

## 5️⃣ Install Python Dependencies

Install the required backend packages:

```powershell
pip install -r requirements.txt
```

---

# 🐘 PostgreSQL Database Setup

SmartFit currently requires a PostgreSQL database named:

```text
SmartFit_db
```

The database must be created before initializing the SmartFit tables.

You can create the database using **pgAdmin** or the PostgreSQL command-line tools.

The expected development database configuration is:

```text
Host:     localhost
Port:     5432
Database: SmartFit_db
User:     postgres
```

For automated testing, SmartFit uses a separate PostgreSQL database:

```text
SmartFit_Test_db
```

The test database is used exclusively by the automated test suite to prevent tests from modifying the development database.

---

## 6️⃣ Configure Environment Variables 🔐

Create a local `.env` file by copying the provided example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace `YOUR_PASSWORD` with the password configured for your PostgreSQL `postgres` user.

The configuration should follow this format:

```env
# Development Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/SmartFit_db

# Test Database
TEST_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/SmartFit_Test_db
```

**⚠️ Important:** Do not commit the `.env` file to Git.

The `.env` file contains local configuration and credentials and is excluded from version control.

The `.env.example` file is provided as a safe configuration template.

---

# 🗃️ Database Initialization

## 7️⃣ Create SmartFit Database Tables

After creating the `SmartFit_db` database and configuring `.env`, initialize the SmartFit database tables:

```powershell
python -m app.db.init_db
```

A successful initialization should display:

```text
Database tables initialized successfully.
```

The current database contains the following core entities:

```text
👤 Users
🎥 Videos
📏 BodyMeasurements
🧍 Avatars
👕 Garments
🪞 VirtualFittings
```

---

# 🧪 Running Tests

## 8️⃣ Run the Automated Test Suite

From the `backend` directory, run:

```powershell
pytest -v
```

The current expected result is:

```text
55 passed
```

The test suite uses the isolated `SmartFit_Test_db` database and verifies:

* 🔌 Database connectivity
* 🗄️ Database model registration
* 📋 Table columns
* 🆔 UUID primary keys
* 🔗 Foreign key relationships
* 🔄 One-to-one constraints
* 💾 CRUD persistence
* 👤 User registration
* 🔐 Password hashing and verification
* 🔑 JWT authentication
* 🛡️ Protected API endpoints
* 🪞 Virtual fitting relationships

All tests should pass before changes are merged into the `main` branch.

---

# ⚡ Running the FastAPI Backend

## 9️⃣ Start the Development Server

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The FastAPI development server will start locally.

The interactive API documentation can be accessed through the FastAPI Swagger UI.

---

# 🌿 Development Workflow

SmartFit uses Git branches to separate stable code from ongoing development.

The `main` branch represents the latest stable and tested version of the project.

Development work is performed on milestone branches.

The current workflow is:

```text
main
  │
  │ 🟢 Stable and tested
  │
  ▼
🌿 Create milestone branch
  │
  ▼
💻 Implement functionality
  │
  ▼
🧪 Write automated tests
  │
  ▼
🔍 Run full test suite
  │
  ▼
✅ Review changes
  │
  ▼
🚀 Merge into main
```

### 📌 Completed Milestones

**Milestone 1 — Database and Persistence Layer**

Status: ✅ Complete

**Milestone 2 — API Foundation**

Status: ✅ Complete

Tests: 🧪 55 passing

### 🔜 Current Milestone

**Milestone 3 — Frontend Foundation**

Status: 🚧 In Progress

The next development stage focuses on building the React frontend and connecting it to the completed FastAPI backend.

---

# 🔐 Security Notes

Never commit sensitive credentials to GitHub.

The following files should remain local:

```text
.env
```

The following file may be committed:

```text
.env.example
```

The `.env.example` file contains configuration placeholders only and does not contain real credentials.

---

# 🧠 Project Development Philosophy

SmartFit is developed incrementally using a test-driven and milestone-based approach.

Each major milestone follows the process:

```text
📝 Design
   ↓
💻 Implementation
   ↓
🧪 Automated Testing
   ↓
🔍 Verification
   ↓
📦 Git Commit
   ↓
🚀 Merge into main
```

The objective is to ensure that the `main` branch remains a **stable, reproducible, and functional version** of the SmartFit system throughout development.

---

## 👨‍💻 Project Status

**SmartFit — Virtual Fitting System**

🚧 **Currently in active development**

**Milestone 1:** ✅ Database & Persistence Layer

**Milestone 2:** ✅ API Foundation

**Milestone 3:** 🚧 Frontend Foundation

**Future:** 🎥 Video Processing · 📏 Body Measurement Estimation · 🧍 Avatar Generation · 👕 Virtual Fitting · 📊 Size Recommendations
