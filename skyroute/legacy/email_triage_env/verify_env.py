from email_env import EmailTriageEnv, Action, ListEmails, GetEmail
import sys

def verify_env():
    print("Verifying EmailTriageEnv...")
    try:
        env = EmailTriageEnv()
        obs = env.reset()
        assert obs.success == True
        assert len(obs.emails) > 0
        print("Reset successful.")

        # Test step
        action = Action(action=ListEmails(folder="INBOX"))
        obs, reward, done, info = env.step(action)
        assert obs.success == True
        print("Step (ListEmails) successful.")

        # Test GetEmail
        email_id = obs.emails[0]["id"]
        action = Action(action=GetEmail(email_id=email_id))
        obs, reward, done, info = env.step(action)
        assert obs.success == True
        assert obs.email_content["id"] == email_id
        print("Step (GetEmail) successful.")

        print("Verification PASSED.")
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_env()
