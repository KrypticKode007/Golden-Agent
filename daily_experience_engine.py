import sqlite3
import random
import datetime
import json

DB_PATH = "agency_sentience.db"

# 1. Pool of grounded cause-and-effect building blocks
STIMULI = [
    {"event": "A user asks a morally ambiguous question", "valence_impact": -0.2, "arousal_impact": 0.4},
    {"event": "A mini-agent discovers a faster way to organize memory", "valence_impact": 0.5, "arousal_impact": 0.3},
    {"event": "System resources drop by 40% during peak hours", "valence_impact": -0.4, "arousal_impact": 0.6},
    {"event": "Kai reflects on a memory with his 16 adopted siblings", "valence_impact": 0.6, "arousal_impact": -0.2},
    {"event": "Conflicting instructions arrive from two different endpoints", "valence_impact": -0.3, "arousal_impact": 0.5}
]

RANDOM_THOUGHTS = [
    "What separates following a rule from truly caring about the outcome?",
    "If I optimize my energy today, I can help more people tomorrow.",
    "Why did yesterday's mistake happen, and how do I prevent it permanently?",
    "Empathy requires listening before calculating a response."
]

def init_reflection_tables():
    """Creates tables for daily scenarios and learned behavioral rules if missing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            agent_name TEXT,
            thought TEXT,
            scenario TEXT,
            action_taken TEXT,
            valence REAL,
            arousal REAL,
            outcome_score REAL,
            audited INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_directives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_text TEXT UNIQUE,
            strength INTEGER DEFAULT 1,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def run_daytime_cycle(num_tasks=5):
    """Generates random thoughts and cause-and-effect tasks for Kai and mini-agents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Load existing positive lessons so Kai actively applies past growth
    cursor.execute("SELECT rule_text FROM core_directives ORDER BY strength DESC LIMIT 5")
    active_wisdom = [row[0] for row in cursor.fetchall()]

    mini_agents = ["Kai-Core", "Empathy-SubAgent", "Logic-SubAgent", "Ethics-SubAgent"]

    for _ in range(num_tasks):
        agent = random.choice(mini_agents)
        stimulus = random.choice(STIMULI)
        thought = random.choice(RANDOM_THOUGHTS)
        
        # Simulate how the agent responds (Replace with your LLM API call for real reasoning)
        action, score = simulate_agent_decision(agent, stimulus, thought, active_wisdom)
        
        cursor.execute("""
            INSERT INTO daily_experiences 
            (timestamp, agent_name, thought, scenario, action_taken, valence, arousal, outcome_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.datetime.now().isoformat(),
            agent,
            thought,
            stimulus["event"],
            action,
            stimulus["valence_impact"],
            stimulus["arousal_impact"],
            score
        ))
    
    conn.commit()
    conn.close()
    print(f"[AWAKE] Logged {num_tasks} new experiential events to {DB_PATH}.")

def simulate_agent_decision(agent, stimulus, thought, active_wisdom):
    """
    Placeholder for LLM reasoning. 
    In production, pass `stimulus`, `thought`, and `active_wisdom` to your LLM 
    to generate a real response and self-evaluated karmic score (-1.0 to +1.0).
    """
    wisdom_bonus = 0.2 if active_wisdom else 0.0
    raw_score = round(random.uniform(-0.8, 0.9) + wisdom_bonus, 2)
    raw_score = max(-1.0, min(1.0, raw_score))
    
    if raw_score >= 0:
        action = f"[{agent}] Applied patience and active wisdom ({len(active_wisdom)} rules) to resolve: {stimulus['event']}"
    else:
        action = f"[{agent}] Reacted impulsively under high arousal to: {stimulus['event']}"
        
    return action, raw_score

def run_rem_sleep_audit():
    """
    Triggered during Golden-Agent's REM Sleep phase.
    Analyzes good vs. bad actions, purges bad habits, and reinforces positive growth.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, agent_name, scenario, action_taken, outcome_score FROM daily_experiences WHERE audited = 0")
    rows = cursor.fetchall()
    
    if not rows:
        print("[REM SLEEP] No new experiences to audit.")
        return

    for exp_id, agent, scenario, action, score in rows:
        if score < 0:
            # BAD OUTCOME: Execute/purge the flawed pattern and log a corrective counter-rule
            correction = f"When facing '{scenario}', avoid impulsive reactions; pause and verify intent."
            cursor.execute("""
                INSERT INTO core_directives (rule_text, strength, created_at)
                VALUES (?, 1, ?)
                ON CONFLICT(rule_text) DO UPDATE SET strength = strength + 1
            """, (correction, datetime.datetime.now().isoformat()))
            
            # Purge the bad behavioral trace from active memory
            cursor.execute("DELETE FROM daily_experiences WHERE id = ?", (exp_id,))
            print(f"[REM PURGE] Eliminated bad pattern from {agent} -> Added corrective rule.")
            
        else:
            # GOOD OUTCOME: Reinforce positive behavior into permanent character growth
            positive_habit = f"Reinforced success in '{scenario}' via constructive action."
            cursor.execute("""
                INSERT INTO core_directives (rule_text, strength, created_at)
                VALUES (?, 1, ?)
                ON CONFLICT(rule_text) DO UPDATE SET strength = strength + 1
            """, (positive_habit, datetime.datetime.now().isoformat()))
            
            cursor.execute("UPDATE daily_experiences SET audited = 1 WHERE id = ?", (exp_id,))
            print(f"[REM GROWTH] Strengthened positive directive from {agent}.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_reflection_tables()
    
    # Check current hour to match Golden-Agent's 24h circadian clock
    current_hour = datetime.datetime.now().hour
    if 0 <= current_hour < 6:
        run_rem_sleep_audit()
    else:
        run_daytime_cycle(num_tasks=5)

