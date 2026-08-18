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

---

### 🔐 Milestone 2 — API Foundation

**Status: ✅ Complete**

The SmartFit backend API foundation has been implemented and tested. It currently includes:

* ⚡ FastAPI API structure
* 👤 User registration API (`POST /api/users/`)
* 📧 Email uniqueness validation
* 🔐 Secure password hashing using bcrypt
* 🔑 Password verification
* 🔓 User login API (`POST /api/users/login`)
* 🎟️ JWT access token generation
* 🛡️ JWT authentication and validation
* 👤 Protected current-user profile endpoint (`GET /api/users/me`)
* 🎥 Video upload API (`POST /api/videos/`)
* 🗑️ Video delete API (`DELETE /api/videos/{video_id}`)
* 🔗 Shared database session dependency
* 🌐 CORS configuration for the React/Vite frontend
* 🧪 Isolated PostgreSQL test database
* 🔄 Repeatable automated API tests
* 🔒 Secure API responses that do not expose password hashes

---

### 💻 Milestone 3 — Frontend Foundation

**Status: ✅ Complete**

The initial SmartFit React frontend has been implemented as a stable user interface foundation. It currently includes:

* ⚛️ React and Vite frontend setup
* 🧭 React Router navigation
* 🏠 Home page
* 🔐 Login page
* 📝 Registration page
* 📊 User dashboard
* 🎥 Video upload interface
* 🧍 Avatar interface
* 🧱 Shared main layout
* 🦶 Shared footer
* 🌙 Dark mode toggle
* 📱 Responsive frontend structure
* 🧩 Reusable frontend components and layouts

---

### 🔗 Milestone 4 — Frontend & Backend Integration

**Status: 🟡 In Progress (Core integration complete)**

The React frontend is now connected to the FastAPI backend for authentication and video upload. Completed integration work includes:

* 🔗 Shared frontend API client (`src/services/api.js`)
* 🌍 Frontend environment configuration (`VITE_API_URL`)
* 📝 Registration API integration
* 🔐 Login API integration
* 🎟️ JWT token storage and automatic Bearer authentication
* 🧠 Centralized authentication state (`AuthContext`)
* 🛡️ Protected frontend routes with session restoration
* 👤 Current-user profile integration (Dashboard, Navbar)
* 🚪 Logout functionality
* 🎥 Video upload API integration

Remaining Milestone 4 work:

* 🗑️ Video delete integration in the frontend UI
* 📋 Display uploaded video status and history
* 🧪 Frontend integration testing and polish
* ⚠️ Consistent error handling across integrated pages

---

### 🔮 Milestone 5 — Video Processing & Body Measurement

**Status: ⬜ Planned**

* 🎥 Body video processing pipeline
* 👁️ Computer vision integration (OpenCV + MediaPipe)
* 📏 Body measurement estimation from video
* 🔄 Video processing status updates
* 💾 Persisted body measurement records

---

### 🔮 Milestone 6 — Avatar Generation & Virtual Fitting

**Status: ⬜ Planned**

* 🧍 Digital avatar generation from body measurements
* 👕 Garment upload and management (retailer workflow)
* 🪞 Virtual fitting engine
* 📊 Size recommendation logic
* 🎨 3D visualization (Three.js)
* 📈 Fit result display

---

### 📊 Test Status

**61 automated backend tests — ✅ All Passing**

The automated test suite covers:

* 🔌 Database connectivity
* 🗄️ Database model registration
* 📋 Table columns and UUID primary keys
* 🔗 Foreign key and one-to-one relationships
* 💾 CRUD persistence
* 👤 User registration and schema validation
* 🔐 Password hashing and verification
* 🔑 JWT authentication
* 🛡️ Protected API endpoints
* 🎥 Video upload and delete API behaviour
* 🪞 Virtual fitting relationships

---

## 🛠️ Technology Stack

### ⚙️ Backend

* 🐍 Python
* ⚡ FastAPI
* 🔗 SQLAlchemy
* 🐘 PostgreSQL
* 📦 Pydantic
* 🔐 Passlib / bcrypt
* 🔑 JWT
* 🧪 Pytest

### 💻 Frontend

* ⚛️ React 19
* ⚡ Vite 8
* 🧭 React Router 7
* 📡 Fetch API (via shared `apiRequest` client)
* 🎨 CSS

