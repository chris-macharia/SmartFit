# 👕 SmartFit

SmartFit is a web-based virtual fitting system designed to revolutionize the online clothing shopping experience. By leveraging computer vision and 3D modeling, SmartFit enables users to estimate body measurements from simple video uploads, generate personalized 3D digital avatars, and receive precise clothing size recommendations.

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

<details>
<summary><b>👗 Milestone 7 — Garment Uploading & Management (✅ Complete)</b></summary>

* ✅ **Retailer & Admin API:** Complete Garment CRUD backend operations (`POST`, `GET`, `PUT`, `DELETE` `/api/garments/`) enforcing retailer-only authorization via `require_retailer` dependency.
* ✅ **Garment Schema & Service:** Integrated SQLAlchemy Garment model and Pydantic schemas (`GarmentCreate`, `GarmentUpdate`, `GarmentResponse`) mapping chest, waist, hip, shoulder width, and inseam measurements.
* ✅ **Multi-Tenant Ownership:** Enforced strict garment ownership validation tied to authenticated retailer account IDs.
* ✅ **Role-Specific Dashboard UI:** Authenticated dashboard routing displaying retailer-specific Upload Garment tiles (`/garments`) while preserving customer video and avatar workflows.
* ✅ **Retailer Garment Upload Page:** Interactive frontend form allowing retailers to register garments with physical measurement attributes using JWT Bearer authentication.
</details>

<details>
<summary><b>👕 Milestone 8 — Virtual Fitting (✅ Completed)</b></summary>

* ✅ **<b>Virtual Fitting Workflow:</b>** Implemented the complete customer virtual fitting workflow, allowing customers to select an available retailer garment and compare it against their generated avatar measurements.

* ✅ **<b>Fit Algorithm & Matching:</b>** Implemented measurement-based fitting logic comparing available body measurements with corresponding garment measurements to classify the fit as <b>Tight</b>, <b>Good Fit</b>, or <b>Loose</b>.

* ✅ **<b>Size Recommendations:</b>** Implemented initial size recommendation logic based on available chest measurements. When chest measurements are unavailable, the system safely returns <b>N/A</b> rather than failing.

* ✅ **<b>Partial Measurement Handling:</b>** Updated the fitting algorithm to ignore unavailable (<code>null</code>) measurements and perform matching using only the body and garment measurements currently available in the prototype.

* ✅ **<b>Virtual Fitting API:</b>** Added authenticated endpoints for creating and retrieving virtual fitting results, including validation for invalid garments, avatars, measurements, duplicate fittings, and unauthorized access.

* ✅ **<b>Available Garments:</b>** Added a customer-accessible endpoint for retrieving garments uploaded by retailers for virtual fitting.

* ✅ **<b>Frontend Integration:</b>** Added the Virtual Fitting interface, garment selection, fitting result display, recommended size display, and navigation from the generated avatar to the fitting workflow.

* 📝 **<b>Prototype Limitation:</b>** The current fitting system uses only the body measurements successfully extracted by the existing measurement module. Further refinement of measurement extraction, sizing accuracy, and advanced fitting logic will be addressed in future development.

</details>

<details>

<summary><b>🛡️ Milestone 9 — System Hardening (🟡 In Progress)</b></summary>

* 🟡 **<b>Security Hardening:</b>** Review and strengthen authentication, authorization, input validation, JWT handling, and protected API access across the system.

* 🟡 **<b>Backend Validation & Error Handling:</b>** Improve API validation, exception handling, HTTP status codes, and error responses to ensure predictable and secure backend behaviour.

* 🟡 **<b>Database & Data Integrity:</b>** Review database relationships, constraints, ownership checks, and data handling to prevent invalid or unauthorized records.

* 🟡 **<b>API Security Testing:</b>** Expand automated tests for authentication, authorization, invalid requests, unauthorized resource access, duplicate operations, and other security-related scenarios.

* 🟡 **<b>Frontend Security & Validation:</b>** Review protected routes, authentication state, API error handling, and client-side validation to improve the security and reliability of the frontend.

* 🟡 **<b>Frontend UI/UX:</b>** Improve the UI/UX of the web application.

* 🟡 **<b>Configuration & Environment Security:</b>** Review environment variables, secrets, development configuration, file handling, and other deployment-related settings to reduce security risks.

* 🟡 **<b>System Reliability:</b>** Identify and address edge cases, unexpected failures, and inconsistencies across the complete SmartFit workflow.

* 📝 **<b>Hardening Scope:</b>** Milestone 9 focuses on strengthening the existing SmartFit prototype rather than introducing major new functionality. The goal is to improve security, reliability, validation, testing, and overall system robustness before final project evaluation.

