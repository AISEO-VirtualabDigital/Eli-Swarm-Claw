# Agent Eli v1 — Integration Registry

## Baserow / PostgreSQL

- **ID**: baserow
- **Category**: data_crm
- **Provider**: self_hosted_or_cloud
- **Auth**: api_token, database_dsn
- **Capabilities**: read_records, create_records, update_records, schema_discovery, sync_jobs
- **Approval Required**: delete_records, bulk_update
- **Status**: available

## Custom REST / Webhook / MCP

- **ID**: custom-adapter
- **Category**: custom
- **Provider**: open
- **Auth**: none, api_key, oauth, basic, bearer, custom
- **Capabilities**: custom_actions, webhooks, mcp_tools, python_scripts, local_commands
- **Approval Required**: external_side_effect, production_write
- **Status**: open

## Google Drive

- **ID**: google-drive
- **Category**: knowledge
- **Provider**: google
- **Auth**: oauth, service_account
- **Capabilities**: search, read, export, folder_sync
- **Approval Required**: share_file, delete_file
- **Status**: available

## n8n

- **ID**: n8n
- **Category**: automation
- **Provider**: self_hosted_or_cloud
- **Auth**: api_key, webhook
- **Capabilities**: run_workflow, inspect_execution, schedule_workflow, pause_workflow
- **Approval Required**: production_webhook_change, credential_change
- **Status**: available

## SiteOne Crawler

- **ID**: siteone
- **Category**: crawler
- **Provider**: self_hosted
- **Auth**: local_process
- **Capabilities**: javascript_crawl, technical_seo, security_audit, accessibility_audit, performance_audit, screenshots, json_export
- **Approval Required**: None
- **Status**: available

