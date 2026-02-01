# CreditScan Architecture

CreditScan is a self-hosted personal finance application for managing multiple credit cards. It allows users to upload credit card statements (PDF), automatically extract transactions, and provides a unified dashboard for tracking expenses, payments, and financial analytics.

## Project Overview

**Problem:** Managing multiple credit cards from different banks is complex due to varying formats, dates, and tracking requirements.

**Solution:** A unified platform that:
- Processes PDF credit card statements automatically
- Centralizes transaction tracking across all cards
- Provides payment reminders and due date alerts
- Offers financial analytics and spending insights
- Can be self-hosted for maximum privacy

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Vue 3 (Composition API), Vite, TypeScript |
| **UI Framework** | PrimeVue with Aura theme |
| **State Management** | Pinia + TanStack Vue Query |
| **Backend** | FastAPI (Python) |
| **ORM** | SQLModel (SQLAlchemy + Pydantic) |
| **Database** | PostgreSQL |
| **Migrations** | Alembic |
| **Auth** | JWT with OAuth2 Bearer tokens |
| **Containerization** | Docker |

---

## Repository Structure

```
app-ai/
├── frontend/                 # Vue 3 SPA
│   ├── src/
│   │   ├── api/             # Auto-generated API SDK (OpenAPI)
│   │   ├── components/      # Reusable Vue components
│   │   ├── composables/     # Vue composables (hooks)
│   │   ├── layouts/         # Page layouts (Default, Auth)
│   │   ├── stores/          # Pinia state stores
│   │   ├── views/           # Page components
│   │   └── router/          # Vue Router config
│   └── ...
│
├── backend/                  # FastAPI server
│   ├── app/
│   │   ├── api/             # HTTP layer (routes, deps)
│   │   ├── core/            # Config, DB, security
│   │   ├── domains/         # Domain-driven modules
│   │   ├── pkgs/            # Shared utilities
│   │   └── services/        # Global services
│   └── ...
│
└── ARCH.md                   # This file
```

---

## Backend Architecture

The backend follows **Domain-Driven Design (DDD)** with a layered architecture.

### Domain Structure

Each domain has a consistent 4-layer structure:

```
domains/{domain_name}/
├── domain/                   # Business logic layer
│   ├── models.py            # SQLModel entities (Base, Create, Update, Public)
│   ├── errors.py            # Domain-specific exceptions
│   └── options.py           # Search/filter options with pagination
├── repository/              # Data access layer
│   └── {domain}_repository.py
├── service/                 # Business orchestration
│   └── {domain}_service.py
└── usecases/                # Application features
    ├── list_{items}/
    ├── create_{item}/
    ├── get_{item}/
    ├── update_{item}/
    └── delete_{item}/
```

### Implemented Domains

| Domain | Description |
|--------|-------------|
| `users` | User accounts, authentication, balance calculation |
| `credit_cards` | Credit card records (bank, brand, last4) |
| `card_statements` | Monthly statements with balances and due dates |
| `transactions` | Individual transactions with installment support |
| `payments` | Payment records against statements |
| `tags` | User-defined transaction categories |
| `transaction_tags` | Tag-transaction associations |

### Dependency Flow

```
API Layer (FastAPI routes)
    ↓
UseCase Layer (Application features)
    ↓
Service Layer (Business orchestration)
    ↓
Repository Layer (Database CRUD)
    ↓
Domain Layer (Models, errors)
```

### Database Models

**Core Entities:**

- **User**: id, email, hashed_password, is_active, is_superuser, full_name
- **CreditCard**: id, user_id, bank, brand (VISA/MASTERCARD/AMEX/DISCOVER/OTHER), last4
- **CardStatement**: id, card_id, period_start/end, close_date, due_date, previous_balance, current_balance, minimum_payment, is_fully_paid
- **Transaction**: id, statement_id, txn_date, payee, description, amount, currency, coupon, installment_cur, installment_tot
- **Payment**: id, user_id, statement_id, amount, payment_date, currency
- **Tag**: tag_id, user_id, label, created_at

### API Endpoints

All endpoints are prefixed with `/api/v1/`:

