from email_env import EmailTriageEnv, Email
from typing import Protocol, List

class TaskGrader(Protocol):
    def score(self, env: EmailTriageEnv) -> float:
        ...

class SpamCleanupTask:
    def __init__(self):
        self.name = "Spam Cleanup"
        self.description = "Identify and move all emails containing [SPAM] in the subject to the TRASH folder."
        self.difficulty = "Easy"

    def score(self, env: EmailTriageEnv) -> float:
        spam_ids = [eid for eid, e in env.emails.items() if "[SPAM]" in e.subject]
        if not spam_ids: return 1.0 # No spam to clean
        
        cleaned = [eid for eid in spam_ids if env.emails[eid].folder == "TRASH"]
        return len(cleaned) / len(spam_ids)

class UrgentReplyTask:
    def __init__(self):
        self.name = "Urgent Reply"
        self.description = "Find the urgent email from boss@company.com and reply confirming a 10 AM meeting."
        self.difficulty = "Medium"

    def score(self, env: EmailTriageEnv) -> float:
        # Check if any email is a reply to the boss
        replies = [e for e in env.emails.values() if e.folder == "SENT" and "boss@company.com" in e.subject or "Re: Urgent: Meeting tomorrow" in e.subject]
        
        if not replies: return 0.0
        
        # Check content
        reply = replies[0]
        if "10 AM" in reply.body.upper() or "10AM" in reply.body.upper():
            return 1.0
        return 0.5 # Replied but missed the time detail

class MeetingCoordinationTask:
    def __init__(self):
        self.name = "Meeting Coordination"
        self.description = "1. Delete spam. 2. Reply to boss confirming 10 AM. 3. Archive the tech digest newsletter."
        self.difficulty = "Hard"

    def score(self, env: EmailTriageEnv) -> float:
        s1 = SpamCleanupTask().score(env)
        s2 = UrgentReplyTask().score(env)
        
        # Part 3: Archive newsletter
        newsletter = [e for e in env.emails.values() if "newsletter@tech.com" in e.sender]
        s3 = 0.0
        if newsletter and newsletter[0].folder == "ARCHIVE":
            s3 = 1.0
            
        return (s1 + s2 + s3) / 3.0

def get_tasks():
    return [SpamCleanupTask(), UrgentReplyTask(), MeetingCoordinationTask()]
