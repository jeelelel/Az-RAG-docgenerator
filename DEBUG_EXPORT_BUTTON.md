# Document Export Debug Guide

## Summary of Changes Made
I've added comprehensive debugging to help identify why the export button remains disabled. The issue is in the condition at Draft.tsx line 55:

```tsx
if (isLoadedSections?.length === sections.length && title.length > 0) {
  setIsExportButtonDisable(false);  // Enable export
} else {
  setIsExportButtonDisable(true);   // Disable export
}
```

## Debug Information Added
- **Draft.tsx**: Console logs showing export button condition checks
- **SectionCard.tsx**: Tracking when sections load content and get added to isLoadedSections
- **TitleCard.tsx**: Tracking title changes
- Added automatic default title fallback

## Testing Steps

### 1. Start the Application
```bash
# Terminal 1 - Backend
cd src
python app.py

# Terminal 2 - Frontend  
cd src/frontend
npm run start
```

### 2. Test Document Generation Workflow
1. Navigate to http://localhost:3000
2. Go to **Generate** tab
3. Ask: "Generate a promissory note for $50,000"
4. Wait for AI response with sections
5. Click **"Generate Draft"** button
6. Navigate to **Draft** tab
7. **Open browser console** (F12 → Console tab)

### 3. Monitor Debug Output
Watch for these console messages:

#### Expected Success Flow:
```
🏷️ Setting document title from chat: "..."
📝 No title found, setting default title (if needed)
🔄 Section "Section Name" is empty, fetching content...
✅ Successfully generated content for section "Section Name"
📝 Adding section "Section Name" to loaded sections
✅ Section "Section Name" has content, adding to loaded sections
✅ Export button ENABLED - All conditions met
```

#### Problem Indicators:
```
❌ Export button DISABLED - Conditions not met
```

### 4. Common Issues & Solutions

#### Issue 1: Sections Not Loading
**Symptoms:** Console shows sections are empty, not generating content
**Solution:** Check backend is running on port 50505 and API endpoints work

#### Issue 2: Title Missing
**Symptoms:** `titleExists: false` in debug output
**Solution:** Manually enter a title in the Draft tab title field

#### Issue 3: isLoadedSections Not Matching
**Symptoms:** `sectionsAllLoaded: false` even when sections have content
**Solution:** Check if sections are being properly added to isLoadedSections array

## Quick Fix Option
If the debug shows sections have content but export is still disabled, you can temporarily force-enable it by modifying Draft.tsx line 55:

```tsx
// TEMPORARY FIX - Remove after debugging
setIsExportButtonDisable(false); // Always enable for testing
```

## Manual Test Steps
1. Generate a document in Generate tab
2. Click "Generate Draft"
3. In Draft tab, ensure:
   - Title field has content (type something if empty)
   - All section text areas have content (click Generate if empty)
   - Check console for debug messages
   - Export button should become enabled

## API Test
Test section generation directly:
```bash
curl -X POST http://localhost:50505/simple_section_generate \
  -H "Content-Type: application/json" \
  -d '{"sectionTitle": "Test", "sectionDescription": "Test description"}'
```

The debug information will help identify exactly where the workflow is breaking down!
