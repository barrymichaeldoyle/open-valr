# OpenAPI Specification Structure

This OpenAPI specification is organized into multiple files for better maintainability and organization.

## File Structure

```
openapi/
├── valr.yaml              # Main OpenAPI file (entry point)
├── paths/
│   ├── public.yaml       # Public API endpoints
│   ├── account.yaml      # Account API endpoints
│   └── wallets.yaml      # Wallet API endpoints
└── components/
    └── schemas.yaml      # Shared schemas/components
```

## How It Works

The main `valr.yaml` file uses `$ref` to reference paths and components from external files:

- **Paths**: Each path is referenced individually using JSON pointer syntax

  ```yaml
  /v1/public/status:
    $ref: "./paths/public.yaml#/paths/~1v1~1public~1status"
  ```

- **Schemas**: Each schema is referenced individually
  ```yaml
  components:
    schemas:
      ValrStatus:
        $ref: "./components/schemas.yaml#/components/schemas/ValrStatus"
  ```

## Adding New APIs

### Adding a Public API endpoint

1. Add the path definition to `paths/public.yaml`
2. Reference it in `valr.yaml`:
   ```yaml
   /v1/public/new-endpoint:
     $ref: "./paths/public.yaml#/paths/~1v1~1public~1new-endpoint"
   ```

### Adding Account or Wallet APIs

1. Add the path definition to `paths/account.yaml` or `paths/wallets.yaml`
2. Reference it in `valr.yaml` following the same pattern

### Adding New Schemas

1. Add the schema to `components/schemas.yaml`
2. Reference it in `valr.yaml` under `components.schemas`

## Using with Tools

Most OpenAPI tools (Swagger UI, Redoc, code generators) support external `$ref` references. If you need to bundle everything into a single file, you can use:

- **@redocly/cli**: `redocly bundle valr.yaml -o bundled.yaml`
- **swagger-cli**: `swagger-cli bundle valr.yaml -o bundled.yaml`

## Path Reference Syntax

When referencing paths, use JSON pointer encoding:

- `/` becomes `~1`
- `~` becomes `~0`

Example: `/v1/public/status` → `~1v1~1public~1status`
