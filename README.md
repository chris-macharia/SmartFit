# 👕 SmartFit  v0.0.1

SmartFit is a web-based virtual fitting system designed to revolutionize the online clothing shopping experience. By leveraging computer vision and 3D modeling, SmartFit enables users to estimate body measurements from simple video uploads, generate personalized 3D digital avatars, and receive precise clothing size recommendations.

The project is built with a **React** frontend, **FastAPI** backend, **PostgreSQL** database with **SQLAlchemy ORM**, **OpenCV/MediaPipe** pose estimation, and **Three.js / React Three Fiber** 3D visual rendering.

---

## 🚀 Development Status & Roadmap

<details>

<summary><b>🗄️ Milestone 1 — Database & Persistence Layer (✅ Complete)</b></summary>

* 🐘 **Database:** PostgreSQL integration with SQLAlchemy ORM and session management.
* 🆔 **Entity Identifiers:** UUID-based primary keys across all relational entities.
* 📐 **Data Schemas:** User, Video, Body Measurement, Avatar, Garment, and Virtual Fitting models.
* 🔗 **Entity Mapping:** Configured foreign key relationships and one-to-one constraints where required.
* 🧪 **Testing:** Automated CRUD persistence and schema validation test suites.

</details>

<details>

<summary><b>🔐 Milestone 2 — API Foundation (✅ Complete)</b></summary>

* ⚡ **Framework:** FastAPI modular router structure with shared database dependencies.
* 👤 **User Management:** User registration (`POST /api/users/`) with email uniqueness validation.
* 🔐 **Security:** Password hashing using `bcrypt` and JWT token authentication (`POST /api/users/login`).
* 🛡️ **Protected Routes:** Bearer token authentication and authenticated user profile access (`GET /api/users/me`).
* 🎥 **Media API:** Video upload (`POST /api/videos/`) and deletion (`DELETE /api/videos/{video_id}`).
* 🌐 **Integration Preparation:** CORS policies configured for React/Vite frontend integration.
* 🧪 **Test Isolation:** Dedicated PostgreSQL test database (`SmartFit_Test_db`) for automated testing.

</details>

<details>

<summary><b>💻 Milestone 3 — Frontend Foundation (✅ Complete)</b></summary>

* ⚛️ **Framework:** React 19 + Vite 8 with React Router 7 navigation.
* 🎨 **UI Engine:** Responsive interface with dark-mode support and reusable UI components.
* 📱 **User Experience:** Dashboard, login, registration, video upload, and avatar viewer pages.

</details>

<details>

<summary><b>🔗 Milestone 4 — Frontend & Backend Integration (✅ Complete)</b></summary>

* 🔗 **API Client:** Centralized HTTP service (`src/services/api.js`) with automatic JWT Bearer header injection.
* 🧠 **State Management:** `AuthContext` provider handling application-wide authentication state.
* 🛡️ **Route Guards:** `ProtectedRoute` component managing authentication state and route authorization.
* 🎥 **Upload Flow:** Video upload interface with declared height inputs (100–250 cm) and 500 MB file validation.
* 🚪 **Authentication Lifecycle:** Integrated login, registration, profile retrieval, session restoration, and logout.

</details>

<details>

<summary><b>👁️ Milestone 5 — Video Processing & Body Measurement (✅ Complete)</b></summary>

* 🎥 **Background Processing:** Asynchronous video processing using FastAPI `BackgroundTasks`.
* 👁️ **Computer Vision:** OpenCV and MediaPipe Pose Landmarker integration through the pose estimation pipeline.
* 📏 **Measurement Engine:** Height-calibrated shoulder-width and inseam estimation.
* 💾 **Persistence:** Body measurement records stored with confidence metrics and algorithm versioning.
* 📊 **Progress UI:** Frontend video-status polling, progress indicators, and processing-status tracking.
* 🛡️ **Data Isolation:** Access controls preventing users from accessing videos and measurements belonging to other accounts.

