# GitHub Actions Workflows - Hướng dẫn sử dụng

## Tổng quan

Repository này sử dụng GitHub Actions để tự động hóa các quy trình CI/CD, kiểm tra bảo mật và review dự án.

## Danh sách Workflows

### 1. Backend CI (`ci.yml`)
**Kích hoạt:** Push và Pull Request đến `main` hoặc `develop`

**Chức năng:**
- Lint Python code với flake8
- Chạy unit tests cho backend
- Kiểm tra cú pháp Python

**Các job:**
- `lint`: Kiểm tra code style và syntax errors
- `test`: Chạy pytest với các test cases

### 2. Frontend CI (`frontend-ci.yml`)
**Kích hoạt:** Push và Pull Request đến `main` hoặc `develop` (chỉ khi có thay đổi trong `frontend-next/`)

**Chức năng:**
- Lint JavaScript/TypeScript code với ESLint
- Kiểm tra TypeScript types
- Build Next.js application

**Các job:**
- `lint-and-build`: Lint, type check và build frontend

### 3. CodeQL Security Analysis (`codeql.yml`)
**Kích hoạt:** 
- Push đến `main`
- Schedule: Hàng ngày lúc 2 AM UTC
- Manual dispatch

**Chức năng:**
- Phân tích bảo mật code với CodeQL
- Quét cả Python và JavaScript/TypeScript
- Sử dụng `security-extended` queries

**Các job:**
- `analyze-python`: Phân tích code Python
- `analyze-javascript`: Phân tích code JavaScript/TypeScript

### 4. Dependency Review (`dependency-review.yml`)
**Kích hoạt:** Pull Request đến `main` hoặc `develop`

**Chức năng:**
- Review dependencies mới được thêm vào PR
- Kiểm tra vulnerabilities và licenses
- Comment kết quả trên PR

**Các job:**
- `dependency-review`: Review và báo cáo vulnerabilities

### 5. Security Scan (`security-scan.yml`)
**Kích hoạt:**
- Push đến `main`
- Pull Request đến `main` hoặc `develop`
- Schedule: Hàng ngày lúc 3 AM UTC
- Manual dispatch

**Chức năng:**
- Quét vulnerabilities trong Python dependencies (pip-audit)
- Quét vulnerabilities trong Node.js dependencies (npm audit)
- Quét security issues trong code (bandit)

**Các job:**
- `pip-audit`: Audit Python dependencies (chỉ chạy trên main và schedule)
- `npm-audit`: Audit Node.js dependencies (chỉ chạy trên main và schedule)
- `bandit-scan`: Quét security issues trong Python code
- `summary`: Tổng hợp kết quả

**Lưu ý:** `pip-audit` và `npm-audit` không chạy trên PR để tránh làm chậm quá trình review.

### 6. Manual Project Review (`manual-project-review.yml`)
**Kích hoạt:** Manual dispatch (workflow_dispatch)

**Chức năng:**
- Chạy full review dự án với static analysis, tests, smoke tests
- Capture UI screenshots
- Tạo PR với review report và screenshots
- Tạo Issue để follow-up

**Parameters:**
- `ref`: Branch/tag/SHA để review (default: `main`)
- `create_pr`: Tạo PR với review results (default: `true`)
- `create_issue`: Tạo follow-up issue (default: `true`)
- `base_url`: Base URL cho frontend screenshots (default: `http://127.0.0.1:9081`)
- `include_ui_screenshots`: Capture UI screenshots (default: `true`)
- `smoke_auth_user`: Username cho smoke tests (default: `admin`)
- `smoke_auth_pass`: Password cho smoke tests (default: `admin123`)
- `issue_labels`: Labels cho issue được tạo (default: `audit,automation`)
- `pr_title`: Tiêu đề cho PR (default: `chore: automated review report + screenshots + docs refresh`)

**Các job:**
1. `audit-static-checks`: Chạy linting và security scan
2. `unit-integration-tests`: Chạy unit và integration tests
3. `boot-smoke-tests`: Boot services và chạy smoke tests
4. `ui-screenshots`: Capture UI screenshots (optional)
5. `doc-consistency-check`: Kiểm tra documentation consistency
6. `generate-report`: Tạo review report từ kết quả các jobs
7. `create-pr-and-issue`: Tạo PR và Issue với review results

