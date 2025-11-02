import json
from datetime import datetime

from emotional_os.parser.signal_parser import parse_input


# Save trace entry to JSON file
def save_trace_json(trace: dict, logs_dir: str = "logs/") -> None:
    timestamp = trace["timestamp"].replace(":", "-")
    filename = f"{logs_dir}trace_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    print(f"Trace saved to {filename}")

# Optional: Save trace to SQLite
def save_trace_sqlite(trace: dict, db_path: str = "glyphs.db") -> None:
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trace_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            input TEXT,
            signals TEXT,
            gates TEXT,
            glyphs TEXT,
            ritual_prompt TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO trace_log (timestamp, input, signals, gates, glyphs, ritual_prompt)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        trace["timestamp"],
        trace["input"],
        ", ".join(trace["signals"]),
        ", ".join(trace["gates"]),
        ", ".join([g["glyph_name"] for g in trace["glyphs"]]),
        trace["ritual_prompt"]
    ))

    conn.commit()
    conn.close()
    print("Trace saved to SQLite")

# Generate ritual prompt (can be expanded later)
def generate_prompt(glyphs: list) -> str:
    if not glyphs:
        return "No glyphs activated."
    return f"Would you like to mark this moment with {glyphs[0]['glyph_name']}?"

# Main trace function
def log_trace(input_text: str, lexicon_path: str = "velonix_lexicon.json") -> dict:
    parsed = parse_input(input_text, lexicon_path)
    parsed["timestamp"] = datetime.now().isoformat()
    parsed["ritual_prompt"] = generate_prompt(parsed["glyphs"])

    save_trace_json(parsed)
    save_trace_sqlite(parsed)
    return parsed

# Example usage
if __name__ == "__main__":
    input_text = input("Enter emotional input: ")
    trace = log_trace(input_text)
    print(json.dumps(trace, indent=2, ensure_ascii=False))
