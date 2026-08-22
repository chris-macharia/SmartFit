# 👕 SmartFit

SmartFit is a web-based virtual fitting system designed to revolutionize the online clothing shopping experience. By leveraging computer vision and 3D modeling, SmartFit enables users to estimate body measurements from simple video uploads, generate personalized 3D digital avatars, and receive precise clothing size recommendations.

The project is built with a **React** frontend, **FastAPI** backend, **PostgreSQL** database with **SQLAlchemy ORM**, **OpenCV/MediaPipe** pose estimation, and **Three.js** 3D visual rendering.

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

<details open>
<summary><b>🔮 Milestone 6 — Avatar Generation & Virtual Fitting (🟡 In Progress)</b></summary>

* ✅ **Avatar Generation Service:** Backend logic to transform estimated body measurements into digital avatar data (`feat(avatar): implement avatar generation and retrieval`).
* ✅ **Pipeline Integration:** Seamless connection linking video measurement outputs directly to the avatar generation flow (`Connect video measurements to avatar generation flow`).
* ✅ **Backend Verification:** Dedicated unit/integration test suite covering avatar creation and retrieval.
* 🟡 **3D Avatar Rendering:** *(Active Focus)* Building the frontend 3D canvas using **Three.js** / **React Three Fiber** to render personalized avatars based on backend measurements.
* ⬜ **Garment Management System:** Retailer API for uploading 3D clothing items with dimensional metadata.
* ⬜ **Virtual Fitting Engine:** Collision detection and fit scoring algorithms for accurate size recommendations.
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
* **Styling:** CSS3 (Modern Flex/Grid with CSS variables for dark/light themes)
* **Networking:** Fetch API with custom HTTP client interceptors

### 🔮 3D Visualization & Engine
* **Render Engine:** Three.js / React Three Fiber

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
│   │   │   │   ├── videos.py
│   │   │   │   └── avatars.py
│   │   │   ├── dependencies.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
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
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   └── videoService.js
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

### 1️⃣ Backend Setup

```powershell
cd backend

# Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # On macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
Copy-Item .env.example .env
```

Ensure PostgreSQL is running with databases `SmartFit_db` and `SmartFit_Test_db`, then initialize and start:

```powershell
# Initialize database tables
python -m app.db.init_db

# Execute test suite
pytest -v

# Run FastAPI development server
uvicorn app.main:app --reload
```
*Interactive API Documentation:* `http://127.0.0.1:8000/docs`

---

### 2️⃣ Frontend Setup

```powershell
cd frontend

# Install Node modules
npm install

# Configure environment
Copy-Item .env.example .env

# Run Vite dev server
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
| `GET/POST` | `/api/avatars/` | Yes | Generate & retrieve avatar data from measurements |

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
| 6 — Avatar Generation & Virtual Fitting | 🟡 In Progress |