# Contributing to Agentic Reliability Framework

Thank you for your interest in contributing! 🎉

ARF is a production-grade, multi-agent system designed to make AI infrastructure self-healing and predictive. Every contribution helps build more reliable AI systems.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git
- 4GB+ RAM recommended

### Setup (5 minutes)

1. **Fork the repository** (click "Fork" on GitHub)

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentic-reliability-framework.git
   cd agentic-reliability-framework
   ```

3. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```
   Open: http://localhost:7860

6. **Run tests:**
   ```bash
   pytest Test/ -v
   ```

✅ If tests pass, you're ready to contribute!

## 🎯 Ways to Contribute

### 1. 🐛 Report Bugs

Found something broken? [Open an issue](https://github.com/petterjuan/agentic-reliability-framework/issues/new) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### 2. 💡 Suggest Features

Have an idea? [Start a discussion](https://github.com/petterjuan/agentic-reliability-framework/discussions) with:
- Use case: Why this would be valuable
- Proposed solution (optional)
- Alternatives considered

### 3. 📚 Improve Documentation

- Fix typos or unclear sections
- Add code examples
- Improve docstrings
- Create tutorials

### 4. 💻 Submit Code

- Fix bugs from issues
- Implement requested features
- Optimize performance
- Add test coverage

## 📋 Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

**Naming convention:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `perf/` - Performance improvements
- `test/` - Adding tests

### 2. Make Your Changes

**Best practices:**
- Write clean, readable code
- Add type hints to functions
- Include docstrings
- Follow existing patterns
- Keep changes focused

### 3. Add Tests

```python
# Test/test_your_feature.py
def test_your_function():
    """Test description"""
    result = your_function(input_data)
    assert result == expected_output
```

### 4. Run Tests

```bash
pytest Test/ -v
```

### 5. Commit

```bash
git commit -m "feat: add your feature description"
```

**Commit format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `perf:` Performance
- `test:` Tests

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create pull request on GitHub with clear description.

## 🎨 Code Style

- **Python 3.10+** syntax
- **Type hints** for functions
- **Docstrings** for public methods
- **Async-first** patterns where applicable
- Follow existing code patterns

## 🧪 Testing Guidelines

- Add tests for new features
- Maintain 80%+ coverage
- Fast tests (<1s each)
- Use pytest fixtures

## 💬 Communication

- **GitHub Discussions:** Questions, ideas, showcase
- **Issues:** Bug reports, feature requests
- **Pull Requests:** Code contributions

## 📖 First-Time Contributors

New to open source? Welcome! Start with:
- Issues labeled `good-first-issue`
- Documentation improvements
- Adding test cases

## 🎯 Priority Areas

**High Priority:**
- Performance optimizations (sub-100ms targets)
- Integration examples (Prometheus, Grafana, K8s)
- Additional demo scenarios
- Documentation improvements

**Medium Priority:**
- Additional healing policies
- Enhanced visualizations
- CLI improvements
- Edge case handling

**Welcome anytime:**
- Code cleanup
- Type hints
- Comments

## ⚖️ Code of Conduct

- Be respectful and constructive
- Focus on solutions, not blame
- Welcome newcomers
- Give credit where due

## 🏆 Recognition

Contributors get:
- Credit in release notes
- GitHub contributor badge
- LinkedIn recommendations (if desired)
- Featured in documentation

## 📞 Questions?

- **Discussions:** https://github.com/petterjuan/agentic-reliability-framework/discussions
- **Email:** petter2025us@outlook.com
- **LinkedIn:** [linkedin.com/in/petterjuan](https://linkedin.com/in/petterjuan)

---

Thank you for making ARF better! 🙏

*For utopia... For money.* — Let's build reliable AI together. 🧠⚡
