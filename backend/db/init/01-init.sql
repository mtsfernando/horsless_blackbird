-- Initialize the horseless database.
-- This script is used by the Docker PostgreSQL container on first start.

SELECT 'CREATE DATABASE horseless'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'horseless')\gexec
