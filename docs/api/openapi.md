# OpenAPI Documentation

Zork automatically generates OpenAPI 3.1 documentation for your API, making it easy to explore and test endpoints.

## Accessing Documentation

### Swagger UI

Interactive API documentation at:

```
http://localhost:8000/docs
```

Swagger UI provides:

- Visual documentation of all endpoints
- Interactive testing interface
- Request/response schema documentation
- Authentication support

### OpenAPI Schema

Raw OpenAPI 3.1 JSON at:

```
http://localhost:8000/openapi.json
```

Use this for:

- Generating client libraries
- API validation tools
- Third-party integrations

## OpenAPI Features

### Auto-Generated Schema

Zork automatically generates schema definitions for:

- Collection models (request/response)
- Field types and validation
- Authentication requirements
- Error responses

### Collection Documentation

For each collection, the schema includes:

- List endpoint with pagination parameters
- Create endpoint with request body
- Get endpoint with path parameters
- Update endpoint with patch body
- Delete endpoint

### Authentication Documentation

Auth endpoints are documented with:

- Request body schemas
- Response schemas
- Security requirements

### Field Documentation

Each field includes:

- Type information
- Format (for dates, URLs, etc.)
- Validation constraints (min/max, required, etc.)
- Default values

## Customizing Documentation

### API Title and Version

Set in your app:

```python
app = Zork(
    title="My Blog API",
    version="2.0.0"
)
```

### Adding Descriptions

Add descriptions in hooks for documentation purposes:

```python
@posts.on("before_create")
async def log_create(data, ctx):
    """This hook validates and transforms post data before creation."""
    return data
```

Note: Hook descriptions are not automatically included in OpenAPI. For detailed API docs, consider adding an OpenAPI specification override.

## Using with Code Generators

Generate client libraries from the OpenAPI schema:

### TypeScript/JavaScript

```bash
npx openapi-typescript https://localhost:8000/openapi.json -o types.ts
```

### Python

```bash
pip install openapi-python-client
openapi-python-client generate --url https://localhost:8000/openapi.json
```

### Other Languages

Most languages have OpenAPI client generators available.

## Postman Collection

Import the OpenAPI schema into Postman:

1. Open Postman
2. Click Import
3. Select "Link"
4. Enter: `http://localhost:8000/openapi.json`

## Authentication in Swagger UI

To test authenticated endpoints in Swagger UI:

1. Click the **Authorize** button
2. Enter your JWT token
3. Click **Authorize**
4. Test your endpoints

Or use the `/api/auth/login` endpoint directly in Swagger:

1. Expand the login POST
2. Click "Try it out"
3. Enter email and password
4. Click Execute
5. Copy the token from the response
6. Authorize with the token

## Health Check

A health check endpoint is available:

```
GET /api/health
```

Response:

```json
{
  "status": "ok"
}
```

This endpoint is not authenticated and can be used for monitoring.

## Next Steps

- [API Endpoints](/api/endpoints) — All available endpoints
- [Authentication](/authentication/setup) — Setting up authentication
