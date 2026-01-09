# Pull Request Checklist

Use this checklist before submitting a pull request to ensure quality and completeness.

---

## Pre-Submit Checklist

### Code Quality

- [ ] **Code follows project style guide** (see AGENTS.md)
  - Backend: PEP 8, type hints, black formatting
  - Frontend: TypeScript strict, functional components, MUI components
- [ ] **No commented-out code** (remove or explain why kept)
- [ ] **No debug statements** (`console.log`, `print` for debugging removed)
- [ ] **No hardcoded values** (use environment variables or constants)
- [ ] **Error handling added** (try/catch, error boundaries, user-friendly messages)

### Testing

- [ ] **Backend tests pass**: `pytest tests/ -v` (all tests green)
- [ ] **Frontend lint passes**: `npm run lint` (no errors)
- [ ] **Frontend type check passes**: `npx tsc --noEmit` (no errors)
- [ ] **Frontend build succeeds**: `npm run build` (no errors)
- [ ] **Manual testing done** (describe in PR description)
- [ ] **Integration tested** (`./start-all.sh` and verify affected features)

### Security

- [ ] **No secrets committed** (API keys, passwords, tokens)
- [ ] **Input validation added** (sanitize user input)
- [ ] **SQL injection prevented** (use parameterized queries)
- [ ] **XSS prevented** (escape HTML, use React's built-in protection)
- [ ] **CSRF protection maintained** (don't bypass existing protections)

### Documentation

- [ ] **README.md updated** (if user-facing changes)
- [ ] **CHANGELOG.md updated** (add entry for this PR)
- [ ] **API docs updated** (if API changes)
- [ ] **Code comments added** (for complex logic)
- [ ] **docs/ updated** (if new features or architecture changes)

### PR Description

- [ ] **Summary section** (1-3 bullet points)
- [ ] **Scope section** (what's included)
- [ ] **Out of Scope section** (what's NOT included)
- [ ] **Testing section** (how you tested)
- [ ] **Risks section** (Low/Medium/High with explanation)
- [ ] **Screenshots** (if UI changes)
- [ ] **Breaking changes noted** (if any)

### Commit Hygiene

- [ ] **Meaningful commit messages** (not "fix", "update", "changes")
- [ ] **Atomic commits** (one logical change per commit)
- [ ] **No merge commits** (rebase before PR if needed)

---

## PR Title Format

Use conventional commits style:

```
<type>(<scope>): <description>

Examples:
fix(backend): resolve CORS error with custom domains
feat(frontend): add first-run admin setup page
docs: update CUSTOM-DOMAIN-GUIDE with Nginx examples
refactor(api): extract rate limiting to middleware
test: add unit tests for user management
```

### Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring (no functional change)
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling
- `perf`: Performance improvement
- `style`: Code style/formatting (no logic change)

### Scope (optional):

- `backend`, `frontend`, `api`, `docs`, `build`, `ci`, `deploy`

---

## PR Description Template

Copy this template into your PR description:

```markdown
## Summary

- [Main change in one sentence]
- [Secondary change]
- [Additional impact]

## Scope

- Files changed: [list key files]
- Features affected: [e.g., Authentication, Dashboard UI]
- Type: [Bug fix / Feature / Refactor / Docs]

## Out of Scope

- Did NOT touch: [list areas intentionally not modified]
- Deferred: [list work for future PRs]

## Testing

- [x] pytest tests/ -v (all pass)
- [x] npm run lint && npx tsc --noEmit (no errors)
- [x] npm run build (succeeds)
- [x] Manual: [describe manual testing done]
- [x] Integration: [describe integration testing]

## Risks

- **[Low/Medium/High]**: [Explanation]

## Breaking Changes

- None
  OR
- [List any breaking changes with migration instructions]

## Screenshots

<!-- If UI changes, add before/after screenshots -->

## Docs Updated

- Updated: [list doc files changed]
  OR
- No docs changes needed

## Related Issues

Fixes #123
Closes #456
Related to #789
```

---

## Post-Merge Checklist

- [ ] **Delete feature branch** (if not needed)
- [ ] **Update project board** (move cards to "Done")
- [ ] **Notify stakeholders** (if major change)
- [ ] **Monitor production** (if deployed)
- [ ] **Update ROADMAP.md** (if milestone reached)

---

## Common Pitfalls to Avoid

❌ **Don't:**

- Submit PRs with failing tests
- Mix unrelated changes in one PR
- Add features not requested (scope creep)
- Skip documentation updates
- Commit secrets or API keys
- Rewrite entire modules without discussion
- Change database schema without migration plan

✅ **Do:**

- Keep PRs small and focused
- Add tests for new code
- Update docs alongside code
- Ask for clarification if requirements unclear
- Rebase on main before submitting
- Respond to review comments promptly
- Celebrate when PR is merged! 🎉
