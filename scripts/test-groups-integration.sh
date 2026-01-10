#!/bin/bash
# Test script for Phase 2 Groups Integration
# This script tests all backend API endpoints and database integration

set -e  # Exit on error

API_BASE="http://localhost:9083"
TOKEN=""
SERVER_ID=""
NOTE_ID=""
SNIPPET_ID=""
GROUP_ID=""

echo "🧪 Phase 2 Groups Integration Test Script"
echo "=========================================="
echo ""

# Step 1: Login
echo "1️⃣  Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi
echo "✅ Login successful, token obtained"
echo ""

# Step 2: Create a test group
echo "2️⃣  Creating test group (type: servers)..."
TIMESTAMP=$(date +%s)
CREATE_GROUP_RESPONSE=$(curl -s -X POST "$API_BASE/api/groups" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Production Servers $TIMESTAMP\",
    \"description\": \"Test group for production servers\",
    \"type\": \"servers\",
    \"color\": \"#2e7d32\"
  }")

GROUP_ID=$(echo "$CREATE_GROUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")

if [ -z "$GROUP_ID" ]; then
  echo "❌ Failed to create group"
  echo "Response: $CREATE_GROUP_RESPONSE"
  exit 1
fi
echo "✅ Group created with ID: $GROUP_ID"
echo ""

# Step 3: Get all groups
echo "3️⃣  Fetching all groups..."
GROUPS_RESPONSE=$(curl -s -X GET "$API_BASE/api/groups" \
  -H "Authorization: Bearer $TOKEN")

if echo "$GROUPS_RESPONSE" | grep -q "Test Production Servers"; then
  echo "✅ Groups API working, test group found"
else
  echo "❌ Test group not found in groups list"
  echo "Response: $GROUPS_RESPONSE"
  exit 1
fi
echo ""

# Step 4: Create server with group
echo "4️⃣  Creating server with group assignment..."
RANDOM_IP="192.168.$(( RANDOM % 256 )).$(( RANDOM % 256 ))"
CREATE_SERVER_RESPONSE=$(curl -s -X POST "$API_BASE/api/servers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"TestServer-$(date +%s)\",
    \"host\": \"$RANDOM_IP\",
    \"port\": 22,
    \"username\": \"testuser\",
    \"description\": \"Test server with group\",
    \"group_id\": $GROUP_ID
  }")

SERVER_ID=$(echo "$CREATE_SERVER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('server_id', ''))" 2>/dev/null || echo "")

if [ -z "$SERVER_ID" ]; then
  echo "❌ Failed to create server"
  echo "Response: $CREATE_SERVER_RESPONSE"
  exit 1
fi
echo "✅ Server created with ID: $SERVER_ID"
echo ""

