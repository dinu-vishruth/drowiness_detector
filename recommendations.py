import pandas as pd
import numpy as np
from datetime import datetime, time
from database import Session, AlertEvent

def analyze_user_sessions(user_id):
    """
    Analyzes historical sessions for a given user using Pandas and returns a dictionary of insights.
    """
    # Fetch all sessions for this user from database
    sessions = Session.query.filter_by(user_id=user_id).order_by(Session.start_time.asc()).all()
    
    if len(sessions) < 2:
        return {
            "has_data": False,
            "message": "Not enough data yet. Complete at least 2 sessions to unlock personalized AI productivity insights!",
            "recommendations": [
                "Establish a baseline by monitoring your alertness for a few sessions at different times of day.",
                "Ensure you calibrate the sensitivity before each session for accurate reports.",
                "Use the cognitive and physical challenges to actively build resistance to afternoon fatigue."
            ],
            "peak_hours": "Unknown",
            "drowsiness_hours": "Unknown",
            "decay_minutes": 45
        }
        
    # Convert sessions to a list of dicts for Pandas DataFrame
    data = []
    for s in sessions:
        # Avoid zero division
        duration_mins = max(s.duration_seconds / 60.0, 0.1)
        data.append({
            "id": s.id,
            "start_time": s.start_time,
            "hour": s.start_time.hour,
            "duration_mins": duration_mins,
            "avg_alertness": s.avg_alertness,
            "yawns_count": s.yawns_count,
            "nods_count": s.nods_count,
            "alerts_count": s.alerts_count,
            "focus_score": s.focus_score,
            "alerts_per_hour": (s.alerts_count / duration_mins) * 60.0
        })
        
    df = pd.DataFrame(data)
    
    # 1. Peak Productivity Hours (Highest Focus, Lowest Alerts)
    # Group by hour
    by_hour = df.groupby('hour').agg({
        'focus_score': 'mean',
        'alerts_count': 'mean',
        'id': 'count'
    }).reset_index()
    
    # Find peak hour
    # Criteria: Focus score high, Alerts count low. We can rank them.
    by_hour['score_rank'] = by_hour['focus_score'].rank(ascending=False)
    by_hour['alert_rank'] = by_hour['alerts_count'].rank(ascending=True)
    by_hour['combined_rank'] = by_hour['score_rank'] + by_hour['alert_rank']
    
    best_hour_row = by_hour.loc[by_hour['combined_rank'].idxmin()]
    worst_hour_row = by_hour.loc[by_hour['combined_rank'].idxmax()]
    
    best_hour = int(best_hour_row['hour'])
    worst_hour = int(worst_hour_row['hour'])
    
    peak_time_str = f"{best_hour:02d}:00 - {(best_hour + 1)%24:02d}:00"
    drowsy_time_str = f"{worst_hour:02d}:00 - {(worst_hour + 1)%24:02d}:00"
    
    # 2. Alertness Decay Analysis
    # Let's see if longer sessions have lower average alertness
    # Correlate duration_mins with avg_alertness
    correlation = df['duration_mins'].corr(df['avg_alertness'])
    
    # Estimate fatigue onset point
    # We look at average alertness for sessions longer than 20 mins vs short ones,
    # or calculate a threshold. By default we suggest a break.
    decay_minutes = 45
    if len(df[df['duration_mins'] > 30]) > 0:
        # Check sessions
        long_sessions = df[df['duration_mins'] > 30]
        # Heuristic: if avg alertness is significantly lower in long sessions
        if long_sessions['avg_alertness'].mean() < df['avg_alertness'].mean() - 5:
            decay_minutes = 40
        else:
            decay_minutes = 50
            
    # Generate recommendations list
    recs = []
    
    # Time of day recommendations
    if 12 <= best_hour <= 15:
        recs.append(f"You demonstrate exceptionally high alertness and focus between 12 PM and 3 PM (Avg Focus Score: {best_hour_row['focus_score']:.1f}%). Leverage this window for complex, cognitive-heavy tasks.")
    elif 8 <= best_hour <= 11:
        recs.append(f"Your analytical peak occurs in the morning around {best_hour:02d}:00 AM. Plan your deepest study or development tasks early in the day.")
    else:
        recs.append(f"Your focus peaks during the session hours starting around {best_hour:02d}:00. Align your core work with this period.")
        
    if 13 <= worst_hour <= 16:
        recs.append(f"Frequent drowsiness events occur post-lunch between 1:00 PM and 4:00 PM. We recommend drinking 250ml of cold water and standing up for a brief stretch immediately before starting a session in this range.")
    elif worst_hour >= 22 or worst_hour <= 4:
        recs.append(f"Your alertness drops significantly during late-night sessions ({worst_hour:02d}:00). Consider capping late sessions at 30 minutes to prevent sleep deprivation cycles.")
    else:
        recs.append(f"Fatigue is most prominent around {worst_hour:02d}:00. Take proactive 5-minute active breaks to refresh your circulation.")
        
    # Duration recommendations
    if correlation < -0.3:
        recs.append(f"Data shows a strong negative correlation ({correlation:.2f}) between session duration and alertness. Your focus significantly decays after {decay_minutes} minutes. We recommend enforcing the Pomodoro technique (45m work, 5m break).")
    else:
        recs.append(f"Your focus decay curve is relatively stable, but to sustain long-term focus, a brief 5-minute walk or eye rest every 50 minutes is highly recommended.")
        
    # Yawning & Nodding correlations
    total_yawns = df['yawns_count'].sum()
    total_nods = df['nods_count'].sum()
    
    if total_yawns > 0 and total_nods > 0:
        yawn_nod_ratio = total_yawns / max(total_nods, 1)
        if yawn_nod_ratio > 1.5:
            recs.append("Analysis indicates yawning is your primary early warning sign. You yawn frequently before head nodding begins. When the first warning alert chimes, immediately drink water or take deep breaths to stop the transition into heavy drowsiness.")
        elif yawn_nod_ratio < 0.7:
            recs.append("You tend to experience sudden microsleeps (head nods) without prior warning yawning. Keep the camera calibration strict (higher sensitivity) so the system warns you at the very first sign of eye-droop.")
    
    # Alert response recommendation
    avg_alerts = df['alerts_count'].mean()
    if avg_alerts > 4:
        recs.append(f"You experience an average of {avg_alerts:.1f} alerts per session. Try configuring your room's airflow or lighting, as stuffy air directly triggers eye closure.")
        
    return {
        "has_data": True,
        "message": f"Successfully analyzed {len(sessions)} historical focus sessions.",
        "recommendations": recs,
        "peak_hours": peak_time_str,
        "drowsiness_hours": drowsy_time_str,
        "decay_minutes": decay_minutes
    }
