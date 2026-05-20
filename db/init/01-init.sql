-- Horseless Blackbird — Initial Database Setup
-- This runs automatically when the PostgreSQL container starts for the first time

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables are managed by Alembic migrations in the backend service.
-- This file only handles database-level setup that needs to run before the app starts.
