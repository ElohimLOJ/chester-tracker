from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import sqlite3
import csv
import io
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATABASE = 'chester_tracker.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            ai_tool TEXT,
            project TEXT,
            status TEXT DEFAULT 'todo',
            position INTEGER DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            time_started TIMESTAMP,
            outcome TEXT,
            outcome_notes TEXT,
            failure_reason TEXT,
            iteration_count INTEGER DEFAULT 1,
            calendar_event_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/activities', methods=['GET'])
def get_activities():
    conn = get_db()
    activities = conn.execute(
        'SELECT * FROM activities ORDER BY status, position'
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in activities])

@app.route('/api/activities', methods=['POST'])
def create_activity():
    data = request.json
    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO activities (title, description, ai_tool, project, status, position, time_spent, outcome, outcome_notes, failure_reason, iteration_count, calendar_event_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data.get('title'), data.get('description'), data.get('ai_tool'), 
         data.get('project'), data.get('status', 'todo'), data.get('position', 0),
         data.get('time_spent', 0), data.get('outcome'), data.get('outcome_notes'),
         data.get('failure_reason'), data.get('iteration_count', 1), 
         data.get('calendar_event_id'))
    )
    activity_id = cursor.lastrowid
    conn.commit()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (activity_id,)).fetchone()
    conn.close()
    return jsonify(dict(activity)), 201

@app.route('/api/activities/<int:id>', methods=['PUT'])
def update_activity(id):
    data = request.json
    conn = get_db()
    
    completed_at = None
    if data.get('status') == 'done':
        existing = conn.execute('SELECT status, completed_at FROM activities WHERE id = ?', (id,)).fetchone()
        if existing and existing['status'] != 'done':
            completed_at = datetime.now().isoformat()
        elif existing and existing['completed_at']:
            completed_at = existing['completed_at']
        else:
            completed_at = datetime.now().isoformat()
    
    conn.execute(
        '''UPDATE activities SET title = ?, description = ?, ai_tool = ?, project = ?, 
           status = ?, position = ?, time_spent = ?, outcome = ?, outcome_notes = ?, 
           failure_reason = ?, iteration_count = ?, calendar_event_id = ?, 
           updated_at = ?, completed_at = ? WHERE id = ?''',
        (data.get('title'), data.get('description'), data.get('ai_tool'),
         data.get('project'), data.get('status'), data.get('position'),
         data.get('time_spent', 0), data.get('outcome'), data.get('outcome_notes'),
         data.get('failure_reason'), data.get('iteration_count', 1),
         data.get('calendar_event_id'), datetime.now(), completed_at, id)
    )
    conn.commit()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(activity))

@app.route('/api/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    conn = get_db()
    conn.execute('DELETE FROM activities WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

@app.route('/api/activities/<int:id>/timer/start', methods=['POST'])
def start_timer(id):
    conn = get_db()
    conn.execute(
        'UPDATE activities SET time_started = ?, status = ? WHERE id = ?',
        (datetime.now().isoformat(), 'in-progress', id)
    )
    conn.commit()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(activity))

@app.route('/api/activities/<int:id>/timer/stop', methods=['POST'])
def stop_timer(id):
    conn = get_db()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (id,)).fetchone()
    
    if activity and activity['time_started']:
        started = datetime.fromisoformat(activity['time_started'])
        elapsed = int((datetime.now() - started).total_seconds())
        new_time = (activity['time_spent'] or 0) + elapsed
        
        conn.execute(
            'UPDATE activities SET time_spent = ?, time_started = NULL WHERE id = ?',
            (new_time, id)
        )
        conn.commit()
    
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(activity))

@app.route('/api/activities/<int:id>/iteration', methods=['POST'])
def increment_iteration(id):
    conn = get_db()
    conn.execute(
        'UPDATE activities SET iteration_count = iteration_count + 1 WHERE id = ?',
        (id,)
    )
    conn.commit()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(activity))

