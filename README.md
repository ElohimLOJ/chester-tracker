# 🤖 Chester Tracker

A beautiful task management app built specifically for tracking AI-assisted work with Apple's design language.

[![GitHub](https://img.shields.io/badge/GitHub-ElohimLOJ%2Fchester--tracker-blue?logo=github)](https://github.com/ElohimLOJ/chester-tracker) ![Chester Tracker](https://img.shields.io/badge/Status-Complete-brightgreen) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0.0-red) ![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🎨 **Apple Design Language**
- **SF Pro Display/Text fonts** for that authentic Apple feel
- **Native Apple color palette** (Apple Blue, Green, Orange, Red, etc.)
- **Dark mode interface** with proper contrast ratios  
- **Smooth animations** and hover effects

### 📱 **Sidebar Navigation**
- **Board view** - Kanban-style task management  
- **Dashboard view** - Comprehensive analytics
- **Projects list** - Auto-populated from your activities
- **Today's stats** - Quick glance at progress

### ⏱ **Time Tracking**
- **Live timers** - Start/stop tracking per task
- **Automatic status updates** - Task moves to "In Progress" when timer starts
- **Time accumulation** - Multiple timer sessions add up
- **Formatted display** - Shows hours and minutes clearly

### 🤖 **AI Tool Analytics**
- **Success rate tracking** - Compare Claude, ChatGPT, Copilot, etc.
- **Average time analysis** - See which tools are fastest
- **Iteration tracking** - How many attempts needed
- **Failure analysis** - Learn from what doesn't work

### 📊 **Rich Dashboard**
- **Overview stats** - Total activities, completion rates, time spent
- **Tool comparison** - Visual cards showing performance metrics
- **Project breakdown** - Bar charts of time allocation
- **Failure analysis** - Categorized reasons for debugging

### 🎯 **Outcome Tracking**
- **Success/Partial/Failed** ratings
- **Detailed notes** - What worked, what didn't
- **Failure categorization** - Wrong tool, poor prompt, complexity, etc.
- **Iteration counting** - Track refinement attempts

### 📤 **Export Options**
- **CSV export** - Raw data for spreadsheet analysis
- **Summary reports** - Formatted text reports with insights
- **Calendar integration** - ICS files for timeline viewing

### ⌨️ **Keyboard Shortcuts**
- **Cmd+N / Ctrl+N** - Create new activity
- **Escape** - Close modal/cancel

## 🚀 Quick Start

```bash
# Clone from GitHub
git clone https://github.com/ElohimLOJ/chester-tracker.git
cd chester-tracker

# Install dependencies
pip3 install -r requirements.txt

# Run the app
python3 app.py

# Open in browser
open http://127.0.0.1:5000
```

## 💡 Usage Guide

### **Creating Activities**
1. Click **"+ New Activity"** in the sidebar
2. Fill in the **title** and **description**
3. Select your **AI tool** (Claude, ChatGPT, etc.)
4. Add a **project name** for organization
5. Set initial **status** and **time spent**

### **Tracking Time**
- Click **"▶ Start"** to begin timing an activity
- The timer shows **live updates** every second
- Click **"⏹ Stop"** to pause and save time
- Times **accumulate** across multiple sessions

### **Managing Tasks**
- **Drag & drop** cards between columns (To Do → In Progress → Done)
- Use **"+1"** button to increment iteration count
- **Edit** tasks to add outcomes and notes
- **Delete** completed or cancelled tasks

### **Outcome Tracking**
- Set outcome to **Success**, **Partial**, or **Failed**
- Add **detailed notes** about what worked
- For failures, **categorize the reason** (wrong tool, poor prompt, etc.)
- Track **iterations** needed to get results

### **Analytics Dashboard**
- View **overall stats** - completion rates, time distribution
- **Compare AI tools** - success rates, average times, iteration counts
- **Project breakdown** - see where you're spending time
- **Failure analysis** - learn from what doesn't work

### **Exporting Data**
- **CSV export** - Import into Excel, Google Sheets, etc.
- **Summary report** - Text-based insights and statistics  
- **Calendar export** - View activities in timeline format

## 🗂 Project Structure

```
chester-tracker/
├── app.py              # Flask backend with all API endpoints
├── requirements.txt    # Python dependencies  
├── templates/
│   └── index.html      # Single-page app with Apple design
├── chester_tracker.db  # SQLite database (auto-created)
└── README.md          # This file
```

## 🛠 Technical Details

### **Backend**
- **Flask 3.0.0** - Lightweight Python web framework
- **SQLite** - Embedded database, no setup required
- **Flask-CORS** - Cross-origin resource sharing

### **Frontend**  
- **Vanilla JavaScript** - No frameworks, fast and lightweight
- **CSS Grid & Flexbox** - Modern responsive layouts
- **Apple Design System** - Authentic colors, fonts, and animations
- **Drag & Drop API** - Native browser functionality

### **Database Schema**
```sql
activities (
    id, title, description, ai_tool, project, status,
    position, time_spent, time_started, outcome, 
    outcome_notes, failure_reason, iteration_count,
    calendar_event_id, created_at, updated_at, completed_at
)
```

## 📈 Analytics Features

### **Tool Performance Metrics**
- **Success Rate** - % of activities marked as successful
- **Average Time** - How long tasks typically take  
- **Iteration Count** - How many refinements needed
- **Activity Volume** - Total tasks per tool

### **Project Insights**
- **Time Allocation** - Visual breakdown of where time goes
- **Completion Rates** - Which projects get finished
- **Activity Distribution** - Task count per project

### **Failure Analysis**
- **Common Failure Modes** - Most frequent issues
- **Tool-Specific Problems** - What fails with which AI
- **Learning Opportunities** - Improve prompting and tool selection

## 🎨 Design Philosophy

This app embodies **Apple's design principles**:

- **Clarity** - Every element has a clear purpose
- **Deference** - The content is the star, UI supports it  
- **Depth** - Visual layers and realistic motion provide vitality

The **dark theme** reduces eye strain during long work sessions, while the **Apple color palette** creates familiarity and trust.

## 🔮 Future Ideas

- **AI Integration** - Auto-categorize tasks and suggest tools
- **Team Collaboration** - Share insights across teams
- **Advanced Analytics** - Predict success rates, suggest improvements
- **Integrations** - Connect with Slack, GitHub, calendar apps
- **Mobile App** - Native iOS/Android versions

## 📝 License

This is your personal project. Use it however you'd like!

---

**Built with ❤️ and Claude**  
*Tracking AI productivity, one task at a time.*