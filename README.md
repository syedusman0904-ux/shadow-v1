# SHADOW
**Private. Secure. Connected.**

Shadow is a security-oriented messaging platform scaffold. This repository implements **Version 1** of the requested roadmap:

- Registration / login / logout
- Argon2id password hashing
- Access + rotating refresh sessions
- User profiles and username/user-ID search
- One-to-one conversations
- PostgreSQL
- Redis
- Authenticated WebSockets
- Message delivery/read acknowledgements
- Rate limiting hooks
- Security-oriented headers
- Automated tests
- Docker Compose

## Important security status

Version 1 is **not end-to-end encrypted**. Message text is stored by the backend in this first milestone so the messaging pipeline can be tested.

Do not advertise Version 1 as E2EE. Version 2 is reserved for integrating an established secure messaging protocol/library. Do not invent a cryptographic protocol.

## Quick start

1. Copy `.env.example` to `.env`.
2. Change all development secrets before any internet deployment.
3. Start services:

```bash
docker compose up --build
```

4. API documentation is available at the FastAPI development endpoint.

Run tests:

```bash
docker compose exec backend pytest -q
```

## Architecture

Client -> HTTPS/WebSocket -> FastAPI -> PostgreSQL
                           |
                           -> Redis

Redis is used for rate limiting and pub/sub-ready infrastructure.

## Production

Use a reverse proxy such as Nginx/Caddy/Traefik, TLS certificates, managed PostgreSQL, managed Redis, object storage for media, backups, monitoring, and secret management.

Before production E2EE claims, perform a threat model and independent security review.