</details>

<details>
<summary><b>🕶️ Milestone 10 — Visualization (⬜ Planned)</b></summary>

* ⬜ **3D Garment Overlay:** Rendering 3D garment overlays onto the user's generated digital avatar.
* ⬜ **Interactive Virtual Fitting Room:** Real-time fitting room UI with fabric drape visualization, style toggling, and interactive fit inspection.
</details>

---

## 📊 Test Status

**<b>118 automated backend tests — ✅ All Passing</b>**

The backend test suite verifies system integrity across all implemented layers:

* 🔌 Database connectivity & clean schema resets

* 💾 CRUD persistence and foreign key constraints

* 🔐 Password hashing, JWT token generation, role-based access control, and authorization dependencies

* 🎥 Multi-tenant video upload, processing status, and deletion

* 📏 Pose landmarker detection and body measurement calculations

* 🧍 Avatar entity creation, persistence, service logic, and video-to-avatar data transformations

* 👗 Garment creation, retailer ownership enforcement, metadata updates, retrieval, and deletion operations

* 👕 Virtual fitting entity creation, persistence, validation, and API operations

* 📐 Measurement-based garment matching and fit classification

* 📏 Initial size recommendation logic and handling of unavailable measurements

* 🔄 Virtual fitting service integration between customers, avatars, body measurements, and garments

* 🔐 Virtual fitting authorization and customer ownership enforcement

---

## 🛠️ Technology Stack
<details>
<summary>⚙️ Backend </summary>

* **Language:** Python 3.12+

* **API Framework:** FastAPI

* **Database & ORM:** PostgreSQL, SQLAlchemy

* **Authentication:** Passlib (`bcrypt`), PyJWT

* **Computer Vision & ML:** OpenCV, MediaPipe Pose Landmarker

* **Testing:** Pytest
</details>

<details>
<summary>💻 Frontend</summary>

* **Core:** React 19, Vite 8

* **Routing:** React Router 7

* **3D Visualization & Engine:** Three.js, React Three Fiber (`@react-three/fiber`), Drei (`@react-three/drei`)

* **Styling:** CSS3 (Modern Flex/Grid with CSS variables for dark/light themes)

* **Networking:** Fetch API with a custom HTTP client wrapper, JWT authorization handling, and Blob stream handling
</details>

---



## 📁 Project Structure

