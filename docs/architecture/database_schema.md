# Database Schema and Security

LunarTech Deep RAG uses **Supabase** (PostgreSQL) as its primary backend for user authentication, workspace management, and persistent metadata storage. The vector/graph data is stored locally via LightRAG, while Supabase handles business logic boundaries.

## Core Tables

### 1. `documents`

Stores metadata about the PDFs and files uploaded by users.

- `id` (UUID, Primary Key)
- `filename` (Text)
- `page_count` (Integer)
- `chunk_count` (Integer)
- `created_at` (Timestamp)
- `user_id` (UUID, FK to `auth.users`)

### 2. `chat_history`

Stores the continuous conversation state, preventing token explosion by allowing selective history retrieval.

- `id` (UUID, Primary Key)
- `role` (Text - 'user' or 'ai')
- `content` (Text)
- `created_at` (Timestamp)
- `user_id` (UUID, FK to `auth.users`)

### 3. `user_roles`

A secure lookup table to define access levels for specific email addresses.

- `email` (Text, Primary Key)
- `role` (Text - e.g., 'admin')

## Row Level Security (RLS)

Security is paramount. The Supabase tables are secured using PostgreSQL's Row Level Security.

### Implementation

By default, all tables have RLS enabled preventing any reads or writes.
Policies are attached to the `documents` and `chat_history` tables enforcing that `auth.uid() = user_id`.

This means a user can mathematically only `SELECT`, `INSERT`, `UPDATE`, or `DELETE` rows that directly belong to their secure UUID, making horizontal data leaks impossible.

### Administrative Override

The system utilizes a `service_role` key strictly within the Python backend limits (specifically in `services/supabase_service.py`) for administrative tasks. The React frontend via Streamlit never exposes this key to the client.
