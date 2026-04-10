# AGENTS.md

## Project
Rebound Cloud Control

## Current Phase
Phase 1: Prototype Validation (Extended with Multi-machine Management)

## Goal
Build a runnable single-machine prototype for a steel pipe springback compensation web system with multi-machine management support.

## In Scope
- Web page basic framework
- Parameter input
- Recommendation display
- Device status display
- Frontend-backend integration
- Single-machine demo with simulator
- Multi-machine management (NEW)
- User authentication system (NEW)
  - Machine login (direct access to machine control)
  - User login (admin/maintenance/operator roles)
- Machine selection for user login

## Out of Scope
- Real PLC integration
- Real MQTT integration
- Production deployment
- Real AI model training
- Advanced permission management
- User management UI (basic support ready)

## Stack
Frontend:
- Vue 3
- Vite
- TypeScript
- Vue Router
- Pinia
- ECharts

Backend:
- Python
- FastAPI
- Pydantic

## API Shape
All responses should use:
{
  "code": 0,
  "message": "success",
  "data": {}
}

## Authentication
Two login modes supported:
1. **Machine Login**: Direct access with machine ID
2. **User Login**: Username/password with roles (admin/maintenance/operator)

Default users:
- admin / admin123 (Administrator)
- maintenance / maint123 (Maintenance staff)
- operator / oper123 (Operator)

## Data Storage
- Each machine has isolated storage in `data/machines/{machine_id}/`
- Machine info: `machine.json`
- History records: `history.json`
- Users: `data/users.json`

## Development Principles
- Keep implementation minimal and runnable
- Favor clarity over complexity
- Use mock data or simulator when real hardware is unavailable
- Write code that can be demoed locally
- Update README when adding runnable features

## Priority Order
1. Backend API runnable ✅
2. Frontend pages runnable ✅
3. Frontend-backend integration ✅
4. Device simulator ✅
5. Multi-machine management ✅
6. Authentication system ✅
7. Demo flow polish
