# 🤝 Contributing Guidelines

> **For AI Agents:** Follow these standards when making changes to the codebase. These ensure consistency and maintainability.

## Code Standards

### Python Style
- **Formatter:** Black (line length 100)
- **Linter:** Ruff
- **Type Hints:** Required for all public functions
- **Docstrings:** Required for all classes and public methods

### File Organization
- **Max File Size:** 300 lines per file
- **Naming:** `snake_case` for files, functions, variables
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`

### Module Structure
```
src/
  ├── api/          # API routes only
  ├── services/     # Business logic only
  ├── models/       # Data models only
  └── utils/        # Helper functions only
```

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `refactor/description` - Code improvements

### Commit Messages
Follow conventional commits:
```
type(scope): description

[optional body]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

**Examples:**
```
feat(vector-store): add similarity threshold configuration
fix(webhook): handle missing X-Gitlab-Token header
docs(architecture): update component diagram
test(openai): add prompt building tests
```

## Testing Requirements

### Coverage
- **Minimum:** 70% overall
- **New Features:** 80% coverage required
- **Critical Paths:** 100% coverage required

### Test Structure
```python
def test_function_name_when_condition_then_expected():
    # Arrange
    setup = create_test_data()
    
    # Act
    result = function_under_test(setup)
    
    # Assert
    assert result == expected_value
```

### Running Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_webhook.py

# With coverage
pytest --cov=src --cov-report=html
```

## Code Quality Checks

### Pre-Commit Hooks
Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

These run automatically on every commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- Ruff linting
- Type checking with mypy

### Manual Checks
```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/ --fix

# Type check
mypy src/ --ignore-missing-imports
```

## Adding New Features

### 1. Language Support
**File:** `src/services/repo_analyzer.py`

Add extension to set:
```python
code_extensions = {
    '.py', '.js', # existing
    '.your_ext'   # new
}
```

Update `docs/ARCHITECTURE.md` and `README.md`.

### 2. New Service
**Template:**
```python
from src.utils import get_logger

logger = get_logger(__name__)


class NewService:
    def __init__(self):
        pass
    
    def public_method(self) -> ReturnType:
        """
        Brief description.
        
        Returns:
            ReturnType: Description
        """
        try:
            # Implementation
            logger.info("Operation completed")
            return result
        except Exception as e:
            logger.error(f"Error in operation: {e}")
            raise
```

**Requirements:**
- Add to `src/services/__init__.py`
- Create unit tests in `tests/test_new_service.py`
- Update `docs/ARCHITECTURE.md`

### 3. New Configuration
**File:** `src/config.py`

Add to Settings class:
```python
new_setting: str = Field(
    default="default_value",
    env="NEW_SETTING"
)
```

**Also update:**
- `.env.example` - Document new variable
- `README.md` - Add to configuration section
- `docs/ARCHITECTURE.md` - Explain usage

## Error Handling

### Pattern
```python
try:
    result = risky_operation()
    logger.info("Success message")
    return result
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    # Handle or re-raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Fallback behavior
```

### Logging Levels
- `DEBUG` - Detailed diagnostic info
- `INFO` - General operational events
- `WARNING` - Potentially harmful situations
- `ERROR` - Error events, may allow continued operation
- `CRITICAL` - Severe errors causing shutdown

## Documentation Requirements

### Code Documentation
```python
def function_name(param: Type) -> ReturnType:
    """
    Brief description of what this does.
    
    Args:
        param: Description of parameter
        
    Returns:
        ReturnType: Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
    """
    pass
```

### Files to Update
When adding features, update:
- [ ] Code implementation
- [ ] Unit tests
- [ ] `README.md` if user-facing
- [ ] `docs/ARCHITECTURE.md` if architectural change
- [ ] `.env.example` if new config
- [ ] This file if new patterns introduced

## Pull Request Process

### Before Submitting
1. Run all tests: `pytest`
2. Check coverage: `pytest --cov=src`
3. Format code: `black src/ tests/`
4. Lint code: `ruff check src/ tests/`
5. Update documentation
6. Write clear commit messages

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings
```

## Common Patterns

### Configuration Access
```python
from src.config import settings

value = settings.config_name
```

### Logging
```python
from src.utils import get_logger

logger = get_logger(__name__)
logger.info("Message")
```

### Service Initialization
```python
# In orchestrator or main
service = ServiceClass()
result = service.method()
```

### API Responses
```python
from fastapi import HTTPException

if error:
    raise HTTPException(status_code=400, detail="Message")

return {"status": "success", "data": result}
```

## Performance Guidelines

### File Operations
- Use size limits: `if file_size > settings.max_file_size_kb`
- Limit results: `[:settings.max_context_files]`
- Close resources: Use context managers

### API Calls
- Implement retries for transient errors
- Use timeouts
- Cache when possible

### Memory Management
- Stream large files
- Limit in-memory collections
- Clean up after processing

## Security Guidelines

### Secrets Management
- **Never** hardcode API keys
- Use environment variables only
- Never log sensitive data
- Sanitize user inputs

### Input Validation
```python
from pydantic import BaseModel, Field

class InputModel(BaseModel):
    value: str = Field(..., min_length=1, max_length=100)
```

### File Access
- Validate paths
- Stay within allowed directories
- Sanitize filenames

---

**Questions?**
Review `docs/ARCHITECTURE.md` for system design details.
Check existing code for examples of these patterns.
