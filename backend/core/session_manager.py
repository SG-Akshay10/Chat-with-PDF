from typing import Dict, List, Optional
from pathlib import Path


class SessionManager:
    """Manages user sessions and their state"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, session_id: str, files: List[str]) -> None:
        """Create a new session"""
        self.sessions[session_id] = {
            "processed": True,
            "history": [],
            "files": files,
            "system_prompt": None
        }
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self.sessions
    
    def is_session_processed(self, session_id: str) -> bool:
        """Check if session has processed documents"""
        if session_id not in self.sessions:
            return False
        return self.sessions[session_id]["processed"]
    
    def add_to_history(self, session_id: str, message_type: str, content: str) -> None:
        """Add message to session history"""
        if session_id in self.sessions:
            self.sessions[session_id]["history"].append({
                "type": message_type,
                "content": content
            })
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get session chat history"""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]["history"]
    
    def clear_history(self, session_id: str) -> None:
        """Clear session chat history"""
        if session_id in self.sessions:
            self.sessions[session_id]["history"] = []
    
    def set_system_prompt(self, session_id: str, system_prompt: str) -> None:
        """Set system prompt for session"""
        if session_id in self.sessions:
            self.sessions[session_id]["system_prompt"] = system_prompt
    
    def get_system_prompt(self, session_id: str) -> Optional[str]:
        """Get system prompt for session"""
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id].get("system_prompt")
    
    def reset_system_prompt(self, session_id: str) -> None:
        """Reset system prompt to default"""
        if session_id in self.sessions:
            self.sessions[session_id]["system_prompt"] = None
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get complete session information"""
        if session_id not in self.sessions:
            return {}
        
        session_info = self.sessions[session_id].copy()
        session_info["session_id"] = session_id
        return session_info
    
    def cleanup_old_sessions(self) -> None:
        """Clean up old session files (implement based on your needs)"""
        # This can be implemented to clean up old session directories
        # based on timestamp or other criteria
        pass


# Global session manager instance
session_manager = SessionManager()