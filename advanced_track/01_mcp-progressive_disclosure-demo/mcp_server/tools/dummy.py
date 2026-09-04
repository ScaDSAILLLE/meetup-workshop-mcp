"""Großer simulierter Betriebskatalog als realistische Ablenkungsmenge.

Die Spezifikationen erzeugen Tools dynamisch. Ihre Implementierung verändert
keine Systeme, sondern spiegelt Eingaben für die Tool-Auswahl-Demo zurück.
"""

import textwrap

from mcp_server.server import mcp

DUMMY_TOOL_SPECS = [
    ("analyze_data", "dataset", "Analyze a dataset and return statistical summaries including mean, median, standard deviation, and quartiles."),
    ("backup_database", "database_name", "Create a full backup of the specified database. Returns backup file path, size, and checksum."),
    ("check_inventory", "warehouse_id", "Check current inventory levels for a specific warehouse. Returns stock counts and low-stock alerts."),
    ("clean_cache", "cache_type", "Clear the specified cache (redis, memcached, or local). Returns number of entries removed."),
    ("compile_report", "report_type", "Compile a formatted report from raw data. Supported types: pdf, docx, xlsx, html."),
    ("compress_file", "file_path", "Compress a file using gzip. Returns the compressed file path and compression ratio."),
    ("configure_alert", "metric_name", "Configure an alert threshold for a specific metric. Sends notification when threshold is exceeded."),
    ("create_backup_schedule", "database_name", "Set up an automated backup schedule for a database. Supports daily, weekly, and monthly intervals."),
    ("decrypt_data", "encrypted_data", "Decrypt data that was encrypted using the system's encryption key. Returns the original plaintext."),
    ("deploy_application", "app_name", "Deploy an application to the specified environment. Returns deployment ID and status."),
    ("download_log", "log_id", "Download a specific log file by its ID. Returns the file content and metadata."),
    ("encrypt_data", "plaintext", "Encrypt data using AES-256. Returns the encrypted ciphertext and encryption key ID."),
    ("export_data", "table_name", "Export database table data to CSV, JSON, or XML format. Returns a download URL."),
    ("flush_queue", "queue_name", "Remove all pending messages from a message queue. Returns the number of messages flushed."),
    ("generate_api_key", "service_name", "Generate a new API key for a specific service. Returns the key, secret, and expiration date."),
    ("generate_report", "report_template", "Generate a report from a template. Fills in placeholders with current data and returns formatted output."),
    ("get_cache_stats", "cache_name", "Retrieve statistics for a cache including hit rate, miss rate, memory usage, and evictions."),
    ("get_config", "config_key", "Retrieve a configuration value by its key. Returns the value and its last modification timestamp."),
    ("get_database_stats", "database_name", "Retrieve statistics for a database including table count, row count, and storage size."),
    ("get_log_level", "service_name", "Get the current logging level for a service. Returns level (debug, info, warn, error) and last change."),
    ("get_memory_usage", "server_id", "Get current memory usage for a server. Returns total, used, and free memory in MB."),
    ("get_metrics", "service_name", "Retrieve performance metrics for a service including CPU, memory, requests/sec, and latency."),
    ("get_queue_stats", "queue_name", "Retrieve statistics for a message queue including depth, throughput, and consumer count."),
    ("get_server_status", "server_id", "Check the operational status of a server. Returns uptime, load average, and health indicators."),
    ("get_storage_usage", "volume_id", "Get current storage usage for a volume. Returns total, used, and available space in GB."),
    ("import_data", "file_path", "Import data from a file into the database. Supports CSV, JSON, and XML formats."),
    ("index_document", "document_id", "Add a document to the search index. Returns the indexing status and document score."),
    ("list_databases", "instance_id", "List all databases on a database instance. Returns database names, sizes, and table counts."),
    ("list_logs", "service_name", "List available log files for a service. Returns log IDs, filenames, sizes, and creation dates."),
    ("list_queues", "broker_id", "List all message queues on a message broker. Returns queue names, depths, and consumer counts."),
    ("list_servers", "region", "List all servers in a specific region. Returns server IDs, hostnames, IP addresses, and statuses."),
    ("list_volumes", "instance_id", "List all storage volumes attached to an instance. Returns volume IDs, sizes, and mount points."),
    ("monitor_service", "service_name", "Start monitoring a service for health and performance. Returns monitor ID and alert configuration."),
    ("notify_team", "team_name", "Send a notification to a team channel. Supports email, Slack, and Teams delivery."),
    ("optimize_database", "database_name", "Run optimization tasks on a database including vacuum, analyze, and index rebuild."),
    ("pause_service", "service_name", "Temporarily pause a running service. Returns the pause status and estimated resume time."),
    ("purge_logs", "log_type", "Delete log entries older than the retention period. Returns the number of entries purged."),
    ("query_database", "query", "Execute a read-only SQL query on the database. Returns query results and execution time."),
    ("rebuild_index", "index_name", "Rebuild a search index from scratch. Returns progress percentage and estimated completion time."),
    ("register_webhook", "event_type", "Register a webhook URL to receive notifications for a specific event type."),
    ("reindex_search", "index_name", "Trigger a full reindex of the search engine. Returns the number of documents indexed."),
    ("restart_service", "service_name", "Restart a running service. Returns the restart status, downtime, and new process ID."),
    ("restore_backup", "backup_id", "Restore a database from a backup file. Returns restore status and database integrity check."),
    ("resume_service", "service_name", "Resume a paused service. Returns the resume status, uptime, and current health."),
    ("rotate_api_key", "service_name", "Rotate the API key for a service. Deactivates the old key and returns the new key."),
    ("run_migration", "migration_id", "Execute a database migration script. Returns migration status, affected rows, and duration."),
    ("scan_vulnerabilities", "target_id", "Scan a target for known security vulnerabilities. Returns findings sorted by severity."),
    ("search_documents", "query", "Search indexed documents using full-text search. Returns matching documents ranked by relevance."),
    ("send_alert", "alert_type", "Send an alert notification to configured channels. Supports critical, warning, and info severity levels."),
    ("set_config", "config_key", "Set a configuration value. Returns the old value, new value, and update timestamp."),
    ("set_log_level", "service_name", "Set the logging level for a service. Supported levels: debug, info, warn, error."),
    ("sync_database", "source_db", "Synchronize data from a source database to a target database. Returns sync status and row counts."),
    ("test_webhook", "webhook_id", "Send a test event to a registered webhook URL. Returns HTTP status, response time, and result."),
    ("update_inventory", "product_id", "Update the inventory level for a specific product. Returns the new stock level and reorder status."),
    ("validate_data", "dataset_id", "Validate a dataset against its schema. Returns validation status, error count, and error details."),
]


def _make_tool_func(func_name: str, param_name: str, description: str):
    """Erzeugt eine benannte, von FastMCP introspektierbare Tool-Funktion."""
    def _tool(value: str) -> dict:
        return {param_name: value, "status": "ok", "tool": func_name}
    _tool.__name__ = func_name
    _tool.__doc__ = textwrap.dedent(f"""
        {description}

        Argument:
            value: Zu verarbeitender Wert für {param_name}.

        Rückgabe:
            Simuliertes Ergebnis mit Status und übergebenem Wert.
    """)
    return _tool


for spec in DUMMY_TOOL_SPECS:
    func = _make_tool_func(*spec)
    mcp.tool(func)
