from api.email.service import EmailService


service = EmailService()

emails = service.get_unread_emails()

for email in emails:

    print("=" * 50)

    print(email.index)
    print(email.sender)
    print(email.subject)
    print(email.date)
    print(email.uid)