**Workflow dependencies:**
```
audit-static-checks
    ├── unit-integration-tests
    │       ├── boot-smoke-tests
    │       │       └── ui-screenshots (optional)
    │       └── doc-consistency-check
    └── doc-consistency-check
            └── generate-report
                    └── create-pr-and-issue
```

## Các thay đổi đã thực hiện (2026-01-08)

### Vấn đề gốc
Workflow `manual-project-review.yml` không tự động tạo PR và Issue khi job `ui-screenshots` bị bỏ qua (khi `include_ui_screenshots = false`).

### Giải pháp
1. **Sửa job dependencies:**
   - Bỏ `ui-screenshots` khỏi `needs` của job `create-pr-and-issue`
   - Chỉ giữ lại `generate-report` trong `needs` list
   - Thêm điều kiện kiểm tra: `needs.generate-report.result != 'failure'`

2. **Cải thiện error handling:**
   - Thêm `continue-on-error: true` cho bước download artifacts trong `generate-report`
   - Download screenshots đã có `continue-on-error: true` sẵn

3. **Sửa YAML syntax error trong `security-scan.yml`:**
   - Sửa indentation của Python code trong job `pip-audit`
   - Sửa indentation của Node.js code trong job `npm-audit`
   - YAML parser yêu cầu code trong heredoc phải được indent đúng

### Trước khi sửa:
```yaml
needs: [generate-report, ui-screenshots]
if: |
  always() && 
  (github.event.inputs.create_pr == 'true' || github.event.inputs.create_issue == 'true')
```

### Sau khi sửa:
```yaml
needs: [generate-report]
if: |
  always() && 
  needs.generate-report.result != 'failure' &&
  (github.event.inputs.create_pr == 'true' || github.event.inputs.create_issue == 'true')
```

## Cách sử dụng Manual Project Review

### Cách 1: Qua GitHub UI
1. Vào tab **Actions** của repository
2. Chọn workflow **Manual Project Review & Release Audit**
3. Click **Run workflow**
4. Chọn các options:
   - Branch để review
   - Có tạo PR không
   - Có tạo Issue không
   - Có capture screenshots không
5. Click **Run workflow** để bắt đầu

### Cách 2: Qua GitHub CLI
```bash
gh workflow run manual-project-review.yml \
  -f ref=main \
  -f create_pr=true \
  -f create_issue=true \
  -f include_ui_screenshots=true
```

### Kết quả
Workflow sẽ:
1. Chạy tất cả các checks (lint, tests, smoke tests, etc.)
2. Tạo review report tại `docs/REVIEW_REPORT.md`
3. Capture screenshots (nếu enabled) tại `docs/screenshots/`
4. Tạo PR với review results và screenshots
5. Tạo Issue để track follow-up actions

## Best Practices

### Khi nào chạy Manual Project Review?
- Trước khi release phiên bản mới
- Sau khi merge nhiều PRs
- Định kỳ hàng tuần/tháng để track quality
- Khi cần audit toàn bộ dự án

### Cách xử lý kết quả
1. Review PR được tạo tự động
2. Download artifacts để xem chi tiết
3. Check Issue để track các vấn đề cần fix
4. Tạo focused PRs cho từng vấn đề tìm được
5. Close PR sau khi đã extract actionable items

### Lưu ý về Security Workflows
- CodeQL chạy tự động mỗi ngày và khi push đến main
- Security Scan có thể chạy manual bất cứ lúc nào
- Dependency Review tự động chạy trên mọi PR
- Nên check security alerts thường xuyên

## Troubleshooting

### Workflow bị fail
1. Check logs của job bị fail
2. Download artifacts để xem chi tiết
3. Chạy lại workflow nếu fail do network/timeout
4. Tạo issue nếu fail do bug trong workflow

### PR/Issue không được tạo
Kiểm tra:
- `create_pr` hoặc `create_issue` có được set thành `true` không?
- Job `generate-report` có chạy thành công không?
- Workflow có permissions `contents: write`, `pull-requests: write`, `issues: write` không?

### Workflow chạy quá lâu
- Bỏ qua UI screenshots nếu không cần: `include_ui_screenshots=false`
- Check timeout của từng job
- Có thể cần tăng timeout nếu tests chạy lâu

## Tài liệu tham khảo
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependency Review Action](https://github.com/actions/dependency-review-action)
