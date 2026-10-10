# CertiFlow - Premium Bulk Certificate Generator SaaS

CertiFlow is a production-quality, enterprise-grade Bulk Certificate Generator. It features a high-performance Python FastAPI backend paired with a stunning, highly-interactive React frontend.

This project was built to demonstrate advanced software architecture, failure isolation, background task processing, real-time observability, and world-class UI/UX design.

---

## 🌟 Key Features

### 🎨 World-Class UI/UX
- **Premium Design System:** Dark-mode first aesthetics with elegant layouts, glassmorphic modals, and custom tailored variables (no raw Tailwind).
- **Interactive Wizards:** A seamless 3-step animated wizard for bulk job creation with client-side validation.
- **Micro-Interactions:** Powered by `framer-motion` for effortless transitions and live progress bars.
- **In-App PDF Previews:** Instantly view generated certificates inside a modal without downloading them blindly.

### ⚙️ Resilient Backend Architecture
- **Asynchronous Processing:** Long-running certificate generation tasks are immediately offloaded to FastAPI `BackgroundTasks`.
- **Failure Isolation:** If one recipient fails (e.g., bad data), the job continues generating the remaining certificates.
- **Alembic Migrations:** Version-controlled database schema management.
- **Data Validation:** Strict Pydantic V2 models ensure absolute data integrity.
- **Global Extraction:** A `.zip` compression endpoint allows downloading thousands of generated certificates instantly.

---

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI & Uvicorn**
- **SQLAlchemy 2.x & Alembic** (ORM and Migrations)
- **PostgreSQL / SQLite** (Configurable via `.env`)
- **ReportLab** (High-speed PDF Generation)
- **Pydantic v2** (Data Validation)
- **Pytest** (Automated Testing)

### Frontend
- **React 18 & Vite**
- **Framer Motion** (Animations)
- **Lucide React** (Iconography)
- **Recharts** (Dashboard Data Visualization)
- **PapaParse** (CSV parsing for bulk uploads)
- **Bootstrap 5** (Layout grid utility structure mapped to custom CSS)

---

## 🚀 How to Run Locally (Windows natively)

We have pre-configured the environment to run flawlessly using a local SQLite database for maximum convenience.

### 1. Start the Backend

1. Open a terminal and navigate to the project root.
2. Activate the virtual environment:
   ```powershell
   .\\venv\\Scripts\\activate
   ```
3. Run the database migrations (if not already done):
   ```powershell
   alembic upgrade head
   ```
4. Start the FastAPI Server:
   ```powershell
   uvicorn app.main:app --reload
   ```
*The backend API will now be running at `http://localhost:8000` (Swagger UI at `/docs`).*

### 2. Start the Frontend

1. Open a **second terminal** and navigate to the `frontend` folder:
   ```powershell
   cd frontend
   ```
2. Install dependencies (if you haven't yet):
   ```powershell
   npm install
   ```
3. Start the development server:
   ```powershell
   npm run dev
   ```
*The frontend application will now be running at `http://localhost:5173`.*

---

## 🏗️ Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── api/            # FastAPI Routers (Jobs, Certificates, Health)
│   ├── core/           # Configuration, Logging, Exceptions
│   ├── db/             # SQLAlchemy Session, Models
│   ├── repositories/   # Database Abstraction Layer
│   ├── schemas/        # Pydantic Input/Output Validation
│   ├── services/       # Core Business Logic (Job Processing, Generation)
│   ├── storage/        # File I/O Management
│   └── templates/      # Base PDF Templates
│
├── frontend/
│   ├── src/
│   │   ├── api/        # Axios API Client Configurations
│   │   ├── components/ # Reusable UI (Sidebar, Layouts)
│   │   ├── hooks/      # React Hooks (useTheme)
│   │   ├── pages/      # Route Components (Dashboard, CreateJob, etc.)
│   │   └── styles/     # global.css (Design System)
│   └── package.json
│
├── tests/              # Pytest Suite (Mock DB, End-to-end processing)
├── alembic/            # Database Migrations folder
└── .env                # Environment Variables
```

---

## 🧪 Testing

To ensure absolute reliability, the backend logic is covered by Pytest (including mocking background tasks and failure scenarios).

Run the tests using:
```powershell
.\\venv\\Scripts\\pytest
```

---

*Architected and developed with ❤️ for the ultimate Bulk Certificate Generator Evaluation.*