| Route | Description |
|-------|-------------|
| `/login` | Authentication (OAuth2 password flow) |
| `/users` | User management (register, profile, password) |
| `/credit-cards` | Credit card CRUD |
| `/card-statements` | Statement management |
| `/payments` | Payment tracking |
| `/transactions` | Transaction CRUD |
| `/tags` | Tag management |
| `/transaction-tags` | Tag associations |

---

## Frontend Architecture

### Folder Structure

```
src/
├── api/                      # Auto-generated from OpenAPI
│   ├── core/                # Request handling, config
│   ├── sdk.gen.ts          # Generated services
│   └── types.gen.ts        # Generated types
│
├── components/              # Reusable components
│   ├── dashboard/          # Dashboard UI (MetricCard, StatusBadge, etc.)
│   ├── PaymentModal.vue    # Payment processing
│   └── icons/              # Icon components
│
├── composables/            # Vue composables
│   ├── useAuth.ts          # Authentication logic
│   ├── useStatements.ts    # Statements & balance
│   ├── useCreditCards.ts   # Credit card operations
│   ├── useTransactions.ts  # Transaction handling
│   └── useToast.ts         # Notifications
│
├── layouts/
│   ├── DefaultLayout.vue   # Authenticated layout (header, nav)
│   └── AuthLayout.vue      # Login/signup layout
│
├── stores/
│   └── auth.ts             # Authentication state (Pinia)
│
├── views/                   # Page components
│   ├── StatementsView.vue  # Main dashboard
│   ├── TransactionsView.vue
│   ├── AnalyticsView.vue
│   ├── LoginView.vue
│   └── SignUpView.vue
│
└── router/index.ts          # Route definitions
```

### State Management

**Pinia Store (`auth.ts`):**
- Token management (localStorage/sessionStorage based on "remember me")
- User profile state
- Login/logout/register actions
- Auto-fetch user on initialization

**TanStack Vue Query:**
- Data fetching with caching
- Automatic refetching
- Loading/error states

### Routes

| Path | View | Auth Required |
|------|------|---------------|
| `/` | StatementsView (Dashboard) | Yes |
| `/transactions` | TransactionsView | Yes |
| `/analytics` | AnalyticsView | Yes |
| `/auth/login` | LoginView | No (guest only) |
| `/auth/signup` | SignUpView | No (guest only) |

### Key Features

- **Dashboard**: Metrics grid, statements table, cards grid, transactions list
- **Tab Navigation**: Statements, Cards, Analytics, Transactions
- **Payment Modal**: Full/partial payments, date selection, currency support
- **Dark Mode**: CSS class-based toggle
- **Responsive Design**: Mobile-first approach

---

## Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Backend Setup

```bash
cd backend
uv sync                      # Install dependencies
cp .env.example .env         # Configure environment
alembic upgrade head         # Run migrations
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env         # Set VITE_API_URL
npm run dev
```

### Environment Variables

**Backend (.env):**
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=creditscan
SECRET_KEY=your-secret-key
```

**Frontend (.env):**
```
VITE_API_URL=http://localhost:8000
```

---

## Adding New Features

### Adding a New Domain (Backend)

See `backend/DOMAIN_ARCHITECTURE_GUIDE.md` for detailed steps:

1. Create domain folder structure
2. Define models (Base, Create, Update, Public)
3. Create repository with CRUD operations
4. Implement service layer
5. Build usecases
6. Create API routes
7. Register in main router

### Adding a New View (Frontend)

1. Create view component in `src/views/`
2. Add composable for data fetching in `src/composables/`
3. Register route in `src/router/index.ts`
4. Add navigation link in layout

---

## Deployment

Both services have Dockerfiles for containerized deployment:

```bash
# Backend
docker build -t creditscan-backend ./backend
docker run -p 8000:8000 creditscan-backend

# Frontend
docker build -t creditscan-frontend ./frontend
docker run -p 80:80 creditscan-frontend
```

For production, use docker-compose or Kubernetes with:
- PostgreSQL database
- Reverse proxy (nginx/traefik)
- SSL/TLS termination
- Environment-specific configuration
