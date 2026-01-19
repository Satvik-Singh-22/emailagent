def fetch_recent_emails(service, max_results=5):
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()

        headers = {
            h["name"]: h["value"]
            for h in msg_data["payload"]["headers"]
        }

        emails.append({
            "id": msg["id"],
            "thread_id": msg_data["threadId"],
            "from": headers.get("From"),
            "subject": headers.get("Subject"),
        })

    return emails
