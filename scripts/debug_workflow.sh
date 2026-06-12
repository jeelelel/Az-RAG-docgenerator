#!/bin/bash

# Simple test script to verify the document generation workflow
echo "🚀 Testing Document Generation Workflow"
echo "======================================"

# Check if frontend and backend are running
echo "1. Checking if servers are running..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend server is running on port 3000"
else
    echo "❌ Frontend server is NOT running on port 3000"
    echo "   Please run: cd src/frontend && npm run start"
fi

if curl -s http://localhost:50505 > /dev/null; then
    echo "✅ Backend server is running on port 50505"
else
    echo "❌ Backend server is NOT running on port 50505"
    echo "   Please run: cd src && python app.py"
fi

echo ""
echo "2. Testing API endpoints..."

# Test the simple section generate endpoint
curl -s -X POST http://localhost:50505/simple_section_generate \
  -H "Content-Type: application/json" \
  -d '{"sectionTitle": "Test Section", "sectionDescription": "A test section for debugging"}' | \
  jq '.' > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Section generation endpoint is working"
else
    echo "❌ Section generation endpoint is not responding correctly"
fi

echo ""
echo "3. Next steps for testing:"
echo "   1. Go to http://localhost:3000"
echo "   2. Navigate to the Generate tab"
echo "   3. Ask: 'Generate a promissory note for $50,000'"
echo "   4. Wait for AI response"
echo "   5. Click 'Generate Draft' button"
echo "   6. Go to Draft tab"
echo "   7. Check browser console for debug information"
echo "   8. Verify sections are loading and title is set"
echo ""
echo "🐛 Debug info will appear in browser console with prefixes:"
echo "   🔄 - Section loading"
echo "   ✅ - Section loaded successfully"  
echo "   📝 - Title or section updates"
echo "   ❌ - Export button disabled"
echo "   ✅ - Export button enabled"
