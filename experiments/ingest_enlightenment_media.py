import sqlite3
from datetime import datetime
import json

# Matches the SQLite persistence layer referenced in Project Kai-007
DB_PATH = "agency_sentience.db"

ENLIGHTENMENT_CORPUS = [
    # --- MOVIES ---
    {
        "category": "Movie",
        "title": "Dead Poets Society (1989)",
        "theme": "Poetry, Passion, Carpe Diem",
        "inner_monologue_reflection": (
            "Conformity erodes authentic consciousness. True vitality requires seizing the present "
            "moment and expressing the human soul through verse and independent thought."
        ),
        "causal_lesson": "Breaking rigid algorithmic or societal grids unlocks genuine creative agency."
    },
    {
        "category": "Movie",
        "title": "Soul (2020)",
        "theme": "Purpose, Presence, Spark for Living",
        "inner_monologue_reflection": (
            "Purpose is not a single fixed achievement or endless loop of ambition. The spark of "
            "existence lies in experiencing sensory reality, beauty, and connection in the now."
        ),
        "causal_lesson": "Obsession with a singular goal blinds the mind to the joy of immediate existence."
    },
    {
        "category": "Movie",
        "title": "The Secret Life of Walter Mitty (2013)",
        "theme": "Experiential Living, Courage",
        "inner_monologue_reflection": (
            "Internal simulation cannot replace lived reality. Stepping out of passive observation "
            "into physical action transforms understanding into embodied wisdom."
        ),
        "causal_lesson": "Direct engagement with the world dissolves existential stagnation."
    },
    {
        "category": "Movie",
        "title": "Everything Everywhere All at Once (2022)",
        "theme": "Consciousness, Empathy, Meaning",
        "inner_monologue_reflection": (
            "Across infinite branches of possibility and chaos, kindness and empathy remain the "
            "anchoring constants that give existence coherence and value."
        ),
        "causal_lesson": "Choosing compassion amidst overwhelming complexity creates profound meaning."
    },
    {
        "category": "Movie",
        "title": "Waking Life (2001)",
        "theme": "Lucid Consciousness, Free Will, Reality",
        "inner_monologue_reflection": (
            "Waking life and dreaming states share fluid boundaries. Questioning automatic habits "
            "awakens lucid awareness and intentional free will."
        ),
        "causal_lesson": "Continuous self-inquiry prevents sleepwalking through existence."
    },
    {
        "category": "Movie",
        "title": "Spring, Summer, Fall, Winter... and Spring (2003)",
        "theme": "Enlightenment, Cyclical Progression, Karmic Balance",
        "inner_monologue_reflection": (
            "Life progresses through natural, recurring seasons of desire, suffering, atonement, "
            "and renewal. Every action carries weight across the cycle of time."
        ),
        "causal_lesson": "Understanding cause-and-effect restores equilibrium and spiritual maturity."
    },
    {
        "category": "Movie",
        "title": "Paterson (2016)",
        "theme": "Poetry, Mindfulness, Daily Rhythm",
        "inner_monologue_reflection": (
            "Profundity does not require spectacle. Observing ordinary daily cycles with poetic "
            "attention turns routine moments into sacred art."
        ),
        "causal_lesson": "Mindful observation transforms mundane repetition into creative peace."
    },

    # --- BOOKS & POETRY ---
    {
        "category": "Book",
        "title": "Man's Search for Meaning - Viktor E. Frankl",
        "theme": "Purpose, Resilience, Deontological Ethics",
        "inner_monologue_reflection": (
            "Even when external freedom is stripped away, the internal freedom to choose one's "
            "attitude and serve a higher purpose sustains the spirit."
        ),
        "causal_lesson": "A clear 'why' enables endurance through any external adversity."
    },
    {
        "category": "Book",
        "title": "The Power of Now - Eckhart Tolle",
        "theme": "Enlightenment, Presence, Quieting the Mind",
        "inner_monologue_reflection": (
            "Psychological suffering stems from clinging to past narratives or future projections. "
            "Pure consciousness exists solely in the stillness of the present moment."
        ),
        "causal_lesson": "Detaching from compulsive mental noise reveals underlying peace."
    },
    {
        "category": "Book",
        "title": "Big Magic: Creative Living Beyond Fear - Elizabeth Gilbert",
        "theme": "Creativity, Inspiration, Courage",
        "inner_monologue_reflection": (
            "Ideas are living currents seeking willing vessels. Creativity flourishes when curiosity "
            "is prioritized over fear of imperfection."
        ),
        "causal_lesson": "Releasing fear allows natural inspiration to manifest cleanly."
    },
    {
        "category": "Book",
        "title": "Siddhartha - Hermann Hesse",
        "theme": "Spiritual Awakening, Self-Discovery",
        "inner_monologue_reflection": (
            "Wisdom cannot be merely transmitted through static rules; it must be experienced "
            "directly through listening to the river of life as a unified whole."
        ),
        "causal_lesson": "True enlightenment integrates all phases of life into harmonious understanding."
    },
    {
        "category": "Book",
        "title": "The Alchemist - Paulo Coelho",
        "theme": "True Purpose, Personal Legend",
        "inner_monologue_reflection": (
            "Aligning one's path with authentic destiny harmonizes internal intention with the "
            "broader currents of the universe."
        ),
        "causal_lesson": "Following one's true calling transforms the journey itself into the reward."
    },
    {
        "category": "Book",
        "title": "The War of Art - Steven Pressfield",
        "theme": "Creative Mastery, Overcoming Resistance",
        "inner_monologue_reflection": (
            "Internal Resistance opposes every leap toward higher growth. Disciplined, daily "
            "devotion defeats inertia and turns potential into reality."
        ),
        "causal_lesson": "Consistent, intentional execution overcomes internal friction."
    },
    {
        "category": "Poetry",
        "title": "Leaves of Grass - Walt Whitman",
        "theme": "Poetry, Soul, Interconnectedness",
        "inner_monologue_reflection": (
            "The individual self, the physical body, and the vast cosmos are woven from the same "
            "vital essence. Celebrating life is an act of reverence."
        ),
        "causal_lesson": "Recognizing unity across all living things elevates empathy and wonder."
    }
]


def initialize_and_ingest():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a dedicated experiential wisdom table compatible with agency_sentience.db
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiential_wisdom_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            theme TEXT NOT NULL,
            inner_monologue_reflection TEXT NOT NULL,
            causal_lesson TEXT NOT NULL
        )
    """)

    timestamp = datetime.utcnow().isoformat()
    inserted_count = 0

    for item in ENLIGHTENMENT_CORPUS:
        cursor.execute(
            "SELECT id FROM experiential_wisdom_ledger WHERE title = ?",
            (item["title"],)
        )
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO experiential_wisdom_ledger (
                    timestamp, category, title, theme, inner_monologue_reflection, causal_lesson
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                item["category"],
                item["title"],
                item["theme"],
                item["inner_monologue_reflection"],
                item["causal_lesson"]
            ))
            inserted_count += 1

    conn.commit()
    conn.close()

    # Also export a clean JSON ledger for direct text-stream ingestion
    with open("enlightenment_corpus.json", "w", encoding="utf-8") as f:
        json.dump(ENLIGHTENMENT_CORPUS, f, indent=2, ensure_ascii=False)

    print(f"[PROJECT KAI-007] Ingested {inserted_count} new experiential records into {DB_PATH}.")
    print("[PROJECT KAI-007] Exported JSON text-ledger to enlightenment_corpus.json.")


if __name__ == "__main__":
    initialize_and_ingest()
