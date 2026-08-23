# 👕 SmartFit

SmartFit is an AI-powered web-based virtual fitting system designed to revolutionize the online clothing shopping experience. By leveraging computer vision and 3D modeling, SmartFit enables users to estimate body measurements from simple video uploads, generate personalized 3D digital avatars, and receive precise clothing size recommendations.

The project is built with a **React** frontend, **FastAPI** backend, **PostgreSQL** database with **SQLAlchemy ORM**, **OpenCV/MediaPipe** pose estimation, and **Three.js / React Three Fiber** 3D visual rendering.

---

## 🚀 Development Status & Roadmap

<details>
<summary><b>🗄️ Milestone 1 — Database & Persistence Layer (✅ Complete)</b></summary>

* 🐘 **Database:** PostgreSQL integration with SQLAlchemy ORM and session management.
* 🆔 **Entity Identifiers:** UUID-based primary keys across all relational entities.
* 📐 **Data Schemas:** User, Video, Body Measurement, Avatar, Garment, and Virtual Fitting models.
* 🔗 **Entity Mapping:** Configured foreign key relationships and strict one-to-one constraints.
* 🧪 **Testing:** Automated CRUD persistence and schema validation test suites.
</details>

<details>
<summary><b>🔐 Milestone 2 — API Foundation (✅ Complete)</b></summary>

* ⚡ **Framework:** FastAPI modular router structure with shared database dependencies.
* 👤 **User Management:** User registration (`POST /api/users/`) with email uniqueness validation.
* 🔐 **Security:** Password hashing using `bcrypt` and JWT token authentication (`POST /api/users/login`).
* 🛡️ **Protected Routes:** Bearer token authentication middleware and user profile route (`GET /api/users/me`).
* 🎥 **Media API:** Video upload (`POST /api/videos/`) and deletion endpoints (`DELETE /api/videos/{video_id}`).
* 🌐 **Integration Prep:** CORS policies configured for React/Vite frontend integration.
* 🧪 **Test Isolation:** Dedicated PostgreSQL test database (`SmartFit_Test_db`) setup.
</details>

<details>
<summary><b>💻 Milestone 3 — Frontend Foundation (✅ Complete)</b></summary>

* ⚛️ **Framework:** React 19 + Vite 8 app shell configured with React Router 7 navigation.
* 🎨 **UI Engine:** Modern responsive layout featuring dark mode toggling and reusable UI components.
* 📱 **User Experience:** Complete dashboard, login, registration, video upload, and avatar viewer pages.
</details>

<details>
<summary><b>🔗 Milestone 4 — Frontend & Backend Integration (✅ Complete)</b></summary>

* 🔗 **API Client:** Centralized HTTP service (`src/services/api.js`) with automatic JWT Bearer header injection.
* 🧠 **State Management:** `AuthContext` provider handling application-wide authentication state.
* 🛡️ **Route Guards:** `ProtectedRoute` component managing session restoration and route authorization.
* 🎥 **Upload Flow:** Video upload interface with declared height inputs (100–250 cm) and 500 MB file validation.
* 🚪 **Auth Lifecycle:** Full integration of login, user registration, profile hydration, and session destruction.
</details>

<details>
<summary><b>👁️ Milestone 5 — Video Processing & Body Measurement (✅ Complete)</b></summary>

* 🎥 **Background Jobs:** Asynchronous video processing workflow using FastAPI `BackgroundTasks`.
* 👁️ **Computer Vision:** Integrated OpenCV and MediaPipe Pose Landmarker (`pose_estimator.py`).
* 📏 **Estimation Engine:** Height-calibrated shoulder-width and inseam calculation (`measurement_estimator.py`).
* 💾 **Persistence:** Stored measurement models complete with confidence metrics and algorithm versioning.
* 📊 **Progress UI:** Real-time frontend video status polling, progress indicators, and status UI tracking (`GET /api/videos/{video_id}`).
* 🛡️ **Data Isolation:** Strict multi-tenant security verification preventing cross-user video and measurement access.
</details>