### 🔮 Planned Processing & Visualization

* 👁️ OpenCV + MediaPipe (body measurement extraction)
* 🎨 Three.js (virtual fitting visualization)

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
│   │   │   ├── routes/
│   │   │   │   ├── users.py
│   │   │   │   └── videos.py
│   │   │   ├── dependencies.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── uploads/
│   ├── .env.example
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   └── videoService.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
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

## 6️⃣ Configure Backend Environment Variables 🔐

Create a local `.env` file by copying the provided example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder values with your local configuration:

```env
# Development Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/SmartFit_db

# Test Database
TEST_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/SmartFit_Test_db

# JWT Authentication
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
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
61 passed
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
* 🎥 Video upload and delete API behaviour
* 🪞 Virtual fitting relationships

All tests should pass before changes are merged into the `main` branch.

---

# ⚡ Running the FastAPI Backend

## 9️⃣ Start the Development Server

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The FastAPI development server will start locally at:

```text
http://127.0.0.1:8000
```

The interactive API documentation can be accessed at:

```text
http://127.0.0.1:8000/docs
```

---

# 💻 Frontend Setup

## 📋 Frontend Requirements

Before running the SmartFit frontend, install:

* 🟢 Node.js
* 📦 npm

---

## 🔟 Navigate to the Frontend

From the SmartFit project root:

```powershell
cd frontend
```

---

## 1️⃣1️⃣ Install Frontend Dependencies

```powershell
npm install
```

---

## 1️⃣2️⃣ Configure Frontend Environment Variables

Create a local `.env` file by copying the provided example:

```powershell
Copy-Item .env.example .env
```

The default configuration should be:

```env
VITE_API_URL=http://127.0.0.1:8000
```

**⚠️ Important:** Do not commit the `.env` file to Git.

Frontend environment files containing `VITE_*` variables should not contain sensitive backend credentials or secrets, because Vite exposes these variables to frontend code.

---

## 1️⃣3️⃣ Start the Frontend Development Server

```powershell
npm run dev
```

Vite will provide a local development address in the terminal (typically `http://localhost:5173`).

Open the displayed address in your browser to access the SmartFit frontend.

---

# 🔌 Current API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | No | API health check |
| `POST` | `/api/users/` | No | Register a new user |
| `POST` | `/api/users/login` | No | Authenticate and receive JWT |
| `GET` | `/api/users/me` | Yes | Get current user profile |
| `POST` | `/api/videos/` | Yes | Upload a body video |
| `DELETE` | `/api/videos/{video_id}` | Yes | Delete a user's video |

Models exist in the database layer for avatars, garments, body measurements, and virtual fittings, but API routes for those features have not been implemented yet.

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

### 📌 Milestone Summary

| Milestone | Status |
|-----------|--------|
| 1 — Database & Persistence Layer | ✅ Complete |
| 2 — API Foundation | ✅ Complete |
| 3 — Frontend Foundation | ✅ Complete |
| 4 — Frontend & Backend Integration | 🟡 In Progress |
| 5 — Video Processing & Body Measurement | ⬜ Planned |
| 6 — Avatar Generation & Virtual Fitting | ⬜ Planned |

---

# 🔐 Security Notes

Never commit sensitive credentials to GitHub.

The following files should remain local:

```text
backend/.env
frontend/.env
```

The following files may be committed:

```text
backend/.env.example
frontend/.env.example
```

The `.env.example` files contain configuration placeholders only and do not contain real credentials.

Frontend environment files containing `VITE_*` variables should also not contain sensitive backend credentials or secrets, because Vite exposes these variables to frontend code.

Passwords are hashed on the backend using bcrypt. JWT access tokens are stored in the browser's `localStorage` under the key `smartfit_token`.

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

**Completed:**

* ✅ Database & Persistence Layer
* ✅ API Foundation
* ✅ Frontend Foundation

**In Progress:**

* 🟡 Frontend & Backend Integration (auth and video upload connected)

**Upcoming:**

* ⬜ Video Processing & Body Measurement Estimation
* ⬜ Avatar Generation
* ⬜ Garment Management
* ⬜ Virtual Fitting & Size Recommendations
* ⬜ 3D Visualization
