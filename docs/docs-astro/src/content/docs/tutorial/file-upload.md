---
title: 'File Upload'
description: 'Handle file uploads in your adapter and access them from processors.'
---

# File Upload

EVOID never touches HTTP specifics — file upload handling happens in your adapter. The runtime sees only the file metadata your adapter places in `intent.metadata["files"]`.

## Handling File Uploads in Your Adapter

Extract file information in your adapter and attach it to the intent:

```python
from evoid.core import Intent, Level


async def intent_from_upload(request) -> Intent:
    form = await request.form()
    files = {}

    for key in form:
        value = form[key]
        if hasattr(value, "read"):
            # It's a file upload
            content = await value.read()
            files[key] = {
                "filename": value.filename,
                "content_type": value.content_type,
                "size": len(content),
                "content": content,
            }

    form_data = {k: form[k] for k in form if not hasattr(form[k], "read")}

    return Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={
            "method": request.method,
            "path": request.url.path,
            "files": files,
            "form": form_data,
            "headers": dict(request.headers),
        },
    )
```

!!! warning "Memory usage"
    Reading entire files into memory works for small uploads. For large files, consider streaming to disk in the adapter and passing file paths in metadata instead.

## Saving Files to Disk

Your adapter can save files before creating the intent:

```python
import os
import uuid
from pathlib import Path
from evoid.core import Intent, Level


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def intent_from_upload(request) -> Intent:
    form = await request.form()
    files = {}

    for key in form:
        value = form[key]
        if hasattr(value, "read"):
            # Generate unique filename
            ext = Path(value.filename).suffix
            filename = f"{uuid.uuid4()}{ext}"
            filepath = UPLOAD_DIR / filename

            # Save to disk
            content = await value.read()
            filepath.write_bytes(content)

            files[key] = {
                "original_name": value.filename,
                "saved_path": str(filepath),
                "content_type": value.content_type,
                "size": len(content),
            }

    return Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={
            "method": request.method,
            "path": request.url.path,
            "files": files,
            "headers": dict(request.headers),
        },
    )
```

## Accessing Files in Processors

Processors read file metadata from `ctx.metadata["files"]`:

```python
from evoid.core import Context


async def validate_upload(ctx: Context) -> dict:
    files = ctx.metadata.get("files", {})

    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}

    for key, info in files.items():
        if info["size"] > MAX_SIZE:
            raise ValueError(f"File {key} exceeds 10MB limit")

        if info.get("content_type") not in ALLOWED_TYPES:
            raise ValueError(f"File {key}: unsupported type {info['content_type']}")

    return {"validated": True}


async def process_upload(ctx: Context) -> dict:
    files = ctx.metadata.get("files", {})
    results = []

    for key, info in files.items():
        results.append({
            "field": key,
            "filename": info.get("original_name", info.get("filename")),
            "size": info["size"],
            "status": "uploaded",
        })

    return {"files": results, "count": len(results)}
```

## @route Style

```python
from evoid.adapters.asgi import post
from evoid.web.route import Service, before

app = Service("api")

@post("/upload")
async def upload() -> dict:
    files = ctx.metadata.get("files", {})
    return {"uploaded": len(files)}

before("POST:/upload", "validate_upload")
```

!!! tip "Keep file I/O in the adapter or dedicated processors"
    The adapter handles the HTTP-specific file extraction. Dedicated processors handle business logic like virus scanning, thumbnail generation, or metadata extraction.

## @controller Style

```python
from evoid.web.controller import Service, Controller, POST

app = Service("api")

@Controller("/documents")
class DocumentController:
    @POST("/upload")
    async def upload(self) -> dict:
        files = ctx.metadata.get("files", {})
        return {"uploaded": len(files)}
```

## Native IOP Style

```python
from evoid import Intent, Level, add_intent

UPLOAD = Intent(
    name="post:upload",
    level=Level.STANDARD,
)


async def handle_upload(intent: Intent) -> dict:
    files = intent.metadata.get("files", {})

    for key, info in files.items():
        # Process each file
        pass

    return {"uploaded": len(files)}


add_intent(UPLOAD, handle_upload)
```

## Streaming Uploads

For large files, avoid loading everything into memory:

```python
async def intent_from_streaming_upload(request) -> Intent:
    form = await request.form()
    files = {}

    for key in form:
        value = form[key]
        if hasattr(value, "read"):
            # Stream to temp file instead of memory
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                while chunk := await value.read(8192):
                    tmp.write(chunk)
                tmp_path = tmp.name

            files[key] = {
                "original_name": value.filename,
                "temp_path": tmp_path,
                "content_type": value.content_type,
            }

    return Intent(
        name=f"{request.method}:{request.url.path}",
        level=Level.STANDARD,
        metadata={"files": files, "headers": dict(request.headers)},
    )
```

!!! info "File handling is adapter-specific"
    The runtime doesn't know what a file is. Your adapter decides how to handle uploads — in memory, to disk, or streamed. Processors work with the result.
