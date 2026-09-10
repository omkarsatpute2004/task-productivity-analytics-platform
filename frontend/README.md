# Task Management & Productivity Analytics Platform — React Frontend

This directory contains the production-ready React 18, TypeScript, Tailwind CSS, Vite, and Recharts frontend for the **Task Management & Productivity Analytics Platform**.

---

## 🛠️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3.4
- **Routing**: React Router DOM 6
- **Data Visualization**: Recharts 2.12
- **Form Validation**: React Hook Form + Zod
- **HTTP Client**: Axios with Request & Response Interceptors
- **Iconography**: Lucide React
- **Testing**: Vitest + React Testing Library + JSDOM

---

## 📁 Directory Architecture

```text
frontend/
├── src/
│   ├── components/
│   │   ├── analytics/     # Recharts charts, KPI cards, and filter controls
│   │   ├── common/        # Toast, Modal, Spinner, Skeleton, Badge, Pagination, EmptyState
│   │   ├── layout/        # Sidebar, TopBar, Layout shell
│   │   └── tasks/         # TaskTable, TaskFilters, TaskForm, TaskActivityTimeline
│   │
│   ├── context/           # AuthContext provider
│   ├── hooks/             # useAuth hook
│   ├── pages/             # Login, Register, Dashboard, Tasks, TaskDetails, CreateTask, EditTask, Analytics, Users, Categories, Profile
│   ├── routes/            # AppRoutes & ProtectedRoute (RBAC)
│   ├── services/          # Centralized Axios API services (api, authApi, taskApi, userApi, categoryApi, analyticsApi)
│   ├── tests/             # Vitest test suite
│   ├── types/             # TypeScript interfaces for models & analytics schemas
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
│
├── .env.example
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

---

## 🚀 Setup & Execution

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure `VITE_API_BASE_URL` points to the running FastAPI backend (e.g. `http://127.0.0.1:8000`).

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Development Server
```bash
npm run dev
```
The application will launch on `http://localhost:3000`.

### 4. Run Frontend Unit & Integration Tests
```bash
npm test
```

### 5. Build for Production
```bash
npm run build
```
Creates an optimized production bundle in `dist/`.
