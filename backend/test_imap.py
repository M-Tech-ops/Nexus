from api.email.imap_client import IMAPClient
from api.email.parser import EmailParser
from core.config import Config


def main():
    client = IMAPClient(
        server=Config.IMAP_SERVER,
        username=Config.EMAIL_ADDRESS,
        password=Config.EMAIL_PASSWORD,
        port=Config.IMAP_PORT,
    )

    try:
        print("Connecting to IMAP server...")
        client.connect()
        print("✅ Connected")

        client.select_inbox()
        print("✅ Inbox selected")

        # UID of the email you want to test
        uid = b"3425"

        print(f"Fetching email with UID: {uid.decode()}")

        raw_email = client.fetch_email(uid)

        msg = EmailParser.parse(raw_email)

        print("\n==============================")
        print("EMAIL METADATA")
        print("==============================")
        print(f"Subject : {EmailParser.subject(msg)}")
        print(f"Sender  : {EmailParser.sender(msg)}")
        print(f"Date    : {EmailParser.date(msg)}")

        print("\n==============================")
        print("EMAIL BODY")
        print("==============================")
        print(EmailParser.body(msg))

    except Exception as e:
        print(f"\n❌ Error: {e}")

    finally:
        client.disconnect()
        print("\nDisconnected.")


if __name__ == "__main__":
    main()