@app.route('/api/projects', methods=['GET'])
def get_projects():
    conn = get_db()
    projects = conn.execute('''
        SELECT project, COUNT(*) as count 
        FROM activities 
        WHERE project IS NOT NULL AND project != ""
        GROUP BY project 
        ORDER BY count DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in projects])

@app.route('/api/stats/today', methods=['GET'])
def get_today_stats():
    conn = get_db()
    today = datetime.now().date().isoformat()
    stats = conn.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
               SUM(time_spent) as time_spent
        FROM activities 
        WHERE date(created_at) = ? OR date(updated_at) = ?
    ''', (today, today)).fetchone()
    conn.close()
    return jsonify(dict(stats))

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    conn = get_db()
    days = int(request.args.get('days', 30))
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    total = conn.execute('SELECT COUNT(*) as count FROM activities').fetchone()['count']
    completed = conn.execute(
        'SELECT COUNT(*) as count FROM activities WHERE status = "done"'
    ).fetchone()['count']
    total_time = conn.execute(
        'SELECT SUM(time_spent) as total FROM activities'
    ).fetchone()['total'] or 0
    
    outcomes = conn.execute('''
        SELECT outcome, COUNT(*) as count 
        FROM activities 
        WHERE outcome IS NOT NULL AND outcome != ""
        GROUP BY outcome
    ''').fetchall()
    
    tool_stats = conn.execute('''
        SELECT ai_tool,
               COUNT(*) as total,
               SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
               SUM(CASE WHEN outcome = 'partial' THEN 1 ELSE 0 END) as partials,
               SUM(CASE WHEN outcome = 'failed' THEN 1 ELSE 0 END) as failures,
               SUM(time_spent) as total_time,
               AVG(time_spent) as avg_time,
               AVG(iteration_count) as avg_iterations
        FROM activities 
        WHERE ai_tool IS NOT NULL AND ai_tool != ""
        GROUP BY ai_tool
    ''').fetchall()
    
    failure_reasons = conn.execute('''
        SELECT failure_reason, COUNT(*) as count 
        FROM activities 
        WHERE failure_reason IS NOT NULL AND failure_reason != ""
        GROUP BY failure_reason 
        ORDER BY count DESC
    ''').fetchall()
    
    project_stats = conn.execute('''
        SELECT project,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
               SUM(time_spent) as total_time
        FROM activities 
        WHERE project IS NOT NULL AND project != ""
        GROUP BY project
    ''').fetchall()
    
    weekly_trend = conn.execute('''
        SELECT strftime('%Y-%W', created_at) as week,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
               SUM(time_spent) as total_time
        FROM activities 
        WHERE created_at >= date('now', '-56 days')
        GROUP BY week 
        ORDER BY week
    ''').fetchall()
    
    daily_activity = conn.execute('''
        SELECT date(created_at) as day, COUNT(*) as count 
        FROM activities 
        WHERE created_at >= date('now', '-30 days')
        GROUP BY day 
        ORDER BY day
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'overview': {
            'total': total,
            'completed': completed,
            'completion_rate': round(completed / total * 100, 1) if total > 0 else 0,
            'total_time': total_time,
            'avg_time': round(total_time / completed, 1) if completed > 0 else 0
        },
        'outcomes': [dict(row) for row in outcomes],
        'tool_stats': [dict(row) for row in tool_stats],
        'failure_reasons': [dict(row) for row in failure_reasons],
        'project_stats': [dict(row) for row in project_stats],
        'weekly_trend': [dict(row) for row in weekly_trend],
        'daily_activity': [dict(row) for row in daily_activity]
    })

@app.route('/api/analytics/tools', methods=['GET'])
def get_tool_comparison():
    conn = get_db()
    tool_comparison = conn.execute('''
        SELECT ai_tool,
               COUNT(*) as total_activities,
               SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
               SUM(CASE WHEN outcome = 'partial' THEN 1 ELSE 0 END) as partials,
               SUM(CASE WHEN outcome = 'failed' THEN 1 ELSE 0 END) as failures,
               ROUND(SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(CASE WHEN outcome IS NOT NULL AND outcome != '' THEN 1 END), 0), 1) as success_rate,
               SUM(time_spent) as total_time,
               ROUND(AVG(time_spent), 0) as avg_time,
               ROUND(AVG(iteration_count), 1) as avg_iterations,
               MIN(time_spent) as min_time,
               MAX(time_spent) as max_time
        FROM activities 
        WHERE ai_tool IS NOT NULL AND ai_tool != ""
        GROUP BY ai_tool 
        ORDER BY total_activities DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in tool_comparison])

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    conn = get_db()
    activities = conn.execute('''
        SELECT id, title, description, ai_tool, project, status, time_spent, 
               outcome, outcome_notes, failure_reason, iteration_count, 
               created_at, completed_at
        FROM activities 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Title', 'Description', 'AI Tool', 'Project', 'Status',
        'Time Spent (seconds)', 'Time Spent (formatted)', 'Outcome',
        'Outcome Notes', 'Failure Reason', 'Iterations', 'Created', 'Completed'
    ])
    
    for activity in activities:
        time_spent = activity['time_spent'] or 0
        hours = time_spent // 3600
        minutes = (time_spent % 3600) // 60
        time_formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        writer.writerow([
            activity['id'], activity['title'], activity['description'],
            activity['ai_tool'], activity['project'], activity['status'],
            time_spent, time_formatted, activity['outcome'],
            activity['outcome_notes'], activity['failure_reason'],
            activity['iteration_count'], activity['created_at'],
            activity['completed_at']
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=chester_tracker_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

@app.route('/api/export/report', methods=['GET'])
def export_report():
    conn = get_db()
    
    overview = conn.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
               SUM(time_spent) as total_time,
               AVG(CASE WHEN status = 'done' THEN time_spent END) as avg_time
        FROM activities
    ''').fetchone()
    
    tool_stats = conn.execute('''
        SELECT ai_tool,
               COUNT(*) as total,
               SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
               ROUND(SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) * 100.0 / 
                     NULLIF(COUNT(CASE WHEN outcome IS NOT NULL AND outcome != '' THEN 1 END), 0), 1) as success_rate,
               SUM(time_spent) as total_time
        FROM activities 
        WHERE ai_tool IS NOT NULL AND ai_tool != ""
        GROUP BY ai_tool
    ''').fetchall()
    
    project_stats = conn.execute('''
        SELECT project,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed,
               SUM(time_spent) as total_time
        FROM activities 
        WHERE project IS NOT NULL AND project != ""
        GROUP BY project
    ''').fetchall()
    
    conn.close()
    
    def format_time(seconds):
        if not seconds:
            return "0m"
        hours = int(seconds) // 3600
        minutes = (int(seconds) % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    report = []
    report.append("=" * 60)
    report.append("NINIOLA - CHESTER TRACKER - SUMMARY REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    report.append("")
    
    report.append("OVERVIEW")
    report.append("-" * 40)
    report.append(f"Total Activities: {overview['total']}")
    report.append(f"Completed: {overview['completed']}")
    report.append(f"Completion Rate: {round(overview['completed'] / overview['total'] * 100, 1) if overview['total'] > 0 else 0}%")
    report.append(f"Total Time Tracked: {format_time(overview['total_time'])}")
    report.append(f"Avg Time per Task: {format_time(overview['avg_time'])}")
    report.append("")
    
    report.append("TOOL PERFORMANCE")
    report.append("-" * 40)
    for tool in tool_stats:
        report.append(f"  {tool['ai_tool']}:")
        report.append(f"    Activities: {tool['total']}")
        report.append(f"    Success Rate: {tool['success_rate'] or 0}%")
        report.append(f"    Time Spent: {format_time(tool['total_time'])}")
        report.append("")
    
    report.append("PROJECT BREAKDOWN")
    report.append("-" * 40)
    for project in project_stats:
        report.append(f"  {project['project']}:")
        report.append(f"    Activities: {project['total']}")
        report.append(f"    Completed: {project['completed']}")
        report.append(f"    Time Spent: {format_time(project['total_time'])}")
        report.append("")
    
    report.append("=" * 60)
    
    return Response(
        "\n".join(report),
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename=chester_report_{datetime.now().strftime("%Y%m%d")}.txt'}
    )

@app.route('/api/calendar/ics', methods=['GET'])
def export_ics():
    conn = get_db()
    activities = conn.execute('''
        SELECT * FROM activities 
        WHERE created_at >= date('now', '-30 days')
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Niniola Chester Tracker//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    for activity in activities:
        created = datetime.fromisoformat(activity['created_at'].replace(' ', 'T'))
        duration = activity['time_spent'] or 1800
        end = created + timedelta(seconds=duration)
        
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{activity['id']}@chester-tracker",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{created.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:[{activity['ai_tool'] or 'AI'}] {activity['title']}",
            f"DESCRIPTION:Project: {activity['project'] or 'N/A'}\\nOutcome: {activity['outcome'] or 'N/A'}\\nIterations: {activity['iteration_count']}",
            f"CATEGORIES:{activity['ai_tool'] or 'AI'},{activity['project'] or 'General'}",
            "END:VEVENT"
        ])
    
    ics_lines.append("END:VCALENDAR")
    
    return Response(
        "\r\n".join(ics_lines),
        mimetype='text/calendar',
        headers={'Content-Disposition': 'attachment; filename=chester_activities.ics'}
    )

@app.route('/api/calendar/import', methods=['POST'])
def import_from_calendar():
    data = request.json
    events = data.get('events', [])
    
    conn = get_db()
    imported = 0
    
    for event in events:
        existing = conn.execute(
            'SELECT id FROM activities WHERE calendar_event_id = ?',
            (event.get('id'),)
        ).fetchone()
        
        if not existing:
            conn.execute(
                '''INSERT INTO activities (title, description, ai_tool, project, status, calendar_event_id, created_at)
                   VALUES (?, ?, ?, ?, 'todo', ?, ?)''',
                (event.get('title'), event.get('description'), event.get('ai_tool'),
                 event.get('project'), event.get('id'), event.get('start'))
            )
            imported += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'imported': imported})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)