</details>

<details>

<summary><b>🧍 Milestone 6 — Avatar Generation (✅ Complete)</b></summary>

* ✅ **Avatar Generation Service:** Backend service for transforming estimated body measurements into digital avatar data.
* ✅ **Pipeline Integration:** Integrated video processing, measurement extraction, and avatar generation workflows.
* ✅ **Backend Verification:** Dedicated unit and integration tests covering avatar creation and retrieval.
* ✅ **3D Avatar Rendering:** Interactive 3D rendering using **Three.js**, **React Three Fiber**, and **Drei** (`useGLTF`, `OrbitControls`).
* ✅ **Complete Avatar Workflow:** Video Upload ➔ Processing ➔ Measurements ➔ Avatar Generation ➔ GLB Retrieval ➔ Interactive 3D Avatar Display.

</details>

<details>

<summary><b>👗 Milestone 7 — Garment Uploading & Management (✅ Complete)</b></summary>

* ✅ **Retailer API:** Complete garment CRUD operations (`POST`, `GET`, `PUT`, `DELETE /api/garments/`) with retailer-only authorization.
* ✅ **Garment Schema & Service:** SQLAlchemy Garment model and Pydantic schemas covering chest, waist, hip, shoulder-width, and inseam measurements.
* ✅ **Multi-Tenant Ownership:** Garment ownership validation tied to authenticated retailer accounts.
* ✅ **Role-Specific Dashboard:** Retailer-specific garment management interface while preserving customer workflows.
* ✅ **Garment Upload Interface:** Interactive frontend form allowing retailers to register garments and their physical measurement attributes.

</details>

<details>

<summary><b>👕 Milestone 8 — Virtual Fitting (✅ Complete)</b></summary>

* ✅ **Virtual Fitting Workflow:** Customer workflow for selecting retailer garments and comparing them against generated avatar measurements.
* ✅ **Fit Algorithm & Matching:** Measurement-based fitting logic classifying results as **Tight**, **Good Fit**, or **Loose**.
* ✅ **Size Recommendations:** Initial size recommendation logic based on available chest measurements, returning **N/A** when the required measurement is unavailable.
* ✅ **Partial Measurement Handling:** Unavailable (`null`) measurements are excluded from fitting calculations so the prototype can operate with the measurements currently supported by the measurement module.
* ✅ **Virtual Fitting API:** Authenticated endpoints for creating and retrieving fitting results, with validation for invalid garments, avatars, measurements, duplicate fittings, and unauthorized access.
* ✅ **Available Garments:** Customer-accessible endpoint for retrieving garments uploaded by retailers.
* ✅ **Frontend Integration:** Virtual Fitting interface with garment selection, fitting-result display, recommended-size display, and navigation from the generated avatar.
* 📝 **Prototype Limitation:** The current fitting system uses only body measurements successfully extracted by the existing measurement module. Further refinement of measurement extraction, sizing accuracy, and fitting logic remains part of future development.

</details>

<details>

<summary><b>🛡️ Milestone 9 — System Hardening (✅ Complete)</b></summary>

* ✅ **Security Hardening:** Review and strengthen authentication, authorization, input validation, JWT handling, and protected API access.
* ✅ **Backend Validation & Error Handling:** Improve API validation, exception handling, HTTP status codes, and error responses for predictable backend behaviour.
* ✅ **Database & Data Integrity:** Review relationships, constraints, ownership checks, and data handling to prevent invalid or unauthorized records.
* ✅ **API Security Testing:** Expand automated tests covering authentication, authorization, invalid requests, unauthorized resource access, duplicate operations, and security-related edge cases.
* ✅ **Frontend Security & Validation:** Review protected routes, authentication state, API error handling, and client-side validation.
* ✅ **Frontend UI/UX:** Improve the consistency, usability, responsiveness, and overall presentation of the web application.
* ✅ **Configuration & Environment Security:** Review environment variables, secrets, development configuration, file handling, and deployment-related settings.
* ✅ **System Reliability:** Identify and address edge cases, unexpected failures, and inconsistencies across the complete SmartFit workflow.
* 📝 **Hardening Scope:** This milestone focuses on strengthening the existing SmartFit prototype rather than introducing major new functionality. The objective is to improve security, reliability, validation, testing, and overall system robustness before the final release.

