"""
Storage utilities for saving and loading conversations
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config.settings import Settings


class ConversationStorage:
    """Handles saving and loading of conversations"""

    def __init__(self, db_path: str = None):
        """
        Initialize storage

        Args:
            db_path: Path to SQLite database (defaults to Settings.DATABASE_PATH)
        """
        self.db_path = db_path or Settings.DATABASE_PATH

        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    oncologist_type TEXT NOT NULL,
                    patient_type TEXT NOT NULL,
                    oncologist_model TEXT,
                    patient_model TEXT,
                    case_id TEXT,
                    case_title TEXT,
                    total_turns INTEGER,
                    conversation_data TEXT NOT NULL
                )
            """)

            # Create index on timestamp
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON conversations(timestamp DESC)
            """)

            conn.commit()

    def save_conversation(
        self,
        messages: List[Dict],
        oncologist_type: str,
        patient_type: str,
        oncologist_model: str,
        patient_model: str,
        case_id: Optional[str] = None,
        case_title: Optional[str] = None,
        statistics: Optional[Dict] = None
    ) -> int:
        """
        Save a conversation to the database

        Args:
            messages: List of message dictionaries
            oncologist_type: Type of oncologist (conservative/liberal)
            patient_type: Type of patient (do-more/do-less)
            oncologist_model: LLM model used for oncologist
            patient_model: LLM model used for patient
            case_id: Case ID if using pre-defined case
            case_title: Case title
            statistics: Conversation statistics

        Returns:
            ID of saved conversation
        """
        timestamp = datetime.now().isoformat()

        # Prepare conversation data
        conversation_data = {
            "messages": messages,
            "statistics": statistics or {}
        }

        total_turns = len([m for m in messages if m.get("role") == "patient"])

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO conversations (
                    timestamp, oncologist_type, patient_type,
                    oncologist_model, patient_model, case_id, case_title,
                    total_turns, conversation_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                oncologist_type,
                patient_type,
                oncologist_model,
                patient_model,
                case_id,
                case_title,
                total_turns,
                json.dumps(conversation_data)
            ))

            conn.commit()
            return cursor.lastrowid

    def load_conversation(self, conversation_id: int) -> Optional[Dict]:
        """
        Load a conversation by ID

        Args:
            conversation_id: ID of conversation to load

        Returns:
            Conversation data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT timestamp, oncologist_type, patient_type,
                       oncologist_model, patient_model, case_id, case_title,
                       total_turns, conversation_data
                FROM conversations
                WHERE id = ?
            """, (conversation_id,))

            row = cursor.fetchone()

            if not row:
                return None

            conversation_data = json.loads(row[8])

            return {
                "id": conversation_id,
                "timestamp": row[0],
                "oncologist_type": row[1],
                "patient_type": row[2],
                "oncologist_model": row[3],
                "patient_model": row[4],
                "case_id": row[5],
                "case_title": row[6],
                "total_turns": row[7],
                "messages": conversation_data.get("messages", []),
                "statistics": conversation_data.get("statistics", {})
            }

    def list_conversations(
        self,
        limit: int = 50,
        oncologist_type: Optional[str] = None,
        patient_type: Optional[str] = None
    ) -> List[Dict]:
        """
        List saved conversations

        Args:
            limit: Maximum number of conversations to return
            oncologist_type: Filter by oncologist type
            patient_type: Filter by patient type

        Returns:
            List of conversation metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT id, timestamp, oncologist_type, patient_type,
                       oncologist_model, patient_model, case_id, case_title, total_turns
                FROM conversations
                WHERE 1=1
            """
            params = []

            if oncologist_type:
                query += " AND oncologist_type = ?"
                params.append(oncologist_type)

            if patient_type:
                query += " AND patient_type = ?"
                params.append(patient_type)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "oncologist_type": row[2],
                    "patient_type": row[3],
                    "oncologist_model": row[4],
                    "patient_model": row[5],
                    "case_id": row[6],
                    "case_title": row[7],
                    "total_turns": row[8]
                }
                for row in rows
            ]

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a conversation

        Args:
            conversation_id: ID of conversation to delete

        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()

            return cursor.rowcount > 0

    def get_statistics(self) -> Dict:
        """
        Get overall statistics about saved conversations

        Returns:
            Dictionary of statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            cursor.execute("""
                SELECT oncologist_type, COUNT(*)
                FROM conversations
                GROUP BY oncologist_type
            """)
            oncologist_stats = dict(cursor.fetchall())

            cursor.execute("""
                SELECT patient_type, COUNT(*)
                FROM conversations
                GROUP BY patient_type
            """)
            patient_stats = dict(cursor.fetchall())

            return {
                "total_conversations": total_conversations,
                "by_oncologist_type": oncologist_stats,
                "by_patient_type": patient_stats
            }


# Create singleton instance
storage = ConversationStorage()
