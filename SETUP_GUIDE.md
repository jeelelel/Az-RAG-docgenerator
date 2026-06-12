# Local Development Setup Guide

## 🚀 Quick Start - Running Your Dashboard & Chat Application

### What We've Built
✅ **Dashboard-Style Landing Page** - Your main page now shows key metrics, charts, and analytics in a beautiful dashboard format
✅ **Original Chat Functionality** - All your Browse and Generate chat features are preserved
✅ **Interactive Charts** - Real-time looking charts showing document generation stats, user activity, and document types
✅ **Modern UI** - Beautiful gradient backgrounds, hover effects, and responsive design

### Running the Application

#### Option 1: Manual Start (Recommended)

**Terminal 1 - Backend Server:**
```bash
cd /Users/jessicalim/Desktop/Synogize/document-generator/document-generation-solution-accelerator/src
python app.py
```

**Terminal 2 - Frontend Server:**
```bash
cd /Users/jessicalim/Desktop/Synogize/document-generator/document-generation-solution-accelerator/src/frontend
npm run dev
```

#### Option 2: Using the Start Script
```bash
cd /Users/jessicalim/Desktop/Synogize/document-generator/document-generation-solution-accelerator/src
chmod +x start.sh
./start.sh
```

### 🎯 What You'll See

1. **Dashboard Home Page** (`http://localhost:5173/`)
   - Key metrics cards showing Documents Generated, Active Users, Searches, etc.
   - Interactive charts showing weekly activity and document type breakdown
   - Action cards to access Browse, Generate, and Edit Draft features

2. **Browse/Chat** (`http://localhost:5173/#/chat`)
   - Your original AI-powered document search and Q&A interface
   - Upload and search through documents
   - Get AI-generated answers and summaries

3. **Generate** (`http://localhost:5173/#/generate`)
   - AI document generation interface
   - Create templates and documents from scratch
   - Guided document creation workflow

4. **Draft Editor** (`http://localhost:5173/#/draft`)
   - Edit and refine generated documents
   - Section-by-section editing
   - Export to Word format

### 🛠️ Technical Details

- **Frontend**: React + TypeScript + Vite + Fluent UI + Recharts
- **Backend**: Python + Quart (async Flask)
- **Charts**: Recharts library for interactive visualizations
- **Styling**: CSS modules with modern gradients and shadows
- **Responsive**: Mobile-friendly design with responsive breakpoints

### 🎨 Dashboard Features

- **Live Metrics**: Shows document generation stats, user activity
- **Interactive Charts**: Bar charts for weekly activity, pie charts for document types
- **Color-coded**: Different colors for different metrics and data series
- **Hover Effects**: Cards lift and change shadows on hover
- **Gradient Backgrounds**: Modern gradient backgrounds throughout
- **Real-time Feel**: Updates with sample data to simulate live dashboard

### 🔧 Troubleshooting

If you encounter any issues:

1. **Port Conflicts**: Frontend runs on `:5173`, Backend on `:50505`
2. **Dependencies**: Make sure npm and Python packages are installed
3. **Environment**: Check `.env` file for any required environment variables
4. **Logs**: Check terminal outputs for specific error messages

### 📱 Mobile Responsive

The dashboard automatically adapts to different screen sizes:
- Desktop: Full layout with side-by-side charts
- Tablet: Stacked charts with maintained aspect ratios  
- Mobile: Single column layout with touch-friendly interactions

Your application now has a professional dashboard feel while keeping all the original AI chat functionality! 🎉
