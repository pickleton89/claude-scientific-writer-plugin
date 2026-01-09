"""Schema validation for paper-2-web transformation requests."""

from pathlib import Path
from typing import Any
import json

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import jsonschema
    from jsonschema import Draft202012Validator, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


SCHEMA_DIR = Path(__file__).parent


def load_schema(schema_name: str = "transformation_request") -> dict[str, Any]:
    """Load a schema file from the schemas directory.

    Args:
        schema_name: Name of the schema file (without extension)

    Returns:
        Schema as a dictionary

    Raises:
        FileNotFoundError: If schema file doesn't exist
        ImportError: If PyYAML is not installed
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is required to load schemas. Install with: pip install pyyaml")

    schema_path = SCHEMA_DIR / f"{schema_name}.yaml"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with open(schema_path) as f:
        return yaml.safe_load(f)


def validate_request(request: dict[str, Any], schema_name: str = "transformation_request") -> tuple[bool, list[str]]:
    """Validate a transformation request against the schema.

    Args:
        request: The request dictionary to validate
        schema_name: Name of the schema to validate against

    Returns:
        Tuple of (is_valid, list_of_errors)

    Raises:
        ImportError: If jsonschema is not installed
    """
    if not JSONSCHEMA_AVAILABLE:
        raise ImportError("jsonschema is required for validation. Install with: pip install jsonschema")

    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)

    errors = []
    for error in validator.iter_errors(request):
        path = " -> ".join(str(p) for p in error.path) if error.path else "root"
        errors.append(f"{path}: {error.message}")

    return len(errors) == 0, errors


def get_schema_defaults(schema_name: str = "transformation_request") -> dict[str, Any]:
    """Extract default values from a schema.

    Args:
        schema_name: Name of the schema

    Returns:
        Dictionary of property paths to their default values
    """
    schema = load_schema(schema_name)
    defaults = {}

    def extract_defaults(obj: dict, path: str = "") -> None:
        if not isinstance(obj, dict):
            return

        properties = obj.get("properties", {})
        for prop_name, prop_schema in properties.items():
            prop_path = f"{path}.{prop_name}" if path else prop_name
            if "default" in prop_schema:
                defaults[prop_path] = prop_schema["default"]
            extract_defaults(prop_schema, prop_path)

    extract_defaults(schema)
    return defaults


def apply_defaults(request: dict[str, Any], schema_name: str = "transformation_request") -> dict[str, Any]:
    """Apply schema defaults to a request.

    Args:
        request: The request dictionary
        schema_name: Name of the schema

    Returns:
        Request with defaults applied (original is not modified)
    """
    import copy
    result = copy.deepcopy(request)
    defaults = get_schema_defaults(schema_name)

    for path, default_value in defaults.items():
        parts = path.split(".")
        obj = result

        # Navigate to parent
        for part in parts[:-1]:
            if part not in obj:
                break
            obj = obj[part]
        else:
            # Apply default if key doesn't exist
            final_key = parts[-1]
            if final_key not in obj:
                obj[final_key] = default_value

    return result


__all__ = [
    "load_schema",
    "validate_request",
    "get_schema_defaults",
    "apply_defaults",
    "SCHEMA_DIR",
]