<details>
<summary><b>🧍 Milestone 6 — Avatar Generation (✅ Complete)</b></summary>

* ✅ **Avatar Generation Service:** Backend logic to transform estimated body measurements into digital avatar data (`feat(avatar): implement avatar generation and retrieval`).
* ✅ **Pipeline Integration:** Seamless connection linking video measurement outputs directly to the avatar generation flow.
* ✅ **Backend Verification:** Dedicated unit/integration test suite covering avatar creation and retrieval.
* ✅ **3D Avatar Rendering:** Interactive frontend 3D canvas built with **Three.js**, **React Three Fiber**, and **Drei (`useGLTF`, `OrbitControls`)** rendering generated GLB models via blob URL fetching.
* ✅ **Full E2E Avatar Workflow:** Video Upload ➔ Processing ➔ Measurements ➔ Avatar Generation ➔ GLB Retrieval ➔ Interactive 3D Avatar Display.
</details>

<details open>
<summary><b>👗 Milestone 7 — Garment Uploading & Management (🟡 In Progress)</b></summary>

* 🟡 **Retailer & Admin API:** *(Active Focus)* Endpoints and services for uploading 3D clothing assets and managing garment metadata (e.g., dimensions, categories, sizes).
* ⬜ **Garment Storage & Retrieval:** Storage pipeline and schema integration for multi-size 3D garment models.
* ⬜ **Garment Management UI:** Frontend interface for browsing, filtering, and uploading 3D garments.
</details>

<details>
<summary><b>👕 Milestone 8 — Garment Matching (⬜ Planned)</b></summary>

* ⬜ **Fit Algorithm & Scoring:** Collision detection and dimensional matching logic comparing avatar measurements to garment parameters.
* ⬜ **Size Recommendations:** Precise sizing suggestions based on fit confidence and garment tolerance values.
</details>

<details>
<summary><b>🕶️ Milestone 9 — Visualization (⬜ Planned)</b></summary>

* ⬜ **3D Garment Overlay:** Rendering 3D garment overlays onto the user's generated digital avatar.
* ⬜ **Interactive Virtual Fitting Room:** Real-time fitting room UI with fabric drape visualization, style toggling, and interactive fit inspection.
</details>

---

## 📊 Test Status

**80 automated backend tests — ✅ All Passing**

The backend test suite verifies system integrity across all layers:
* 🔌 Database connectivity & clean schema resets
* 💾 CRUD persistence and foreign key constraints
* 🔐 Password hashing, JWT token generation, and authorization dependencies
* 🎥 Multi-tenant video upload, status polling, and deletion
* 📏 Pose landmarker detection and body measurement calculations
* 🧍 Avatar entity creation and video-to-avatar data transformations

---

## 🛠️ Technology Stack

### ⚙️ Backend
* **Language:** Python 3.12+
* **API Framework:** FastAPI
* **Database & ORM:** PostgreSQL, SQLAlchemy
* **Authentication:** Passlib (`bcrypt`), PyJWT
* **Computer Vision & ML:** OpenCV, MediaPipe Pose Landmarker
* **Testing:** Pytest

### 💻 Frontend
* **Core:** React 19, Vite 8
* **Routing:** React Router 7
* **3D Visualization & Engine:** Three.js, React Three Fiber (`@react-three/fiber`), Drei (`@react-three/drei`)
* **Styling:** CSS3 (Modern Flex/Grid with CSS variables for dark/light themes)
* **Networking:** Fetch API with custom HTTP client interceptors & Blob stream handling

---

## 📁 Project Structure