</details>

<details>

<summary><b>📦 Milestone 10 — Release Engineering & Version Release (✅ Complete)</b></summary>

* ✅ **Release Preparation:** Prepare the SmartFit application for reproducible installation and distribution as a final project release.
* 🐳 **Docker Deployment:** Finalize Docker and Docker Compose configuration for running the complete SmartFit stack, including the React frontend, FastAPI backend, and PostgreSQL database.
* 🗄️ **Database Initialization:** Automate creation and initialization of the SmartFit development and test databases during Docker setup.
* 🪟 **Windows Installer:** Complete and validate the Windows installation process, including Python, PostgreSQL, Node.js, project dependencies, database configuration, environment setup, and application verification.
* 🐧 **Linux Installer:** Prepare and validate the Linux installation process for supported development environments.
* ⚙️ **Environment Configuration:** Ensure required configuration files, environment variables, bundled models, database credentials, and runtime dependencies are correctly prepared during installation.
* 🧪 **Clean-Environment Testing:** Test the release from a clean developer environment to verify that SmartFit can be installed and started without relying on previously configured local development dependencies.
* 🔍 **Release Verification:** Execute the automated backend test suite and perform end-to-end verification of authentication, video processing, body measurement, avatar generation, garment management, and virtual fitting workflows.
* 📋 **Documentation:** Finalize installation instructions, system requirements, configuration guidance, troubleshooting information, and developer setup documentation.
* 🏷️ **Versioned Release:** Produce the final SmartFit release package with a documented version number, release notes, and reproducible installation procedure.
* 📝 **Release Scope:** This milestone focuses on stabilizing, packaging, installing, and verifying the existing SmartFit prototype. Major new application functionality is not introduced unless required to resolve release-blocking defects.

</details>

<details>

<summary><b>🕶️ Milestone 11 — Visualization (⬜ Planned)</b></summary>

* ⬜ **3D Garment Overlay:** Rendering 3D garment overlays onto the user's generated digital avatar.
* ⬜ **Interactive Virtual Fitting Room:** Real-time fitting-room interface with garment visualization, style toggling, and interactive fit inspection.

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

<summary>⚙️ Backend</summary>

* **Language:** Python 3.12+
* **API Framework:** FastAPI
* **Database:** PostgreSQL 18
* **ORM:** SQLAlchemy
* **Configuration:** Pydantic Settings and environment-based configuration
* **Authentication:** Passlib (`bcrypt`) and PyJWT
* **Computer Vision:** OpenCV
* **Pose Estimation:** MediaPipe Pose Landmarker
* **Background Processing:** FastAPI `BackgroundTasks`
* **API Testing:** Pytest

</details>

<details>

<summary>💻 Frontend</summary>

* **Core:** React 19, Vite 8
* **Routing:** React Router 7
* **3D Visualization:** Three.js, React Three Fiber (`@react-three/fiber`), and Drei (`@react-three/drei`)
* **3D Model Format:** GLB / glTF
* **Styling:** CSS3 with modern Flexbox/Grid layouts and CSS variables for light/dark themes
* **Networking:** Fetch API with a centralized HTTP client wrapper
* **Authentication:** JWT Bearer token handling and protected route management
* **File Handling:** Multipart video uploads and Blob-based 3D model retrieval

</details>

<details>

<summary>🐳 Containerization & Deployment</summary>

