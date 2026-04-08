from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
import uuid

# --- Models ---

class Email(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    subject: str
    body: str
    folder: str = "INBOX"  # INBOX, SPAM, ARCHIVE, SENT
    is_read: bool = False

class ListEmails(BaseModel):
    folder: str = "INBOX"

class GetEmail(BaseModel):
    email_id: str

class ReplyEmail(BaseModel):
    email_id: str
    body: str

class DeleteEmail(BaseModel):
    email_id: str

class MoveEmail(BaseModel):
    email_id: str
    destination_folder: str

class Action(BaseModel):
    action_type: str
    args: Dict[str, Any] = {}

    def to_core_action(self) -> Union[ListEmails, GetEmail, ReplyEmail, DeleteEmail, MoveEmail]:
        if self.action_type == "ListEmails":
            return ListEmails(**self.args)
        elif self.action_type == "GetEmail":
            return GetEmail(**self.args)
        elif self.action_type == "ReplyEmail":
            return ReplyEmail(**self.args)
        elif self.action_type == "DeleteEmail":
            return DeleteEmail(**self.args)
        elif self.action_type == "MoveEmail":
            return MoveEmail(**self.args)
        raise ValueError(f"Unknown action type: {self.action_type}")

class Observation(BaseModel):
    emails: Optional[List[Dict[str, str]]] = None
    email_content: Optional[Dict[str, str]] = None
    message: str
    success: bool

class State(BaseModel):
    step_count: int
    current_folder: str
    mailbox_size: int

# --- Environment ---

class EmailTriageEnv:
    def __init__(self):
        self.emails: Dict[str, Email] = {}
        self.step_count = 0
        self.max_steps = 20
        self.done = False
        self._initialize_mailbox()

    def _initialize_mailbox(self):
        # Initial mock data for testing/reset
        initial_emails = [
            Email(sender="support@service.com", subject="Your Subscription", body="Your subscription is expiring soon. Renew now!"),
            Email(sender="spam_king@lottery.xxx", subject="[SPAM] YOU WON $1,000,000", body="Click here to claim your prize!"),
            Email(sender="boss@company.com", subject="Urgent: Meeting tomorrow", body="Hi, can you meet at 10 AM tomorrow to discuss the roadmap?"),
            Email(sender="newsletter@tech.com", subject="Weekly Tech Digest", body="Here are the top stories of the week."),
            Email(sender="phishing@scam.net", subject="[SPAM] Account Security Alert", body="Verify your login immediately at this suspicious link."),
        ]
        self.emails = {e.id: e for e in initial_emails}

    def reset(self) -> Observation:
        self.step_count = 0
        self.done = False
        self._initialize_mailbox()
        return Observation(
            message="Mailbox reset. You are in the INBOX.",
            success=True,
            emails=self._get_email_list("INBOX")
        )

    def _get_email_list(self, folder: str):
        return [
            {"id": e.id, "sender": e.sender, "subject": e.subject, "is_read": str(e.is_read)}
            for e in self.emails.values() if e.folder == folder
        ]

    def step(self, action_wrapper: Action) -> tuple[Observation, float, bool, dict]:
        self.step_count += 1
        reward = 0.0
        info = {}
        
        action = action_wrapper.to_core_action()
        
        if self.step_count >= self.max_steps:
            self.done = True

        try:
            if isinstance(action, ListEmails):
                emails = self._get_email_list(action.folder)
                obs = Observation(message=f"Listing emails in {action.folder}", success=True, emails=emails)
            
            elif isinstance(action, GetEmail):
                email = self.emails.get(action.email_id)
                if email:
                    email.is_read = True
                    obs = Observation(
                        message=f"Read email: {email.subject}", 
                        success=True, 
                        email_content={"id": email.id, "sender": email.sender, "subject": email.subject, "body": email.body}
                    )
                else:
                    obs = Observation(message="Email not found", success=False)
            
            elif isinstance(action, ReplyEmail):
                email = self.emails.get(action.email_id)
                if email:
                    # Logic for reply - create a record in SENT
                    sent_email = Email(sender="me@work.com", subject=f"Re: {email.subject}", body=action.body, folder="SENT")
                    self.emails[sent_email.id] = sent_email
                    obs = Observation(message=f"Replied to {email.sender}", success=True)
                    reward += 0.5 # Partial reward for replying
                else:
                    obs = Observation(message="Cannot reply to non-existent email", success=False)
                    reward -= 0.1 # Penalty for bad action

            elif isinstance(action, DeleteEmail):
                email = self.emails.get(action.email_id)
                if email:
                    email.folder = "TRASH"
                    obs = Observation(message=f"Moved email {email.id} to TRASH", success=True)
                    reward += 0.1
                else:
                    obs = Observation(message="Email not found", success=False)

            elif isinstance(action, MoveEmail):
                email = self.emails.get(action.email_id)
                if email:
                    email.folder = action.destination_folder
                    obs = Observation(message=f"Moved email to {action.destination_folder}", success=True)
                    reward += 0.2
                else:
                    obs = Observation(message="Email not found", success=False)
            
            else:
                obs = Observation(message="Unknown action type", success=False)
                reward -= 0.2

        except Exception as e:
            obs = Observation(message=f"Error: {str(e)}", success=False)
            reward -= 0.5

        return obs, reward, self.done, info

    def state(self) -> State:
        return State(
            step_count=self.step_count,
            current_folder="INBOX",
            mailbox_size=len([e for e in self.emails.values() if e.folder == "INBOX"])
        )