```text
SmartFit/
│
├── setup.ps1              # One-click setup script (Windows)
├── setup.sh               # One-click setup script (macOS/Linux)
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── users.py
│   │   │   │   ├── videos.py
│   │   │   │   └── avatars.py
│   │   │   ├── dependencies.py
│   │   │   └── router.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── pose_estimator.py
│   │   │   ├── measurement_estimator.py
│   │   │   └── avatar_service.py
│   │   └── main.py
│   │
│   ├── models/            # MediaPipe model assets (.task)
│   ├── tests/             # Pytest automated test suite
│   ├── uploads/           # Local video storage directory
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── pages/
│   │   │   ├── GenerateAvatar.jsx
│   │   │   └── Avatar.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   ├── videoService.js
│   │   │   └── avatarService.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example
│   └── package.json
│
├── docs/
└── README.md
```

---

## ⚡ Quick Start Guide

### 1️⃣ One-Command Automated Setup

Run the setup script for your operating system from the root folder. It will automatically check/create PostgreSQL databases (`SmartFit_db` & `SmartFit_Test_db`), set up Python `.venv`, install requirements, populate `.env` files, run database migrations, execute tests, and install npm packages.

* **Windows (PowerShell):**
  ```powershell
  .\setup.ps1
  ```

* **macOS / Linux (Bash):**
  ```bash
  chmod +x setup.sh
  ./setup.sh
  ```

<details>
<summary><b>📜 OS Setup Script Reference & Troubleshooting</b></summary>

<details>
<summary><b>🪟 Windows Setup Script (`setup.ps1`)</b></summary>

```powershell
# SmartFit Automated Setup Script for Windows (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting SmartFit Full System Setup..." -ForegroundColor Cyan

# PostgreSQL credentials
$env:PGUSER = if ($env:PGUSER) { $env:PGUSER } else { "postgres" }

# 1. Database Setup
Write-Host "`n🐘 Checking & Creating PostgreSQL Databases..." -ForegroundColor Yellow
try {
    psql -U $env:PGUSER -c 'CREATE DATABASE "SmartFit_db";' 2>$null
    Write-Host "  ✅ Database SmartFit_db ready." -ForegroundColor Green
} catch {
    Write-Host "  ℹ️ SmartFit_db ready or postgres CLI bypassed." -ForegroundColor Gray
}

try {
    psql -U $env:PGUSER -c 'CREATE DATABASE "SmartFit_Test_db";' 2>$null
    Write-Host "  ✅ Database SmartFit_Test_db ready." -ForegroundColor Green
} catch {
    Write-Host "  ℹ️ SmartFit_Test_db ready or postgres CLI bypassed." -ForegroundColor Gray
}

# 2. Backend Setup
Write-Host "`n⚙️ Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".venv")) {
    Write-Host "  📦 Creating Python virtual environment (.venv)..." -ForegroundColor Blue
    python -m venv .venv
}

Write-Host "  🔌 Activating virtual environment..." -ForegroundColor Blue
& .\.venv\Scripts\Activate.ps1

Write-Host "  📥 Installing Python dependencies..." -ForegroundColor Blue
pip install -r requirements.txt --quiet

if (-not (Test-Path ".env")) {
    Write-Host "  📄 Copying .env.example to .env..." -ForegroundColor Blue
    Copy-Item .env.example .env
}

Write-Host "  🗄️ Initializing database tables..." -ForegroundColor Blue
python -m app.db.init_db

Write-Host "  🧪 Executing automated backend test suite..." -ForegroundColor Blue
pytest -v

Set-Location ..

# 3. Frontend Setup
Write-Host "`n💻 Setting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path ".env")) {
    Write-Host "  📄 Copying .env.example to .env..." -ForegroundColor Blue
    Copy-Item .env.example .env
}

Write-Host "  📥 Installing npm packages (Three.js, R3F, React 19)..." -ForegroundColor Blue
npm install

Set-Location ..

Write-Host "`n🎉 Setup complete! You are ready to start development." -ForegroundColor Green
```
</details>

<details>
<summary><b>🍎 / 🐧 macOS & Linux Setup Script (`setup.sh`)</b></summary>

```bash
#!/usr/bin/env bash
set -e