* **Container Platform:** Docker
* **Container Orchestration:** Docker Compose
* **Backend Container:** Python/FastAPI application container
* **Frontend Container:** React/Vite application container
* **Database Container:** PostgreSQL 18 container
* **Database Initialization:** PostgreSQL initialization scripts for automatic database creation
* **Persistent Storage:** Docker named volumes for PostgreSQL data and application uploads
* **Service Networking:** Docker Compose service-to-service networking
* **Environment Configuration:** Docker Compose environment variables and application configuration files

</details>

<details>

<summary>🧪 Testing & Quality Assurance</summary>

* **Backend Testing:** Pytest automated test suite
* **API Testing:** FastAPI endpoint and integration testing
* **Release Testing:** Clean-environment installation and application verification for Docker

</details>

<details>

<summary>🛠️ Development & Build Tools</summary>

* **Version Control:** Git
* **Backend Environment:** Python virtual environments (`venv`)
* **Frontend Package Management:** npm
* **Backend Dependency Management:** `pip` and `requirements.txt`
* **Frontend Build System:** Vite
* **Container Build System:** Dockerfiles and Docker Compose
* **Documentation:** Markdown
* **API Documentation:** OpenAPI / FastAPI Swagger UI

</details>

<details>

<summary>📦 Installation & Release</summary>

* **Container Platform:** Docker and Docker Compose

* **Application Services:** Containerized React frontend, FastAPI backend, and PostgreSQL database.

* **Database Initialization:** Automatic creation of the SmartFit development and test databases during first-time PostgreSQL initialization.

* **Persistent Storage:** Docker named volumes for PostgreSQL data and SmartFit application uploads.

</details>


---



## 📁 Project Structure

<details>

<summary><b>⚙️ Backend</b></summary>

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── avatars.py
│   │   │   ├── garments.py
│   │   │   ├── users.py
│   │   │   ├── videos.py
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
│   ├── test_garment_schema.py
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

The `backend/` directory contains the FastAPI application, database layer, SQLAlchemy models, Pydantic schemas, business services, computer-vision processing, database utilities, and automated tests. The bundled MediaPipe Pose Landmarker model is stored under `backend/models/`.

</details>

<details>

<summary><b>💻 Frontend</b></summary>

```text
frontend/
├── public/
│   ├── favicon.svg
│   ├── icons.svg
│   └── smartfit-logo.svg
│
├── scripts/
│   ├── css-review/
│   ├── extract-css.ps1
│   ├── README.md
│   └── replace-css.ps1
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

The `frontend/` directory contains the React/Vite application, reusable components, authentication context, application pages, API service modules, styling, and frontend development utilities.

</details>

<details>

<summary><b>🐳 Docker & Container Configuration</b></summary>

```text
docker/
├── backend/
│   └── Dockerfile
│
├── frontend/
│   └── Dockerfile
│
└── postgres/
    └── init/
        └── 01-create-test-database.sql

docker-compose.yml
.dockerignore
```

The `docker/` directory contains the Docker build definitions and PostgreSQL initialization configuration used by the containerized SmartFit development environment.

* `docker/backend/Dockerfile` — Builds the FastAPI backend container.
* `docker/frontend/Dockerfile` — Builds the React/Vite frontend container.
* `docker/postgres/init/01-create-test-database.sql` — Creates the dedicated SmartFit test database during first-time PostgreSQL initialization.
* `docker-compose.yml` — Defines and orchestrates the frontend, backend, and PostgreSQL services.
* `.dockerignore` — Controls which project files are excluded from Docker build contexts.

</details>

<details>

<summary><b>🛠️ Installation & Release</b></summary>

```text
installer/
├── linux/
│   └── modules/
│       ├── backend.sh
│       ├── frontend.sh
│       ├── logging.sh
│       ├── postgresql.sh
│       ├── python.sh
│       └── verification.sh
│
└── windows/
    └── modules/
        ├── Backend.ps1
        ├── Frontend.ps1
        ├── Logging.ps1
        ├── PostgreSQL.ps1
        ├── Python.ps1
        └── Verification.ps1

