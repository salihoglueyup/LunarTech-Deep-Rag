# Enterprise Admin Panel

The Admin Panel is a restricted view within LunarTech designed exclusively for system administrators to oversee platform usage, manage the team, and generate global reports.

## Accessing the Admin Panel

The Admin Panel is hidden from standard users. It will only appear in the sidebar navigation if the currently authenticated user's email matches one of the emails defined in `config.ADMIN_EMAILS` (located in `config.py`).

By default, an email like `admin@metazon.com` gives immediate access.

## Capabilities

### 1. Global Document Oversight

Admins have access to a global data table viewing every document uploaded to the system across all users.

- Identifies the uploader's `user_id`.
- Tracks `page_count` and `chunk_count` for billing or storage estimation.
- Allows the admin to systematically delete documents that violate data handling policies.

### 2. Telemetry and Analytics

The panel provides real-time gauges and charts detailing:

- Total Tokens Consumed.
- Memory/Disk Cache Hit Ratios.
- Count of active Shadow Agent tasks currently running in the background.

## Future Extensibility

The admin panel is built using modular Streamlit containers. Developers can easily mount new features (e.g., User Role assignment, Billing dashboards) by importing and writing new functions inside `app/views/admin.py`.
