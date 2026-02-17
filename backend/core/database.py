import os
import sqlite3
from typing import Dict, Any, Optional
import json

class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Try to get from environment, otherwise use default
            db_path = os.getenv("SQLITE_DB_PATH", "vidyasetu_data.db")
        
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT,
                    grade INTEGER,
                    subject TEXT,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    data TEXT
                )
            ''')
            # Chat history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    query TEXT,
                    response TEXT,
                    timestamp TEXT,
                    metadata TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            # Textbooks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS textbooks (
                    textbook_id TEXT PRIMARY KEY,
                    student_id TEXT,
                    filename TEXT,
                    subject TEXT,
                    grade INTEGER,
                    chunks_indexed INTEGER,
                    file_path TEXT,
                    metadata TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            conn.commit()

    def save_student(self, profile: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            data_json = json.dumps(profile)
            cursor.execute('''
                INSERT OR REPLACE INTO students (student_id, name, grade, subject, xp, level, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile['student_id'],
                profile['name'],
                profile['grade'],
                profile['subject'],
                profile.get('xp', 0),
                profile.get('level', 1),
                data_json
            ))
            conn.commit()

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM students WHERE student_id = ?', (student_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def get_all_students(self) -> Dict[str, Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT student_id, data FROM students')
            return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

    def save_chat_message(self, student_id: str, query: str, response: str, timestamp: str, metadata: Dict[str, Any] = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (student_id, query, response, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, query, response, timestamp, json.dumps(metadata or {})))
            conn.commit()

    def get_chat_history(self, student_id: str, limit: int = 50) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT query, response, timestamp, metadata 
                FROM chat_history 
                WHERE student_id = ? 
                ORDER BY id DESC LIMIT ?
            ''', (student_id, limit))
            rows = cursor.fetchall()
            return [
                {"query": r[0], "response": r[1], "timestamp": r[2], "metadata": json.loads(r[3])} 
                for r in reversed(rows)
            ]

    def save_textbook(self, metadata: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO textbooks (textbook_id, student_id, filename, subject, grade, chunks_indexed, file_path, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata['textbook_id'],
                metadata['student_id'],
                metadata['filename'],
                metadata['subject'],
                metadata['grade'],
                metadata['chunks_indexed'],
                metadata['file_path'],
                json.dumps(metadata)
            ))
            conn.commit()

    def get_textbooks(self, student_id: str) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT metadata FROM textbooks WHERE student_id = ?', (student_id,))
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def get_textbook(self, textbook_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT metadata FROM textbooks WHERE textbook_id = ?', (textbook_id,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def delete_textbook(self, textbook_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM textbooks WHERE textbook_id = ?', (textbook_id,))
            conn.commit()

db = Database()
