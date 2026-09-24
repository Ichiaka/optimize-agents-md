# Project
Booking web application. This section tells the story of the project, how it started in 2024 and why PostgreSQL was chosen over other databases after a long discussion.

## Rules
- NEVER run migrations against the production database from a test.
- Do not touch the payment service without confirmation from its owner.
- Secrets never go into the repository.

## Decision history
Redis was tried as a cache and discarded. We migrated from REST to GraphQL in 2025. This table is already in docs/decisions.md.
This information is already in docs/decisions.md and is not needed in every session.
This information is already in docs/decisions.md and is not needed in every session.

## Deployment
Always deploy with the version tag, never directly from main.