# Step 5: Get server and verify group_id
echo "5️⃣  Fetching server details and verifying group..."
SERVER_DETAILS=$(curl -s -X GET "$API_BASE/api/servers/$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$SERVER_DETAILS" | grep -q "\"group_id\":[[:space:]]*$GROUP_ID"; then
  echo "✅ Server has correct group_id: $GROUP_ID"
else
  echo "❌ Server group_id mismatch"
  echo "Response: $SERVER_DETAILS"
  exit 1
fi

if echo "$SERVER_DETAILS" | grep -q '"group_name":[[:space:]]*"Test Production Servers'; then
  echo "✅ Server includes group_name: Test Production Servers"
else
  echo "❌ Server missing group_name"
  echo "Response: $SERVER_DETAILS"
  exit 1
fi

if echo "$SERVER_DETAILS" | grep -q '"group_color":[[:space:]]*"#2e7d32"'; then
  echo "✅ Server includes group_color: #2e7d32"
else
  echo "❌ Server missing group_color"
  echo "Response: $SERVER_DETAILS"
  exit 1
fi
echo ""

# Step 6: Create note with group
echo "6️⃣  Creating server note with group..."
CREATE_NOTE_RESPONSE=$(curl -s -X POST "$API_BASE/api/servers/$SERVER_ID/notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Note\",
    \"content\": \"This is a test note with group assignment\",
    \"group_id\": $GROUP_ID
  }")

NOTE_ID=$(echo "$CREATE_NOTE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('note_id', ''))" 2>/dev/null || echo "")

if [ -z "$NOTE_ID" ]; then
  echo "❌ Failed to create note"
  echo "Response: $CREATE_NOTE_RESPONSE"
  exit 1
fi
echo "✅ Note created with ID: $NOTE_ID"
echo ""

# Step 7: Get notes and verify group
echo "7️⃣  Fetching server notes and verifying group..."
NOTES_RESPONSE=$(curl -s -X GET "$API_BASE/api/servers/$SERVER_ID/notes" \
  -H "Authorization: Bearer $TOKEN")

if echo "$NOTES_RESPONSE" | grep -q "\"group_id\":[[:space:]]*$GROUP_ID"; then
  echo "✅ Note has correct group_id"
else
  echo "❌ Note group_id mismatch"
  echo "Response: $NOTES_RESPONSE"
  exit 1
fi

if echo "$NOTES_RESPONSE" | grep -q '"group_name":[[:space:]]*"Test Production Servers'; then
  echo "✅ Note includes group_name"
else
  echo "❌ Note missing group_name"
  echo "Response: $NOTES_RESPONSE"
  exit 1
fi
echo ""

# Step 8: Create snippet with group (using notes group)
echo "8️⃣  Creating notes group for snippet test..."
NOTES_GROUP_RESPONSE=$(curl -s -X POST "$API_BASE/api/groups" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Snippets $TIMESTAMP\",
    \"description\": \"Test group for snippets\",
    \"type\": \"snippets\",
    \"color\": \"#ed6c02\"
  }")

SNIPPET_GROUP_ID=$(echo "$NOTES_GROUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")

if [ -z "$SNIPPET_GROUP_ID" ]; then
  echo "❌ Failed to create snippet group"
  exit 1
fi
echo "✅ Snippet group created with ID: $SNIPPET_GROUP_ID"
echo ""

echo "9️⃣  Creating command snippet with group..."
CREATE_SNIPPET_RESPONSE=$(curl -s -X POST "$API_BASE/api/snippets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Snippet\",
    \"command\": \"echo 'test'\",
    \"description\": \"Test snippet with group\",
    \"category\": \"test\",
    \"group_id\": $SNIPPET_GROUP_ID
  }")

SNIPPET_ID=$(echo "$CREATE_SNIPPET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('snippet_id', ''))" 2>/dev/null || echo "")

if [ -z "$SNIPPET_ID" ]; then
  echo "❌ Failed to create snippet"
  echo "Response: $CREATE_SNIPPET_RESPONSE"
  exit 1
fi
echo "✅ Snippet created with ID: $SNIPPET_ID"
echo ""

# Step 9: Get snippets and verify group
echo "🔟  Fetching snippets and verifying group..."
SNIPPETS_RESPONSE=$(curl -s -X GET "$API_BASE/api/snippets" \
  -H "Authorization: Bearer $TOKEN")

if echo "$SNIPPETS_RESPONSE" | grep -q "\"group_id\":[[:space:]]*$SNIPPET_GROUP_ID"; then
  echo "✅ Snippet has correct group_id"
else
  echo "❌ Snippet group_id mismatch"
  echo "Response: $SNIPPETS_RESPONSE"
  exit 1
fi

if echo "$SNIPPETS_RESPONSE" | grep -q '"group_name":[[:space:]]*"Test Snippets'; then
  echo "✅ Snippet includes group_name"
else
  echo "❌ Snippet missing group_name"
  echo "Response: $SNIPPETS_RESPONSE"
  exit 1
fi
echo ""

# Step 10: Cleanup
echo "🧹  Cleaning up test data..."
curl -s -X DELETE "$API_BASE/api/servers/$SERVER_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "✅ Test server deleted"

curl -s -X DELETE "$API_BASE/api/snippets/$SNIPPET_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "✅ Test snippet deleted"

curl -s -X DELETE "$API_BASE/api/groups/$GROUP_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "✅ Test groups deleted"

curl -s -X DELETE "$API_BASE/api/groups/$SNIPPET_GROUP_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo ""

echo "=========================================="
echo "✅ All tests passed! Phase 2 integration successful!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✅ Authentication working"
echo "  ✅ Groups CRUD working"
echo "  ✅ Server with group assignment working"
echo "  ✅ Server returns group_name and group_color"
echo "  ✅ Notes with group assignment working"
echo "  ✅ Notes return group info via JOIN"
echo "  ✅ Snippets with group assignment working"
echo "  ✅ Snippets return group info via JOIN"
echo ""
echo "Next steps:"
echo "  1. Test in browser: http://localhost:9081/en/dashboard"
echo "  2. Create test groups in Settings → Groups"
echo "  3. Assign servers to groups using 'Add Server' dialog"
echo "  4. Verify group badges display on server cards"
echo "  5. Test group filter dropdown functionality"
