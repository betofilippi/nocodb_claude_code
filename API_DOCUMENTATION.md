# NocoDB HTTP Server API Documentation

This is a REST API server for NocoDB that can be deployed on Railway or any other hosting platform.

## Base URL

When deployed: `https://your-app.railway.app`

## Authentication

Set the following environment variables:
- `NOCODB_BASE_URL`: Your NocoDB instance URL (e.g., `https://nocodb.plataforma.app/api/v2`)
- `NOCODB_API_KEY`: Your NocoDB API token

## Endpoints

### Health Check

```
GET /health
```

Returns the server health status.

### List Available Tools

```
GET /tools
```

Returns a list of all available tools/operations.

### Execute Tool

```
POST /execute
Content-Type: application/json

{
  "tool": "tool_name",
  "args": {
    "arg1": "value1",
    "arg2": "value2"
  }
}
```

## Available Tools

### Base Operations

#### list_bases
List all bases.
```json
{
  "tool": "list_bases",
  "args": {}
}
```

#### get_base
Get a specific base.
```json
{
  "tool": "get_base",
  "args": {
    "base_id": "base_id_here"
  }
}
```

#### create_base
Create a new base.
```json
{
  "tool": "create_base",
  "args": {
    "name": "My New Base",
    "description": "Optional description"
  }
}
```

#### update_base
Update an existing base.
```json
{
  "tool": "update_base",
  "args": {
    "base_id": "base_id_here",
    "name": "Updated Name",
    "description": "Updated description"
  }
}
```

#### delete_base
Delete a base.
```json
{
  "tool": "delete_base",
  "args": {
    "base_id": "base_id_here"
  }
}
```

### Table Operations

#### list_tables
List all tables in a base.
```json
{
  "tool": "list_tables",
  "args": {
    "base_id": "base_id_here"
  }
}
```

#### get_table
Get a specific table.
```json
{
  "tool": "get_table",
  "args": {
    "base_id": "base_id_here",
    "table_id": "table_id_here"
  }
}
```

#### create_table
Create a new table.
```json
{
  "tool": "create_table",
  "args": {
    "base_id": "base_id_here",
    "name": "My Table",
    "columns": [
      {
        "name": "Name",
        "type": "SingleLineText",
        "required": true
      },
      {
        "name": "Email",
        "type": "Email"
      }
    ]
  }
}
```

#### update_table
Update a table.
```json
{
  "tool": "update_table",
  "args": {
    "table_id": "table_id_here",
    "name": "Updated Table Name"
  }
}
```

#### delete_table
Delete a table.
```json
{
  "tool": "delete_table",
  "args": {
    "table_id": "table_id_here"
  }
}
```

### Column Operations

#### list_columns
List all columns in a table.
```json
{
  "tool": "list_columns",
  "args": {
    "table_id": "table_id_here"
  }
}
```

#### create_column
Create a new column.
```json
{
  "tool": "create_column",
  "args": {
    "table_id": "table_id_here",
    "column_data": {
      "name": "Age",
      "type": "Number",
      "required": false
    }
  }
}
```

#### update_column
Update a column.
```json
{
  "tool": "update_column",
  "args": {
    "column_id": "column_id_here",
    "column_data": {
      "name": "Updated Column Name",
      "required": true
    }
  }
}
```

#### delete_column
Delete a column.
```json
{
  "tool": "delete_column",
  "args": {
    "column_id": "column_id_here"
  }
}
```

### Record Operations

#### list_records
List records in a table.
```json
{
  "tool": "list_records",
  "args": {
    "table_id": "table_id_here",
    "limit": 25,
    "offset": 0,
    "fields": ["Name", "Email"],
    "where": "(Name,eq,John)",
    "sort": ["-CreatedAt"]
  }
}
```

#### get_record
Get a specific record.
```json
{
  "tool": "get_record",
  "args": {
    "table_id": "table_id_here",
    "record_id": "record_id_here"
  }
}
```

#### create_record
Create a new record.
```json
{
  "tool": "create_record",
  "args": {
    "table_id": "table_id_here",
    "record_data": {
      "Name": "John Doe",
      "Email": "john@example.com"
    }
  }
}
```

#### update_record
Update a record.
```json
{
  "tool": "update_record",
  "args": {
    "table_id": "table_id_here",
    "record_id": "record_id_here",
    "record_data": {
      "Name": "Jane Doe"
    }
  }
}
```

#### delete_record
Delete a record.
```json
{
  "tool": "delete_record",
  "args": {
    "table_id": "table_id_here",
    "record_id": "record_id_here"
  }
}
```

### Bulk Operations

#### bulk_create_records
Create multiple records at once.
```json
{
  "tool": "bulk_create_records",
  "args": {
    "table_id": "table_id_here",
    "records": [
      {"Name": "John", "Email": "john@example.com"},
      {"Name": "Jane", "Email": "jane@example.com"}
    ]
  }
}
```

#### bulk_update_records
Update multiple records at once.
```json
{
  "tool": "bulk_update_records",
  "args": {
    "table_id": "table_id_here",
    "records": [
      {"id": "record1_id", "Name": "John Updated"},
      {"id": "record2_id", "Name": "Jane Updated"}
    ]
  }
}
```

#### bulk_delete_records
Delete multiple records at once.
```json
{
  "tool": "bulk_delete_records",
  "args": {
    "table_id": "table_id_here",
    "record_ids": ["record1_id", "record2_id"]
  }
}
```

### View Operations

