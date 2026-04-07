# Email Triage Simulation (OpenEnv)

This environment simulates a real-world email management task. An AI agent is tasked with triaging a mailbox, responding to urgent matters, and organizing folders.

## Motivation
Most LLM benchmarks focus on simple Q&A. This environment tests long-horizon reasoning, tool use (email actions), and decision-making in a professional context.

## Action Space
The agent can call the following actions:
- `ListEmails(folder)`: Returns a list of emails (id, sender, subject) in the folder.
- `GetEmail(email_id)`: Fetches the full body and details of an email.
- `ReplyEmail(email_id, body)`: Sends a reply and adds it to the SENT folder.
- `DeleteEmail(email_id)`: Moves the email to the TRASH folder.
- `MoveEmail(email_id, folder)`: Moves the email to ARCHIVE, SPAM, or other folders.

## Observation Space
- `emails`: List of email summaries.
- `email_content`: Detailed content of a single email.
- `message`: Human-readable status message.
- `success`: Boolean indicating if the action was successful.

## Tasks
| Task | ID | Difficulty | Description |
| :--- | :--- | :--- | :--- |
| **Spam Cleanup** | `spam_cleanup` | Easy | Clean the INBOX of all [SPAM] emails. |
| **Urgent Reply** | `urgent_reply` | Medium | Find an urgent email from the boss and confirm a meeting. |
| **Meeting Coordination** | `meeting_coord` | Hard | Coordinate multiple emails and clean up the mailbox. |

## Reward Function
- **Signal**: Baseline rewards for successful actions (+0.1 for delete, +0.2 for move, +0.5 for reply).
- **Partial Progress**: Graders score based on the percentage of target emails correctly handled.
- **Penalties**: -0.1 for invalid email IDs, -0.2 for unknown actions, -0.5 for exceptions.

## Setup & Usage

### Local Execution
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the environment server:
   ```bash
   python api.py
   ```

### Baseline Performance
To run the baseline agent (requires OpenAI API key):
```bash
export OPENAI_API_KEY="your-key"
python baseline.py
```

## Deployment
This environment is designed to run as a container on Hugging Face Spaces.
- Tag: `openenv`
- SDK: `docker`