setup.ps1
setup.sh
```

The `installer/` directory contains the modular native installation workflows for Windows and Linux. The root-level `setup.ps1` and `setup.sh` provide the corresponding installer entry points.

For the current Docker-based release workflow, `docker-compose.yml` provides the primary containerized application setup.

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
│   ├── 2_4_integration_and_architecture/
│   ├── 3_6_system_specification/
│   ├── 3_7_1_1_use_case_diagrams/
│   ├── 3_7_4_activity_diagram/
│   ├── 3_7_5_sequence_diagrams/
│   ├── 3_8_logical_design/
│   └── 3_9_1_database_design/
│
├── Official SmartFit Documentation.docx
└── Official SmartFit Documentation.pdf
```

The `docs/` directory contains the project's formal documentation, user-interface design references, UML diagrams, PlantUML source files, and generated diagram images. PlantUML (`.puml`) source files are retained alongside their corresponding `.png` diagrams so that diagrams can be regenerated or modified when required.

</details>

<details>

<summary><b>📄 Root Configuration & Project Files</b></summary>

```text
SmartFit/
├── backend/
├── docker/
├── docs/
├── frontend/
├── installer/
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── README.md
├── setup.ps1
└── setup.sh
```

The project root contains the primary Docker Compose configuration, installation entry points, repository configuration files, and the main SmartFit documentation.

</details>

---

## ⚡ Quick Start Guide

> **⚠️ Important — SmartFit v0.0.1 Installation**
>
> The native **Windows (`setup.ps1`)** and **Linux (`setup.sh`)** installers are currently under development and **are not supported installation methods for v0.0.1**.
>
> For the current release, SmartFit should be installed and run using **Docker and Docker Compose**.

<details>
<summary><b>1️⃣ Docker Installation</b></summary>

Before starting, install:

* **Docker Desktop** on Windows or macOS
* **Docker Engine and Docker Compose** on Linux

Verify that Docker is available:

```bash
docker --version
docker compose version
```

</details>

<details>
<summary><b>2️⃣ Clone the Repository</b></summary>

Clone the SmartFit repository and enter the project directory:

```bash
git clone <repository-url>
cd SmartFit
```

</details>

<details>
<summary><b>3️⃣ Start SmartFit</b></summary>

From the SmartFit root directory, run:

```bash
docker compose up --build
```

Docker Compose automatically:

1. Builds the SmartFit frontend image.
2. Builds the SmartFit FastAPI backend image.
3. Creates the PostgreSQL container.
4. Initializes the SmartFit PostgreSQL databases.
5. Creates the required Docker volumes.
6. Starts the backend API.
7. Starts the React frontend.
8. Connects the application services through the Docker network.

Once the containers have started:

* **🌐 SmartFit Frontend:** `http://localhost:5173`
* **⚡ SmartFit API:** `http://localhost:8000`
* **📚 API Documentation:** `http://localhost:8000/docs`

</details>

<details>
<summary><b>4️⃣ Verify Running Containers</b></summary>

In another terminal, run:

```bash
docker compose ps
```

The SmartFit services should be running:

```text
smartfit-frontend
smartfit-backend
smartfit-db
```

To view all service logs:

```bash
docker compose logs
```

To view a specific service:

```bash
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

</details>

<details>
<summary><b>5️⃣ Stop SmartFit</b></summary>

To stop the application:

```bash
docker compose down
```

This stops and removes the containers while preserving persistent Docker volumes.

</details>

<details>
<summary><b>6️⃣ Rebuild SmartFit</b></summary>

If project dependencies or Docker configuration change, rebuild the containers:

```bash
docker compose up --build
```

For a completely clean Docker rebuild:

```bash
docker compose build --no-cache
docker compose up
```

</details>

<details>
<summary><b>7️⃣ SmartFit Docker Environment</b></summary>

The Docker Compose configuration provides the complete SmartFit development environment:

```text
┌───────────────────────────────────────────────┐
│                 SmartFit                      │
│                                               │
│  ┌─────────────┐      ┌──────────────────┐   │
│  │  Frontend   │ ───► │     Backend      │   │
│  │ React/Vite  │      │ FastAPI/Python   │   │
│  │ :5173       │      │ :8000            │   │
│  └─────────────┘      └────────┬─────────┘   │
│                                │              │
│                                ▼              │
│                       ┌──────────────────┐    │
│                       │   PostgreSQL 18  │    │
│                       │      :5432       │    │
│                       └──────────────────┘    │
└───────────────────────────────────────────────┘
```

When running SmartFit through Docker, a local Python virtual environment, PostgreSQL installation, or Node.js installation is **not required**.

</details>

<details>
<summary><b>⚠️ Native Installers — Currently Unsupported</b></summary>

The repository contains native installation scripts for Windows and Linux:

```text
installer/
├── linux/
│   └── modules/
└── windows/
    └── modules/

setup.ps1
setup.sh
```

These installers are **currently not working and should not be used to install SmartFit v0.0.1**.

They are retained as part of the project's ongoing release-engineering work and may be completed in a future release.

**For SmartFit v0.0.1, Docker Compose is the supported installation method.**

</details>

<details>
<summary><b>🛠️ Troubleshooting</b></summary>

If SmartFit does not start correctly, first check the container status:

```bash
docker compose ps
```

Then inspect the service logs:

```bash
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

To recreate the containers:

```bash
docker compose down
docker compose up --build
```

> **💡 Tip:** Always run Docker Compose commands from the **SmartFit project root**, where `docker-compose.yml` is located.

</details>


---
## 🔌API Endpoints
<details>
<summary><b>Current API Endpoints</b></summary>

| Method   | Endpoint                             | Auth Required | Role / Description                                                        |
| -------- | ------------------------------------ | ------------- | ------------------------------------------------------------------------- |
| `GET`    | `/`                                  | No            | Health check and API status endpoint                                      |
| `POST`   | `/api/users/`                        | No            | Register a new user                                                       |
| `POST`   | `/api/users/login`                   | No            | Authenticate user and issue JWT                                           |
| `GET`    | `/api/users/me`                      | Yes           | Retrieve the logged-in user's profile                                     |
| `POST`   | `/api/videos/`                       | Yes           | Upload a body video with height metadata (Customer)                       |
| `GET`    | `/api/videos/{video_id}`             | Yes           | Retrieve video processing status and body measurements (Customer)         |
| `DELETE` | `/api/videos/{video_id}`             | Yes           | Delete a user's uploaded body video (Customer)                            |
| `POST`   | `/api/avatars/`                      | Yes           | Generate a personalized avatar from body measurement data (Customer)      |
| `GET`    | `/api/avatars/me`                    | Yes           | Retrieve the logged-in user's generated avatar (Customer)                 |
| `GET`    | `/api/avatars/{avatar_id}/file`      | Yes           | Retrieve the authenticated user's avatar GLB model file (Customer)        |
| `POST`   | `/api/garments/`                     | Yes           | Register a new garment with measurements (Retailer)                       |
| `GET`    | `/api/garments/`                     | Yes           | List garments owned by the authenticated retailer (Retailer)              |
| `GET`    | `/api/garments/available`            | Yes           | Retrieve garments available for customer virtual fitting                  |
| `GET`    | `/api/garments/{garment_id}`         | Yes           | Retrieve a specific garment (Retailer)                                    |
| `PUT`    | `/api/garments/{garment_id}`         | Yes           | Update garment details and measurements (Retailer)                        |
| `DELETE` | `/api/garments/{garment_id}`         | Yes           | Delete a retailer's garment (Retailer)                                    |
| `POST`   | `/api/virtual-fittings/`             | Yes           | Create a virtual fitting using a garment and generated avatar (Customer)  |
| `GET`    | `/api/virtual-fittings/{fitting_id}` | Yes           | Retrieve a virtual fitting result belonging to the authenticated customer |

</details>


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