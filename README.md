# FlowBiz AI Builder Client Service

> ⚠️ **CRITICAL: MANDATORY PRE-DEPLOYMENT READING**  
> Before deploying this project to a shared FlowBiz VPS, you MUST read:  
> - [docs/ADR_SYSTEM_NGINX.md](docs/ADR_SYSTEM_NGINX.md) - System architecture (WHY nginx is external)
> - [docs/AGENT_NEW_PROJECT_CHECKLIST.md](docs/AGENT_NEW_PROJECT_CHECKLIST.md) - Complete deployment checklist
> - [docs/AGENT_BEHAVIOR_LOCK.md](docs/AGENT_BEHAVIOR_LOCK.md) - Strict deployment rules
>   
> **IF ANY CHECKLIST ITEM IS "NO" → DEPLOYMENT IS FORBIDDEN**  
> Deploying without reading these documents violates project rules.

**Related:** See [natbkgift/flowbiz-ai-core](https://github.com/natbkgift/flowbiz-ai-core) for VPS infrastructure documentation.

[![CI](https://github.com/natbkgift/flowbiz-client-ai-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/natbkgift/flowbiz-client-ai-builder/actions/workflows/ci.yml)

Client service for FlowBiz AI Builder that integrates with FlowBiz AI Core system. Built from the FlowBiz Template Service baseline with Core integration capabilities.

## 🎯 Purpose

This service provides:
- **Core Integration**: Contract-first integration with FlowBiz AI Core
- **Workflow Operations**: Build and validate AI workflows
- **Mock-First Design**: Develop and test without Core system dependency
- **Standard API Contracts**: Health checks, metadata, and Core operations
- **Docker Containerization**: Production-ready deployment
- **CI/CD Pipeline**: Automated testing and policy enforcement
- **Configuration-Driven**: Switch between mock and real Core via environment

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Development

```bash
# Clone repository
git clone https://github.com/natbkgift/flowbiz-client-ai-builder.git
cd flowbiz-client-ai-builder

# Start services (binds to localhost:8000)
docker compose up --build

# Verify services
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/v1/meta
curl http://127.0.0.1:8000/v1/core/health
```

### Local Python Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Run application
python apps/api/main.py

# Run tests
pytest -q

# Run linting
ruff check .
```

## 📋 API Endpoints

### Standard Endpoints

#### `GET /healthz`
Service health check for monitoring.

**Response:**
```json
{
  "status": "ok",
  "service": "flowbiz-template-service",
  "version": "0.1.0"
}
```

#### `GET /v1/meta`
Service metadata and environment information.

**Response:**
```json
{
  "service": "flowbiz-template-service",
  "environment": "dev",
  "version": "0.1.0",
  "build_sha": "abc123"
}
```

### Core Integration Endpoints

#### `GET /v1/core/health`
Check FlowBiz AI Core service health and connection status.

**Response:**
```json
{
  "healthy": true,
  "mode": "mock",
  "service": "flowbiz-ai-core"
}
```

#### `POST /v1/core/build`
Build a workflow in the Core system.

**Request:**
```json
{
  "project_id": "my-project-123",
  "workflow_spec": {
    "nodes": [
      {"id": "1", "type": "start"},
      {"id": "2", "type": "process"}
    ],
    "edges": [
      {"from": "1", "to": "2"}
    ]
  },
  "options": {
    "timeout": 300
  }
}
```

**Response:**
```json
{
  "build_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "message": "Build completed for project my-project-123",
  "artifacts": {
    "workflow_id": "660e8400-e29b-41d4-a716-446655440001",
    "deployment_url": "https://core.example.com/workflow/660e8400..."
  }
}
```

#### `POST /v1/core/validate`
Validate a workflow specification before building.

**Request:**
```json
{
  "workflow_spec": {
    "nodes": [
      {"id": "1", "type": "start"}
    ],
    "edges": []
  }
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "No edges defined in workflow"
  ]
}
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

**Runtime (APP_*)**
- `APP_ENV`: Environment (`dev`|`prod`)
- `APP_HOST`: Bind host (default: `127.0.0.1`) ⚠️ MUST be localhost for VPS
- `APP_PORT`: Bind port (default: `8000`)
- `APP_LOG_LEVEL`: Log level (default: `info`)

**Metadata (FLOWBIZ_*)**
- `FLOWBIZ_SERVICE_NAME`: Service identifier
- `FLOWBIZ_VERSION`: Semantic version
- `FLOWBIZ_BUILD_SHA`: Git commit SHA

**Core Integration (CORE_*)**
- `CORE_SERVICE_MODE`: Integration mode (`mock`|`real`)
  - `mock`: Use mock adapter for development/testing (default)
  - `real`: Connect to real FlowBiz AI Core system
- `CORE_SERVICE_URL`: Core service URL (required when `mode=real`)
  - Example: `https://core.flowbiz.example.com`

### Core Integration Modes

#### Mock Mode (Development)
```bash
CORE_SERVICE_MODE=mock
```
- ✅ No external dependencies
- ✅ Fast testing and development
- ✅ Predictable responses
- ✅ Configurable failure simulation

#### Real Mode (Production)
```bash
CORE_SERVICE_MODE=real
CORE_SERVICE_URL=https://core.flowbiz.example.com
```
- ⚠️ Requires live Core system
- ⚠️ Network connectivity required
- ⚠️ Authentication may be required (future)

## 🐳 Docker

### Development
```bash
docker compose up --build
```

### Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Verify local access (service binds to localhost only)
curl http://127.0.0.1:8000/healthz
```

**⚠️ Important:** 
- Service binds to `127.0.0.1` (localhost) only
- NO nginx included in docker-compose (managed by system-level nginx)
- See [docs/ADR_SYSTEM_NGINX.md](docs/ADR_SYSTEM_NGINX.md) for architecture
- Public HTTPS access configured by infrastructure team

## 🏗️ Architecture

### Core Integration Design

This service follows a **contract-first, adapter-based** integration pattern:

```
Client Service (AI Builder)
  ↓
API Layer (FastAPI routes)
  ├─ /v1/core/build
  ├─ /v1/core/validate
  └─ /v1/core/health
     ↓
Gateway Layer (CoreServiceGateway)
  └─ Selects adapter based on CORE_SERVICE_MODE
     ↓
Adapter Layer
  ├─ MockCoreService (mock mode)
  └─ RealCoreService (real mode - future)
     ↓
Contract Layer (ICoreService interface)
  ├─ BuildRequest/Response
  ├─ ValidationRequest/Response
  └─ Health check interface
     ↓
FlowBiz AI Core System (external)
```

**Key Benefits:**
- ✅ **Mock-first**: Develop and test without Core system
- ✅ **Testable**: Full test coverage with no external dependencies
- ✅ **Switchable**: Toggle between mock and real via configuration
- ✅ **Contract-driven**: Interface ensures compatibility
- ✅ **Replaceable**: Easy to swap implementations

### Project Structure

```
flowbiz-client-ai-builder/
├── apps/
│   └── api/              # FastAPI application
│       ├── main.py       # App entry point
│       └── routes/       # API endpoints
│           ├── health.py
│           └── v1/
│               ├── meta.py
│               └── core.py  # Core integration endpoints
├── packages/
│   └── core/             # Core integration logic
│       ├── config.py     # Settings management
│       ├── contracts.py  # Interface definitions
│       ├── gateway.py    # Adapter factory
│       └── adapters/     # Service implementations
│           └── mock.py   # Mock adapter
├── tests/                # Test suite
│   ├── test_health.py
│   ├── test_meta.py
│   ├── test_core_integration.py    # Unit tests
│   └── test_core_endpoints.py      # API tests
└── docs/                 # Documentation
```

## 🧪 Testing

All tests are deterministic with no external dependencies (31 tests total).

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=apps --cov=packages

# Run specific test suites
pytest tests/test_core_integration.py -v  # Core logic tests
pytest tests/test_core_endpoints.py -v     # API endpoint tests
pytest tests/test_health.py -v             # Health check tests
```

## 🔒 Security

### VPS Architecture
- Services bind to **localhost (127.0.0.1) only**
- System-level nginx handles public routing and SSL
- No nginx in docker-compose (see [ADR_SYSTEM_NGINX.md](docs/ADR_SYSTEM_NGINX.md))

### Security Headers (Managed by System Nginx)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security` (production with SSL)

### Best Practices
- No secrets in code or environment files
- Non-root container user
- Minimal base images
- Regular dependency updates

## 📚 Documentation

- **[ADR: System Nginx](docs/ADR_SYSTEM_NGINX.md)** - ⚠️ MANDATORY - VPS architecture overview
- **[New Project Checklist](docs/AGENT_NEW_PROJECT_CHECKLIST.md)** - ⚠️ MANDATORY - Pre-deployment verification
- **[Agent Behavior Lock](docs/AGENT_BEHAVIOR_LOCK.md)** - ⚠️ MANDATORY - Deployment rules and constraints
- [Project Contract](docs/PROJECT_CONTRACT.md) - API contracts and conventions
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment steps
- [Guardrails](docs/GUARDRAILS.md) - CI/CD philosophy and rules
- [Pre-flight Checklist](docs/CODEX_PREFLIGHT.md) - Pre-merge verification

## 🛡️ Guardrails

This project uses **Blueprint-enforced** CI guardrails:
- **Linting**: `ruff` for code quality
- **Testing**: `pytest` with 100% pass requirement
- **Policy Check**: PR must include [BA], [QA], [SRE], [DEV] sections
- **Scope Validation**: Changes must align with Blueprint milestones
- **Security Scanning**: CodeQL and dependency checks

See [BLUEPRINT.md](BLUEPRINT.md) for complete policy details.

## 🚫 Scope Boundaries

### ✅ In Scope
- **Core Integration**: Contract-first design with mock/real modes
- **Workflow Operations**: Build and validate AI workflows
- **Standard Endpoints**: Health checks and metadata
- **Docker Containerization**: Service-only deployment
- **Localhost Binding**: 127.0.0.1 for security
- **Configuration Management**: Environment-based settings
- **CI/CD Pipeline**: Automated testing and deployment
- **Mock-First Development**: Independent testing capability

### ❌ Out of Scope
- Nginx configuration (managed by system-level nginx)
- SSL/TLS certificates (managed by infrastructure)
- Public port exposure (services bind to localhost only)
- Real Core implementation (future phase)
- Authentication/Authorization (future phase)
- Database integrations (future phase)
- Queue/Worker systems (not required)
- UI/Frontend code (separate service)
- FlowBiz Core runtime (external system)
- Environment configuration
- CI/CD infrastructure

### ❌ Out of Scope
- Nginx configuration (managed by system-level nginx)
- SSL/TLS certificates (managed by infrastructure)
- Public port exposure (services bind to localhost only)
- Business logic endpoints
- Authentication/Authorization
- Database integrations
- Queue/Worker systems
- UI/Frontend code
- FlowBiz Core runtime

**See [AGENT_BEHAVIOR_LOCK.md](docs/AGENT_BEHAVIOR_LOCK.md) and [BLUEPRINT.md](BLUEPRINT.md) for complete rules.**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following Blueprint conventions
4. Run tests (`pytest -q`) and linting (`ruff check .`)
5. Submit PR with [BA], [QA], [SRE], [DEV] sections completed
6. Apply appropriate persona labels (persona:core|infra|docs)
7. Ensure all CI checks pass

See [CODEX_PREFLIGHT.md](docs/CODEX_PREFLIGHT.md) and [BLUEPRINT.md](BLUEPRINT.md) for detailed guidelines.

## 📝 License

This service is maintained by the FlowBiz AI Core team.

## 🔗 Links

- [FlowBiz AI Core](https://github.com/natbkgift/flowbiz-ai-core)
- [FlowBiz Template Service](https://github.com/natbkgift/flowbiz-template-service)
- [Documentation](docs/)
- [Blueprint](BLUEPRINT.md)
- [Issues](https://github.com/natbkgift/flowbiz-client-ai-builder/issues)