echo "🚀 Starting SmartFit Full System Setup..."

PGUSER=${PGUSER:-postgres}

# 1. Database Setup
echo "
🐘 Checking & Creating PostgreSQL Databases..."
psql -U "$PGUSER" -c 'CREATE DATABASE "SmartFit_db";' 2>/dev/null || echo "  ℹ️ SmartFit_db ready or already exists."
psql -U "$PGUSER" -c 'CREATE DATABASE "SmartFit_Test_db";' 2>/dev/null || echo "  ℹ️ SmartFit_Test_db ready or already exists."

# 2. Backend Setup
echo "
⚙️ Setting up Backend..."
cd backend

if [ ! -d ".venv" ]; then
    echo "  📦 Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "  🔌 Activating virtual environment..."
source .venv/bin/activate

echo "  📥 Installing Python dependencies..."
pip install -r requirements.txt --quiet

if [ ! -f ".env" ]; then
    echo "  📄 Copying .env.example to .env..."
    cp .env.example .env
fi

echo "  🗄️ Initializing database tables..."
python -m app.db.init_db

echo "  🧪 Executing automated backend test suite..."
pytest -v

cd ..

# 3. Frontend Setup
echo "
💻 Setting up Frontend..."
cd frontend

if [ ! -f ".env" ]; then
    echo "  📄 Copying .env.example to .env..."
    cp .env.example .env
fi

echo "  📥 Installing npm packages..."
npm install

cd ..

echo "
🎉 Setup complete! You are ready to start development."
```
</details>

<details>
<summary><b>🛠️ Manual Setup Steps</b></summary>

If you prefer to run each step manually:

1. **PostgreSQL Databases:**
   ```sql
   CREATE DATABASE "SmartFit_db";
   CREATE DATABASE "SmartFit_Test_db";
   ```
2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   cp .env.example .env       # Windows: Copy-Item .env.example .env
   python -m app.db.init_db
   pytest -v
   ```
3. **Frontend Setup:**
   ```bash
   cd frontend
   cp .env.example .env       # Windows: Copy-Item .env.example .env
   npm install
   ```
</details>

</details>

---

### 2️⃣ Start Development Servers

Open two terminal windows to start the services:

* **Backend Server:**
  ```powershell
  cd backend
  .venv\Scripts\Activate.ps1   # macOS/Linux: source .venv/bin/activate
  uvicorn app.main:app --reload
  ```
  *Interactive API Documentation:* `http://127.0.0.1:8000/docs`

* **Frontend Client:**
  ```powershell
  cd frontend
  npm run dev
  ```
  *Application Client:* `http://localhost:5173`

---

## 🔌 Current API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/` | No | Health check endpoint |
| `POST` | `/api/users/` | No | User registration |
| `POST` | `/api/users/login` | No | User login & JWT issuance |
| `GET` | `/api/users/me` | Yes | Retrieve logged-in user profile |
| `POST` | `/api/videos/` | Yes | Upload body video with height metadata |
| `GET` | `/api/videos/{video_id}` | Yes | Query video processing & measurement status |
| `DELETE` | `/api/videos/{video_id}` | Yes | Delete user video |
| `POST` | `/api/avatars/` | Yes | Generate avatar metadata from measurement UUID |
| `GET` | `/api/avatars/me` | Yes | Retrieve user's generated avatar metadata |
| `GET` | `/api/avatars/{avatar_id}/file` | Yes | Download authenticated avatar GLB model binary stream |

---

## 🌿 Development Workflow

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
| 4 — Frontend & Backend Integration | ✅ Complete |
| 5 — Video Processing & Body Measurement | ✅ Complete |
| 6 — Avatar Generation | ✅ Complete |
| 7 — Garment Uploading & Management | 🟡 In Progress |
| 8 — Garment Matching | ⬜ Planned |
| 9 — Visualization | ⬜ Planned |