<details>
<summary><b>🔧 Backend</b></summary>

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── users.py
│   │   │   ├── videos.py
│   │   │   ├── avatars.py
│   │   │   ├── garments.py
│   │   │   └── virtual_fittings.py
│   │   ├── dependencies.py
│   │   └── router.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── avatar.py
│   │   ├── body_measurements.py
│   │   ├── garment.py
│   │   ├── user.py
│   │   ├── video.py
│   │   └── virtual_fitting.py
│   │
│   ├── schemas/
│   │   ├── avatar.py
│   │   ├── garment.py
│   │   ├── user.py
│   │   ├── video.py
│   │   └── virtual_fitting.py
│   │
│   ├── services/
│   │   ├── avatar_generator.py
│   │   ├── avatar_service.py
│   │   ├── garment_service.py
│   │   ├── measurement_estimator.py
│   │   ├── pose_estimator.py
│   │   ├── video_processor.py
│   │   ├── virtual_fitting.py
│   │   └── virtual_fitting_service.py
│   │
│   ├── utils/
│   └── main.py
│
├── models/
│   └── pose_landmarker_lite.task
│
├── scripts/
│   ├── generate_project_tree.ps1
│   └── reset_databases.py
│
├── tests/
│   ├── test_auth_api.py
│   ├── test_auth_dependencies.py
│   ├── test_avatar_api.py
│   ├── test_avatar_crud.py
│   ├── test_avatar_model.py
│   ├── test_avatar_schema.py
│   ├── test_avatar_service.py
│   ├── test_body_measurement_crud.py
│   ├── test_body_measurement_model.py
│   ├── test_database_connection.py
│   ├── test_garment_api.py
│   ├── test_garment_crud.py
│   ├── test_garment_model.py
│   ├── test_garment_service.py
│   ├── test_measurement_estimator.py
│   ├── test_security.py
│   ├── test_user_api.py
│   ├── test_user_crud.py
│   ├── test_user_model.py
│   ├── test_user_schema.py
│   ├── test_video_api.py
│   ├── test_video_crud.py
│   ├── test_video_model.py
│   ├── test_virtual_fitting_api.py
│   ├── test_virtual_fitting_crud.py
│   ├── test_virtual_fitting_model.py
│   └── test_virtual_fitting_service.py
│
├── .env.example
├── pytest.ini
├── README.md
└── requirements.txt
```
</details> 

<details>
 <summary><b>💻 Frontend</b></summary>

```text
frontend/
├── public/
│   ├── favicon.svg
│   └── icons.svg
│
├── src/
│   ├── assets/
│   │   ├── hero.png
│   │   ├── react.svg
│   │   └── vite.svg
│   │
│   ├── components/
│   │   ├── Footer.jsx
│   │   ├── MainLayout.jsx
│   │   ├── Navbar.jsx
│   │   └── ProtectedRoute.jsx
│   │
│   ├── context/
│   │   └── AuthContext.jsx
│   │
│   ├── hooks/
│   │
│   ├── layouts/
│   │   └── MainLayout.jsx
│   │
│   ├── pages/
│   │   ├── Avatar.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Garments.jsx
│   │   ├── GenerateAvatar.jsx
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── UploadVideo.jsx
│   │   └── VirtualFitting.jsx
│   │
│   ├── services/
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── avatarService.js
│   │   ├── garmentService.js
│   │   ├── videoService.js
│   │   └── virtualFittingService.js
│   │
│   ├── App.css
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
│
├── .env.example
├── .gitignore
├── .oxlintrc.json
├── index.html
├── package.json
├── package-lock.json
├── README.md
└── vite.config.js
```
</details> 

<details>
<summary><b>📚 Documentation & UML</b></summary>

```text
docs/
├── ui-design/
│   ├── avatar_generation_interface.png
│   ├── customer_dashboard_interface.png
│   ├── garment_upload_and_management_interface.png
│   ├── home_screen_interface.png
│   ├── retailer_dashboard_interface.png
│   ├── user_login_interface.png
│   ├── user_registration_interface.png
│   ├── video_processing_interface.png
│   ├── video_upload_and_processing_interface.png
│   └── virtual_fitting_interface.png
│
├── uml-diagrams/
│   ├── 1_8_proposed_system_methodology/
│   │   ├── Data Collection Methods.png
│   │   ├── Data_collection_methods.puml
│   │   ├── Modular System Design Approach.png
│   │   ├── modular_system_design_approach.puml
│   │   ├── Software Development Methodology.png
│   │   ├── software_development_methodology.puml
│   │   ├── Testing and Evaluation Approach.png
│   │   ├── Testing_and_evaluation_report.puml
│   │   ├── Tools and Technologies used in the proposed system architecture.png
│   │   └── Tools_and_technologies_used.puml
│   │
│   ├── 2_4_integration_and_architecture/
│   │   ├── Avatar Generation and Visualization Module of the Proposed Virtual Fitting System.png
│   │   ├── Avatar_generation.puml
│   │   ├── Backend Layer of the Proposed Virtual Fitting System.png
│   │   ├── Backend_layer.puml
│   │   ├── Computer Vision Processing Module of the Proposed Virtual Fitting System.png
│   │   ├── Computer_vision_processing_module.puml
│   │   ├── Database Layer of the Proposed Virtual Fitting System.png
│   │   ├── Database_layer.puml
│   │   ├── Frontend Layer of the Proposed Virtual Fitting System.png
│   │   ├── Frontend_Layer.puml
│   │   ├── Integration_architecture.puml
│   │   ├── Integration_architecture_of_the_proposed_virtual_fitting_system.png
│   │   ├── System Integration Workflow of the Proposed Virtual Fitting System.png
│   │   └── System_integration_workflow.puml
│   │
│   ├── 3_6_system_specification/
│   │   ├── functional_requirement.png
│   │   ├── functional_requirement.puml
│   │   ├── non_functional_requirement.puml
│   │   └── non_functional_requirements.png
│   │
│   ├── 3_7_1_1_use_case_diagrams/
│   │   └── Use Case Diagram.png
│   │
│   ├── 3_7_4_activity_diagram/
│   │   └── Activity Diagrams.png
│   │
│   ├── 3_7_5_sequence_diagrams/
│   │   ├── Sequence_Avatar_Generation.png
│   │   ├── Sequence_Avatar_Generation.puml
│   │   ├── Sequence_Garment_Generation.png
│   │   ├── Sequence_Garment_Generation.puml
│   │   ├── Sequence_User_Authentication.png
│   │   ├── Sequence_User_Authentication.puml
│   │   ├── Sequence_Virtual_Fitting.png
│   │   └── Sequence_Virtual_Fitting.puml
│   │
│   ├── 3_8_logical_design/
│   │   ├── 3_8_1_system_architecture/
│   │   │   ├── application_layer.png
│   │   │   ├── application_layer.puml
│   │   │   ├── data_layer.png
│   │   │   ├── data_layer.puml
│   │   │   ├── presentation_layer.png
│   │   │   ├── presentation_layer.puml
│   │   │   ├── processing_layer.png
│   │   │   └── processing_layer.puml
│   │   │
│   │   ├── 3_8_2_control_flow_and_process_design/
│   │   │   ├── customer_virtual_fitting_process.png
│   │   │   ├── customer_virtual_fitting_process.puml
│   │   │   ├── exception_handling.png
│   │   │   ├── exception_handling.puml
│   │   │   ├── retailer_garment_management_process.png
│   │   │   ├── retailer_garment_management_process.puml
│   │   │   ├── system_control_logic.png
│   │   │   └── system_control_logic.puml
│   │   │
│   │   ├── 3_8_3_non_functional_requirements_design/
│   │   │   ├── error_exception_handling.png
│   │   │   ├── error_exception_handling.puml
│   │   │   ├── performance_maintainability_scalability.png
│   │   │   ├── performance_maintainability_scalability.puml
│   │   │   ├── security_design.png
│   │   │   ├── security_design.puml
│   │   │   ├── usability_user_experience.png
│   │   │   └── usability_user_experience.puml
│   │   │
│   │   ├── Logical_Architecture.png
│   │   └── Logical_Architecture.puml
│   │
│   └── 3_9_1_database_design/
│       ├── avatars_entity.png
│       ├── avatars_entity.puml
│       ├── body_measurements_entity.png
│       ├── body_measurements_entity.puml
│       ├── erd.png
│       ├── erd.puml
│       ├── garments_entity.png
│       ├── garments_entity.puml
│       ├── users_entity.png
│       ├── users_entity.puml
│       ├── videos_entity.png
│       ├── videos_entity.puml
│       ├── virtual_fittings_entity.png
│       └── virtual_fittings_entity.puml
│
├── Official SmartFit Documentation.docx
└── Official SmartFit Documentation.pdf
```

The `docs/` directory contains the project's formal documentation, UML/architecture source files, generated diagrams, and interface design references. PlantUML `.puml` files are retained alongside their corresponding `.png` diagrams to allow diagrams to be regenerated or modified when required.

</details>


<details>
<summary><b>📄 Root Files</b></summary>

```text
SmartFit/
├── .gitignore
├── README.md
├── setup.ps1       # Windows setup script
└── setup.sh        # macOS/Linux setup script
```
</details>

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
  .venv\Scripts\Activate.ps1   # Windows
  .venv/bin/activate          # MacOS/Linux

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

| Method | Endpoint | Auth Required | Role / Description |
|--------|----------|---------------|--------------------|
| `GET` | `/` | No | Health check and API status endpoint |
| `POST` | `/api/users/` | No | Register a new user |
| `POST` | `/api/users/login` | No | Authenticate user and issue JWT |
| `GET` | `/api/users/me` | Yes | Retrieve the logged-in user's profile |
| `POST` | `/api/videos/` | Yes | Upload a body video with height metadata (Customer) |
| `GET` | `/api/videos/{video_id}` | Yes | Retrieve video processing status and body measurements (Customer) |
| `DELETE` | `/api/videos/{video_id}` | Yes | Delete a user's uploaded body video (Customer) |
| `POST` | `/api/avatars/` | Yes | Generate a personalized avatar from body measurement data (Customer) |
| `GET` | `/api/avatars/me` | Yes | Retrieve the logged-in user's generated avatar (Customer) |
| `GET` | `/api/avatars/{avatar_id}/file` | Yes | Retrieve the authenticated user's avatar GLB model file (Customer) |
| `POST` | `/api/garments/` | Yes | Register a new garment with measurements (Retailer) |
| `GET` | `/api/garments/` | Yes | List garments owned by the authenticated retailer (Retailer) |
| `GET` | `/api/garments/available` | Yes | Retrieve garments available for customer virtual fitting |
| `GET` | `/api/garments/{garment_id}` | Yes | Retrieve a specific garment (Retailer) |
| `PUT` | `/api/garments/{garment_id}` | Yes | Update garment details and measurements (Retailer) |
| `DELETE` | `/api/garments/{garment_id}` | Yes | Delete a retailer's garment (Retailer) |
| `POST` | `/api/virtual-fittings/` | Yes | Create a virtual fitting using a garment and generated avatar (Customer) |
| `GET` | `/api/virtual-fittings/{fitting_id}` | Yes | Retrieve a virtual fitting result belonging to the authenticated customer |

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
| 7 — Garment Uploading & Management | ✅ Complete |
| 8 — Garment Matching | ✅ Complete |
| 9 — System Hardening | 🟡 In Progress |
| 10 — Visualization | ⬜ Planned |