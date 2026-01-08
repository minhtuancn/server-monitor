#!/bin/bash

###############################################################################
# Documentation Checker Script
# 
# Validates documentation consistency and checks for broken links
# Used by the manual-project-review workflow
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📚 Checking documentation consistency...${NC}"

# Track issues
ISSUES=0

# Documentation files to check
DOC_FILES=(
  "README.md"
  "DEPLOYMENT.md"
  "SECURITY.md"
  "ARCHITECTURE.md"
  "ROADMAP.md"
  "TODO-IMPROVEMENTS.md"
  "CONTRIBUTING.md"
  "TEST_GUIDE.md"
  "docs/PROJECT_SPECIFICATION.md"
  "docs/RELEASE_PROCESS.md"
  "docs/CI_WORKFLOWS.md"
)

echo -e "\n${BLUE}1. Checking if documentation files exist...${NC}"
for doc in "${DOC_FILES[@]}"; do
  if [ -f "$doc" ]; then
    echo -e "${GREEN}✅${NC} $doc"
  else
    echo -e "${RED}❌${NC} $doc (missing)"
    ((ISSUES++))
  fi
done

echo -e "\n${BLUE}2. Checking for broken internal links...${NC}"

# Function to check internal links
check_internal_links() {
  local file=$1
  local broken=0
  
  if [ ! -f "$file" ]; then
    return 0
  fi
  
  # Extract markdown links [text](path)
  # Filter for internal links (no http/https)
  while IFS= read -r link; do
    # Extract just the path from [text](path)
    local path=$(echo "$link" | sed -n 's/.*(\([^)]*\)).*/\1/p')

    # Skip non-file links that shouldn't be validated
    # - External URLs (http://, https://)
    # - Email addresses (mailto:)
    # - Internal anchors (#)
    # - Placeholder text (...)
    # - Empty paths
    if [[ "$path" =~ ^https?:// ]] || \
       [[ "$path" =~ ^mailto: ]] || \
       [[ "$path" =~ ^# ]] || \
       [[ "$path" == "..." ]] || \
       [[ -z "$path" ]]; then
      continue
    fi

    # Remove anchor from path
    local clean_path=$(echo "$path" | sed 's/#.*//')

    # Skip if empty after removing anchor
    if [ -z "$clean_path" ]; then
      continue
    fi

    # Resolve path relative to the file's directory
    local file_dir=$(dirname "$file")
    local resolved_path
    if [[ "$clean_path" = /* ]]; then
      # Absolute path
      resolved_path="$clean_path"
    else
      # Relative path - resolve relative to the file's directory
      resolved_path="$file_dir/$clean_path"
    fi

    # Check if file exists
    if [ ! -f "$resolved_path" ] && [ ! -d "$resolved_path" ]; then
      echo -e "${YELLOW}⚠️${NC}  Broken link in $file: $path"
      ((broken++))
    fi
  done < <(grep -o '\[.*\]([^)]*)' "$file" 2>/dev/null || true)

  return $broken
}

for doc in "${DOC_FILES[@]}"; do
  if [ -f "$doc" ]; then
    check_internal_links "$doc"
    if [ $? -gt 0 ]; then
      ((ISSUES++))
    fi
  fi
done

echo -e "\n${BLUE}3. Checking for TODO items in documentation...${NC}"
TODO_COUNT=$(grep -r "TODO\|FIXME\|XXX" README.md DEPLOYMENT.md SECURITY.md ARCHITECTURE.md 2>/dev/null | wc -l || echo "0")
echo -e "Found ${YELLOW}${TODO_COUNT}${NC} TODO/FIXME items in main documentation"

echo -e "\n${BLUE}4. Checking OpenAPI specification...${NC}"
if [ -f "docs/openapi.yaml" ]; then
  echo -e "${GREEN}✅${NC} docs/openapi.yaml exists"
  
  # Basic YAML validation
  if command -v python3 &> /dev/null; then
    python3 -c "import yaml; yaml.safe_load(open('docs/openapi.yaml'))" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅${NC} docs/openapi.yaml is valid YAML"
    else
      echo -e "${RED}❌${NC} docs/openapi.yaml has YAML syntax errors"
      ((ISSUES++))
    fi
  fi
else
  echo -e "${RED}❌${NC} docs/openapi.yaml missing"
  ((ISSUES++))
fi

echo -e "\n${BLUE}5. Checking for outdated version references...${NC}"

# Check if version in pyproject.toml matches README
if [ -f "pyproject.toml" ] && [ -f "README.md" ]; then
  PYPROJECT_VERSION=$(grep 'version = ' pyproject.toml | head -1 | sed 's/.*"\(.*\)".*/\1/')
  README_VERSION=$(grep -o 'version-[0-9.]*-blue' README.md | head -1 | sed 's/version-\(.*\)-blue/\1/')
  
  if [ -n "$PYPROJECT_VERSION" ] && [ -n "$README_VERSION" ]; then
    if [ "$PYPROJECT_VERSION" != "$README_VERSION" ]; then
      echo -e "${YELLOW}⚠️${NC}  Version mismatch: pyproject.toml ($PYPROJECT_VERSION) vs README.md ($README_VERSION)"
      ((ISSUES++))
    else
      echo -e "${GREEN}✅${NC} Version consistent: $PYPROJECT_VERSION"
    fi
  fi
fi

echo -e "\n${BLUE}6. Checking for empty documentation sections...${NC}"

# Check for markdown headers without content
for doc in "${DOC_FILES[@]}"; do
  if [ -f "$doc" ]; then
    EMPTY_SECTIONS=$(awk '/^#+ / {if (prev) print prev; prev=$0} /./ {if (!/^#+ /) prev=""} END {if (prev) print prev}' "$doc" 2>/dev/null | wc -l || echo "0")
    if [ "$EMPTY_SECTIONS" -gt 0 ]; then
      echo -e "${YELLOW}⚠️${NC}  $doc has $EMPTY_SECTIONS potentially empty sections"
    fi
  fi
done

# Summary
echo -e "\n=========================================="
echo -e "${BLUE}Documentation Check Summary${NC}"
echo -e "=========================================="

if [ $ISSUES -eq 0 ]; then
  echo -e "${GREEN}✅ No issues found!${NC}"
  exit 0
else
  echo -e "${YELLOW}⚠️  Found ${ISSUES} issue(s)${NC}"
  echo -e "Review the output above for details"
  exit 0  # Don't fail the workflow, just report
fi
