# Contributing to Server Monitor Dashboard

Thank you for your interest in contributing to Server Monitor Dashboard! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

This project follows a Code of Conduct that all contributors are expected to adhere to:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## 💡 How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:

1. Check existing [issues](https://github.com/minhtuancn/server-monitor/issues)
2. Use the latest version of the software
3. Gather relevant information (logs, screenshots, environment)

Bug reports should include:

- Clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- Clear description of the enhancement
- Use cases and benefits
- Possible implementation approach
- Any related issues or discussions

### Code Contributions

Areas where contributions are especially welcome:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage
- Security enhancements

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- SQLite 3
- SSH access to test servers (optional)

### Setup Steps

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/server-monitor.git
   cd server-monitor
   ```

2. **Install Dependencies**

   ```bash
   # Install backend dependencies (from project root)
   pip3 install -r backend/requirements.txt

   # Install test dependencies
   pip3 install -r tests/requirements.txt
   ```

3. **Initialize Database**

   ```bash
   # From project root
   python3 -c "import sys; sys.path.insert(0, 'backend'); import database; database.init_database()"
   ```

4. **Start Development Servers**

   ```bash
   cd ..
   ./start-all.sh
   ```

5. **Run Tests**
   ```bash
   cd tests
   pytest -v
   ```

---

## 📝 Coding Standards

### Python Code Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines:

```python
# Good
def get_server_stats(server_id, include_processes=False):
    """
    Get statistics for a specific server.

    Args:
        server_id: Integer ID of the server
        include_processes: Boolean to include process list

    Returns:
        Dictionary containing server statistics
    """
    pass

# Bad
def GetServerStats(ServerID, IncludeProcesses=False):
    pass
```

### JavaScript Code Style

Use ES6+ features and consistent formatting:

```javascript
// Good
const fetchServerData = async (serverId) => {
  try {
    const response = await fetch(`${API_URL}/api/servers/${serverId}`);
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch server data:", error);
    throw error;
  }
};

// Bad
function GetData(id) {
  var x = fetch(API_URL + "/api/servers/" + id);
  return x;
}
```

### File Organization

```
backend/
├── module_name.py          # Main module
├── tests/
│   └── test_module_name.py # Tests for module
└── docs/
    └── module_name.md      # Documentation
```

---

## 📨 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good commits
git commit -m "feat(api): add server health check endpoint"
git commit -m "fix(security): patch XSS vulnerability in user input"
git commit -m "docs(readme): update installation instructions"

# Bad commits
git commit -m "fix stuff"
git commit -m "updates"
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Update from main branch**

   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests**

   ```bash
   pytest tests/ -v
   ```

3. **Check code style**

   ```bash
   flake8 backend/
   ```

4. **Update documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update CHANGELOG_v1.0.md

### Creating Pull Request

1. **Create feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**

   ```bash
   git add .
   git commit -m "feat(component): description of changes"
   ```

3. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Fill in PR template
   - Link related issues

### PR Requirements

- [ ] Code follows style guidelines
- [ ] Tests pass successfully
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG_v1.0.md updated
- [ ] No merge conflicts with main
- [ ] PR description is clear and complete

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

- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors
```

---

## 🧪 Testing

### Running Tests

```bash
# All tests
cd tests
pytest -v

# Specific test file
pytest test_api.py -v

# Specific test
pytest test_api.py::TestAuthentication::test_login_success -v

# With coverage
pytest --cov=backend --cov-report=html
```

### Writing Tests

```python
import pytest
from backend import module_name

class TestFeature:
    """Test suite for feature"""

    def test_success_case(self):
        """Test successful operation"""
        result = module_name.function()
        assert result is True

    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            module_name.function(invalid_input)
```

### Test Coverage

Aim for:

- 80%+ overall coverage
- 100% coverage for critical security code
- All new features must include tests

---

## 📚 Documentation

### Code Documentation

```python
def function_name(param1, param2):
    """
    Brief description of function.

    Longer description if needed, explaining what the function
    does, how it works, and any important notes.

    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2

    Returns:
        type: Description of return value

    Raises:
        ExceptionType: When this exception occurs

    Example:
        >>> result = function_name('value1', 'value2')
        >>> print(result)
        'expected output'
    """
    pass
```

### README Updates

When adding features:

1. Update feature list
2. Add configuration examples
3. Update API documentation
4. Add troubleshooting if needed

### API Documentation

Document all endpoints:

```python
@app.route('/api/endpoint', methods=['POST'])
def endpoint():
    """
    Endpoint description.

    Request:
        {
            "param1": "value",
            "param2": 123
        }

    Response:
        {
            "success": true,
            "data": {...}
        }

    Status Codes:
        200: Success
        400: Bad request
        401: Unauthorized
        500: Server error
    """
    pass
```

---

## 🐛 Debugging

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

1. **Database locked**: Stop all services, restart
2. **Port in use**: Check with `lsof -i :PORT`
3. **Import errors**: Verify PYTHONPATH and dependencies

---

## 📞 Getting Help

Need help? Contact:

**Minh Tuấn**

- 📧 Email: [vietkeynet@gmail.com](mailto:vietkeynet@gmail.com)
- 📱 WhatsApp/WeChat: +84912537003
- 🐙 GitHub: [@minhtuancn](https://github.com/minhtuancn)

Or:

- Open an [issue](https://github.com/minhtuancn/server-monitor/issues)
- Check [existing discussions](https://github.com/minhtuancn/server-monitor/discussions)
- Read the [documentation](README.md)

---

## 🙏 Thank You!

Thank you for contributing to Server Monitor Dashboard! Your contributions help make this project better for everyone.

---

**Last Updated**: 2026-01-06
**Version**: 1.0.0

---

## Documentation Rules (IMPORTANT)

- Canonical docs live in `docs/` only. Do not add new root-level `.md` files.
- Update the index at `docs/README.md` whenever adding or moving docs.
- Use these categories: Getting Started, Architecture, Features, API, Frontend, Backend, Security, Deployment, Operations, Testing, Release, Roadmap.
- For decisions, use `docs/adr/YYYY-MM-DD-title.md` (optional, but recommended).

## AI/Agent Contributors

To avoid scope drift ("lan man"):

- Follow the existing docs structure — do not invent new folders/files.
- Prefer editing canonical docs instead of creating new documents.
- Keep PRs small with clear acceptance criteria and link to the roadmap/task.
- If a new doc category is needed, propose structure change first via PR.
