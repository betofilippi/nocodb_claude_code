#!/usr/bin/env python3
"""
NocoDB HTTP Server - REST API version for Railway deployment
"""

import os
import logging
import requests
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do NocoDB
NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL", "https://nocodb.plataforma.app/api/v2")
NOCODB_API_KEY = os.getenv("NOCODB_API_KEY", "")

app = FastAPI(title="NocoDB HTTP Server", version="1.0.0")

# Pydantic models
class ExecuteRequest(BaseModel):
    tool: str
    args: Dict[str, Any]

class NocoDBAPI:
    def __init__(self):
        self.base_url = NOCODB_BASE_URL
        self.api_key = NOCODB_API_KEY
        self.headers = {
            "xc-token": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making {method} request to {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}, Response: {e.response.text if e.response else 'No response'}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Bases
    def list_bases(self) -> List[Dict[str, Any]]:
        return self._make_request("GET", "/bases")
    
    def get_base(self, base_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/bases/{base_id}")
    
    def create_base(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        data = {"name": name}
        if description:
            data["description"] = description
        return self._make_request("POST", "/bases", json=data)
    
    def update_base(self, base_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        return self._make_request("PATCH", f"/bases/{base_id}", json=data)
    
    def delete_base(self, base_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/bases/{base_id}")
    
    # Tables
    def list_tables(self, base_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/bases/{base_id}/tables")
    
    def get_table(self, base_id: str, table_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/tables/{table_id}")
    
    def create_table(self, base_id: str, name: str, columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        data = {
            "name": name,
            "columns": columns
        }
        return self._make_request("POST", f"/bases/{base_id}/tables", json=data)
    
    def update_table(self, table_id: str, name: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if name:
            data["name"] = name
        return self._make_request("PATCH", f"/tables/{table_id}", json=data)
    
    def delete_table(self, table_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/tables/{table_id}")
    
    # Columns
    def list_columns(self, table_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/tables/{table_id}/columns")
    
    def create_column(self, table_id: str, column_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"/tables/{table_id}/columns", json=column_data)
    
    def update_column(self, column_id: str, column_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/columns/{column_id}", json=column_data)
    
    def delete_column(self, column_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/columns/{column_id}")
    
    # Records
    def list_records(self, table_id: str, limit: int = 25, offset: int = 0, 
                    fields: Optional[List[str]] = None, where: Optional[str] = None,
                    sort: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        params = {
            "limit": limit,
            "offset": offset
        }
        if fields:
            params["fields"] = ",".join(fields)
        if where:
            params["where"] = where
        if sort:
            params["sort"] = sort
        
        return self._make_request("GET", f"/tables/{table_id}/records", params=params)
    
    def get_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/tables/{table_id}/records/{record_id}")
    
    def create_record(self, table_id: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"/tables/{table_id}/records", json=record_data)
    
    def update_record(self, table_id: str, record_id: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/tables/{table_id}/records/{record_id}", json=record_data)
    
    def delete_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/tables/{table_id}/records/{record_id}")
    
    # Bulk operations
    def bulk_create_records(self, table_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._make_request("POST", f"/tables/{table_id}/records/bulk", json=records)
    
    def bulk_update_records(self, table_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/tables/{table_id}/records/bulk", json=records)
    
    def bulk_delete_records(self, table_id: str, record_ids: List[str]) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/tables/{table_id}/records/bulk", json={"ids": record_ids})
    
    # Views
    def list_views(self, table_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/tables/{table_id}/views")
    
    def create_view(self, table_id: str, title: str, view_type: str = "grid") -> Dict[str, Any]:
        data = {
            "title": title,
            "type": view_type
        }
        return self._make_request("POST", f"/tables/{table_id}/views", json=data)
    
    def update_view(self, view_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if title:
            data["title"] = title
        return self._make_request("PATCH", f"/views/{view_id}", json=data)
    
    def delete_view(self, view_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/views/{view_id}")
    
    # Filters
    def list_filters(self, view_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/views/{view_id}/filters")
    
    def create_filter(self, view_id: str, filter_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", f"/views/{view_id}/filters", json=filter_data)
    
    def update_filter(self, filter_id: str, filter_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/filters/{filter_id}", json=filter_data)
    
    def delete_filter(self, filter_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/filters/{filter_id}")
    
    # Sort
    def list_sorts(self, view_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/views/{view_id}/sorts")
    
    def create_sort(self, view_id: str, field: str, direction: str = "asc") -> Dict[str, Any]:
        data = {
            "field": field,
            "direction": direction
        }
        return self._make_request("POST", f"/views/{view_id}/sorts", json=data)
    
    def update_sort(self, sort_id: str, field: Optional[str] = None, direction: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if field:
            data["field"] = field
        if direction:
            data["direction"] = direction
        return self._make_request("PATCH", f"/sorts/{sort_id}", json=data)
    
    def delete_sort(self, sort_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/sorts/{sort_id}")
    
    # Shared views
    def create_shared_view(self, view_id: str, password: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if password:
            data["password"] = password
        return self._make_request("POST", f"/views/{view_id}/share", json=data)
    
    def update_shared_view(self, view_id: str, password: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if password:
            data["password"] = password
        return self._make_request("PATCH", f"/views/{view_id}/share", json=data)
    
    def delete_shared_view(self, view_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/views/{view_id}/share")
    
    # Webhooks
    def list_webhooks(self, table_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/tables/{table_id}/hooks")
    
    def create_webhook(self, table_id: str, title: str, url: str, event: str, 
                      condition: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = {
            "title": title,
            "url": url,
            "event": event
        }
        if condition:
            data["condition"] = condition
        return self._make_request("POST", f"/tables/{table_id}/hooks", json=data)
    
    def update_webhook(self, hook_id: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/hooks/{hook_id}", json=webhook_data)
    
    def delete_webhook(self, hook_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/hooks/{hook_id}")
    
    # Global search
    def global_search(self, query: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/search", params={"q": query})
    
    # Comments
    def list_comments(self, table_id: str, record_id: str) -> List[Dict[str, Any]]:
        return self._make_request("GET", f"/tables/{table_id}/records/{record_id}/comments")
    
    def create_comment(self, table_id: str, record_id: str, comment: str) -> Dict[str, Any]:
        data = {"comment": comment}
        return self._make_request("POST", f"/tables/{table_id}/records/{record_id}/comments", json=data)
    
    def update_comment(self, comment_id: str, comment: str) -> Dict[str, Any]:
        data = {"comment": comment}
        return self._make_request("PATCH", f"/comments/{comment_id}", json=data)
    
    def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/comments/{comment_id}")
    
    # File upload
    def upload_file(self, storage: str, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/storage/upload",
                headers={"xc-token": self.api_key},
                params={"storage": storage},
                files=files
            )
            return response.json()

# Initialize API
api = NocoDBAPI()

# Routes
@app.get("/")
async def root():
    return {
        "message": "NocoDB HTTP Server",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    return {
        "tools": [
            # Bases
            {"name": "list_bases", "description": "List all bases"},
            {"name": "get_base", "description": "Get specific base"},
            {"name": "create_base", "description": "Create new base"},
            {"name": "update_base", "description": "Update existing base"},
            {"name": "delete_base", "description": "Delete base"},
            
            # Tables
            {"name": "list_tables", "description": "List all tables in a base"},
            {"name": "get_table", "description": "Get specific table"},
            {"name": "create_table", "description": "Create new table"},
            {"name": "update_table", "description": "Update existing table"},
            {"name": "delete_table", "description": "Delete table"},
            
            # Columns
            {"name": "list_columns", "description": "List all columns in a table"},
            {"name": "create_column", "description": "Create new column"},
            {"name": "update_column", "description": "Update existing column"},
            {"name": "delete_column", "description": "Delete column"},
            
            # Records
            {"name": "list_records", "description": "List all records in a table"},
            {"name": "get_record", "description": "Get specific record"},
            {"name": "create_record", "description": "Create new record"},
            {"name": "update_record", "description": "Update existing record"},
            {"name": "delete_record", "description": "Delete record"},
            
            # Bulk operations
            {"name": "bulk_create_records", "description": "Create multiple records"},
            {"name": "bulk_update_records", "description": "Update multiple records"},
            {"name": "bulk_delete_records", "description": "Delete multiple records"},
            
            # Views
            {"name": "list_views", "description": "List all views in a table"},
            {"name": "create_view", "description": "Create new view"},
            {"name": "update_view", "description": "Update existing view"},
            {"name": "delete_view", "description": "Delete view"},
            
            # Filters
            {"name": "list_filters", "description": "List all filters in a view"},
            {"name": "create_filter", "description": "Create new filter"},
            {"name": "update_filter", "description": "Update existing filter"},
            {"name": "delete_filter", "description": "Delete filter"},
            
            # Sort
            {"name": "list_sorts", "description": "List all sorts in a view"},
            {"name": "create_sort", "description": "Create new sort"},
            {"name": "update_sort", "description": "Update existing sort"},
            {"name": "delete_sort", "description": "Delete sort"},
            
            # Shared views
            {"name": "create_shared_view", "description": "Create shared view"},
            {"name": "update_shared_view", "description": "Update shared view"},
            {"name": "delete_shared_view", "description": "Delete shared view"},
            
            # Webhooks
            {"name": "list_webhooks", "description": "List all webhooks"},
            {"name": "create_webhook", "description": "Create new webhook"},
            {"name": "update_webhook", "description": "Update existing webhook"},
            {"name": "delete_webhook", "description": "Delete webhook"},
            
            # Other
            {"name": "global_search", "description": "Search across all data"},
            {"name": "list_comments", "description": "List all comments for a record"},
            {"name": "create_comment", "description": "Create new comment"},
            {"name": "update_comment", "description": "Update existing comment"},
            {"name": "delete_comment", "description": "Delete comment"},
            {"name": "upload_file", "description": "Upload file to storage"}
        ]
    }

@app.post("/execute")
async def execute_tool(request: ExecuteRequest):
    """Execute a specific tool with the provided arguments"""
    tool_name = request.tool
    args = request.args
    
    try:
        # Map tool names to API methods
        method = getattr(api, tool_name, None)
        if method is None:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
        
        # Execute the method with the provided arguments
        result = method(**args)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)