#### list_views
List all views in a table.
```json
{
  "tool": "list_views",
  "args": {
    "table_id": "table_id_here"
  }
}
```

#### create_view
Create a new view.
```json
{
  "tool": "create_view",
  "args": {
    "table_id": "table_id_here",
    "title": "Active Users",
    "view_type": "grid"
  }
}
```

#### update_view
Update a view.
```json
{
  "tool": "update_view",
  "args": {
    "view_id": "view_id_here",
    "title": "Updated View Title"
  }
}
```

#### delete_view
Delete a view.
```json
{
  "tool": "delete_view",
  "args": {
    "view_id": "view_id_here"
  }
}
```

### Filter Operations

#### list_filters
List all filters in a view.
```json
{
  "tool": "list_filters",
  "args": {
    "view_id": "view_id_here"
  }
}
```

#### create_filter
Create a new filter.
```json
{
  "tool": "create_filter",
  "args": {
    "view_id": "view_id_here",
    "filter_data": {
      "field": "Status",
      "op": "eq",
      "value": "Active"
    }
  }
}
```

#### update_filter
Update a filter.
```json
{
  "tool": "update_filter",
  "args": {
    "filter_id": "filter_id_here",
    "filter_data": {
      "value": "Inactive"
    }
  }
}
```

#### delete_filter
Delete a filter.
```json
{
  "tool": "delete_filter",
  "args": {
    "filter_id": "filter_id_here"
  }
}
```

### Sort Operations

#### list_sorts
List all sorts in a view.
```json
{
  "tool": "list_sorts",
  "args": {
    "view_id": "view_id_here"
  }
}
```

#### create_sort
Create a new sort.
```json
{
  "tool": "create_sort",
  "args": {
    "view_id": "view_id_here",
    "field": "CreatedAt",
    "direction": "desc"
  }
}
```

#### update_sort
Update a sort.
```json
{
  "tool": "update_sort",
  "args": {
    "sort_id": "sort_id_here",
    "direction": "asc"
  }
}
```

#### delete_sort
Delete a sort.
```json
{
  "tool": "delete_sort",
  "args": {
    "sort_id": "sort_id_here"
  }
}
```

### Shared View Operations

#### create_shared_view
Create a shared view.
```json
{
  "tool": "create_shared_view",
  "args": {
    "view_id": "view_id_here",
    "password": "optional_password"
  }
}
```

#### update_shared_view
Update a shared view.
```json
{
  "tool": "update_shared_view",
  "args": {
    "view_id": "view_id_here",
    "password": "new_password"
  }
}
```

#### delete_shared_view
Delete a shared view.
```json
{
  "tool": "delete_shared_view",
  "args": {
    "view_id": "view_id_here"
  }
}
```

### Webhook Operations

#### list_webhooks
List all webhooks.
```json
{
  "tool": "list_webhooks",
  "args": {
    "table_id": "table_id_here"
  }
}
```

#### create_webhook
Create a new webhook.
```json
{
  "tool": "create_webhook",
  "args": {
    "table_id": "table_id_here",
    "title": "New Record Webhook",
    "url": "https://example.com/webhook",
    "event": "record.create",
    "condition": {
      "field": "Status",
      "op": "eq",
      "value": "Active"
    }
  }
}
```

#### update_webhook
Update a webhook.
```json
{
  "tool": "update_webhook",
  "args": {
    "hook_id": "hook_id_here",
    "webhook_data": {
      "title": "Updated Webhook",
      "url": "https://example.com/new-webhook"
    }
  }
}
```

#### delete_webhook
Delete a webhook.
```json
{
  "tool": "delete_webhook",
  "args": {
    "hook_id": "hook_id_here"
  }
}
```

### Other Operations

#### global_search
Search across all data.
```json
{
  "tool": "global_search",
  "args": {
    "query": "search term"
  }
}
```

#### list_comments
List comments for a record.
```json
{
  "tool": "list_comments",
  "args": {
    "table_id": "table_id_here",
    "record_id": "record_id_here"
  }
}
```

#### create_comment
Create a new comment.
```json
{
  "tool": "create_comment",
  "args": {
    "table_id": "table_id_here",
    "record_id": "record_id_here",
    "comment": "This is a comment"
  }
}
```

#### update_comment
Update a comment.
```json
{
  "tool": "update_comment",
  "args": {
    "comment_id": "comment_id_here",
    "comment": "Updated comment"
  }
}
```

#### delete_comment
Delete a comment.
```json
{
  "tool": "delete_comment",
  "args": {
    "comment_id": "comment_id_here"
  }
}
```

#### upload_file
Upload a file to storage.
```json
{
  "tool": "upload_file",
  "args": {
    "storage": "local",
    "file_path": "/path/to/file.jpg"
  }
}
```

## Error Handling

All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a detail message:
```json
{
  "detail": "Error message here"
}
```

## Deployment on Railway

1. Set environment variables in Railway:
   - `NOCODB_BASE_URL`
   - `NOCODB_API_KEY`

2. Deploy using Railway CLI or GitHub integration

3. The server will automatically use the PORT environment variable provided by Railway

## Example Usage

```bash
# Health check
curl https://your-app.railway.app/health

# List all bases
curl -X POST https://your-app.railway.app/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "list_bases", "args": {}}'

# Create a new record
curl -X POST https://your-app.railway.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create_record",
    "args": {
      "table_id": "table_id_here",
      "record_data": {
        "Name": "John Doe",
        "Email": "john@example.com"
      }
    }
  }'
```