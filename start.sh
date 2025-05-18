#!/bin/bash
cd /home/betofilippi/projects/nocodb_mcp_full
uvicorn main:app --host 127.0.0.1 --port 8000