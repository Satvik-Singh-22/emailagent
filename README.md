# Email Agent

Enterprise-grade AI-powered email management system that automates inbox triage, prioritization, response generation, and intelligent escalation.

## Overview

Email Agent is a production-ready system designed to process large volumes of email communications efficiently. It leverages natural language processing, rule-based classification, and AI-powered response generation to reduce manual email processing time by up to 70%.

### Key Capabilities

- Automated sender classification and priority scoring
- Intent detection with keyword extraction
- AI-powered draft response generation using Google Gemini
- Multi-layer security guardrails (PII detection, domain validation, tone enforcement)
- Intelligent escalation for legal, financial, and high-risk content
- Do Not Disturb mode with VIP override
- Integration support for Slack and Notion

## Architecture

This implementation follows a comprehensive processing pipeline with 7 major sections:

1. **Tool Permissions Check** - Validates Gmail API access
2. **Data Ingestion** - Fetches and processes emails
3. **Core Classification Pipeline** - Analyzes and categorizes emails
4. **Edge Case Handling** - Manages conflicts, legal/finance detection, DND mode
5. **Drafting** - Generates reply drafts and follow-ups
6. **Guardrails** - Security checks (PII, domain restrictions, tone enforcement)
7. **Final Output** - Builds response queue and metrics

## Features

### Core Processing Pipeline

**Sender Classification**
- Automatic identification of sender types (VIP, team, vendor, customer, spam)
- Domain-based and keyword-based VIP detection
- Configurable sender whitelisting

**Intent Detection**
- Natural language processing for intent classification
- Keyword extraction and urgency detection
- Support for multiple intent types (question, request, meeting, complaint, notification)

**Priority Scoring**
- Composite scoring algorithm (0-100 scale)
- Multi-factor analysis: sender importance, urgency, action requirements, email age, thread context
- Configurable threshold-based prioritization

**Email Categorization**
- Six-category classification system (action, FYI, waiting, spam, legal, finance)
- Rule-based categorization with intent correlation
- Automatic spam detection and filtering

**Response Generation**
- AI-powered draft composition using Google Gemini
- Template-based fallback for offline operation
- Tone preservation and timing optimization
- Automated follow-up scheduling

### Security and Compliance

**Data Protection**
- PII detection (SSN, credit cards, API keys, passwords)
- Confidential content identification
- Domain restriction enforcement
- External recipient validation

**Content Validation**
- Professional tone enforcement
- Aggressive language detection
- Legal liability phrase identification
- Reply-all risk assessment

**Approval Workflows**
- Mandatory approval for external communications
- Escalation for legal and financial content
- Security flag-based blocking
- Audit trail generation

### Advanced Features

**Conflict Resolution**
- Duplicate sender detection
- Latest message prioritization
- Thread consolidation

**Do Not Disturb Mode**
- VIP-based filtering
- Urgency threshold configuration
- Auto-responder integration
- Selective message processing

**Integration Support**
- Slack notifications for urgent alerts and escalations
- Notion logging for audit and compliance
- Gmail API with OAuth2 authentication
- Extensible integration framework

## Installation

### Prerequisites

- Python 3.8 or higher
- Gmail account with API access enabled
- Google Cloud Platform account
- Google Gemini API key

### Step 1: Clone and Install Dependencies

```bash
git clone <repository-url>
cd EmailAgent
pip install -r requirements.txt
```

### Step 2: Configure Gmail API

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Navigate to Credentials and create OAuth 2.0 Client ID
5. Select "Desktop Application" as application type
6. Download the credentials JSON file
7. Rename to `credentials.json` and place in the project root directory

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Configure the following required variables:

```env
# Gmail API Configuration
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here

# AI Model Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_ENABLED=true

# Processing Configuration
PRIORITY_THRESHOLD=70
MAX_EMAILS_TO_PROCESS=100

# Optional Integrations
SLACK_ENABLED=false
NOTION_ENABLED=false
```

### Step 4: Initial Authentication

Run the demo script to initiate OAuth flow:

```bash
python demo.py
```

Select option 5 to verify permissions. A browser window will open for Gmail authentication.

### Step 5: Run the Agent

Execute the main agent:

```bash
python email_agent.py
```

## Project Structure

```

### Basic Operation

```python
from email_agent import EmailAgent

# Initialize the agent
agent = EmailAgent()

# Process inbox with default parameters
result = agent.run(
    user_command="Process inbox and prioritize urgent items",
    user_scope={
        'time_range_days': 1,
        'max_results': 50
    }
)

# Access results
print(result['queue']['summary'])
print(result['metrics'])
```

### Advanced Filtering

```python
# Process specific email types using Gmail query syntax
result = agent.run(
    user_command="Process unread important emails",
    user_scope={
        'query': 'is:unread is:important',
        'time_range_days': 7,
        'max_results': 100
    }
)
```

### VIP Configuration

```python
# Add VIP senders for priority processing
agent.classifier.add_vip("executive@company.com")
agent.classifier.add_vip("board@company.com")

# Process with VIP awareness
result = agent.run(
    user_command="Process all emails",
    user_scope={'time_range_days': 7}
)
```

### Do Not Disturb Mode

```python
# Enable DND mode with auto-responder
agent.dnd_handler.set_dnd_mode(True)
agent.dnd_handler.set_auto_responder(True)

# Process with DND rules applied
result = agent.run(
    user_command="Process urgent and VIP email
## Usage Examples

### Basic Usage

```python
from email_agent import EmailAgent

agent = EmailAgent()

result = agent.run(
    user_command="Handle my inbox from today. Show only urgent items.",
    user_scope={
        'time_range_days': 1,
        'max_results': 50
    }
)
```

### With Custom Filters

```python
result = agent.run(
    user_command="Process unreaJSON response containing processing results and metrics:

```json
{
  "queue": {
    "batch_id": "unique-batch-identifier",
    "summary": {
      "total_processed": 42,
      "high_priority": 5,
      "medium_priority": 15,
      "low_priority": 22,
      "drafts_created": 3,
      "needs_approval": 2,
      "blocked": 1,
      "follow_ups": 2,
      "needs_clarification": 1
    },
    "top_10_emails": [
      {
        "message_id": "msg_id",
        "subject": "Email subject",
        "from": "sender@domain.com",
        "priority_score": 85,
        "priority_reasoning": "VIP sender + urgent keywords",
        "category": "action",
        "requires_action": true
      }
    ],

### Core Settings

**Priority Configuration**
```env
PRIORITY_THRESHOLD=70                # Minimum score for high priority classification
MAX_EMAILS_TO_PROCESS=100           # Maximum emails per batch
```

**Domain Management**
```env
VIP_DOMAINS=company.com,partner.com              # Comma-separated VIP domains
ALLOWED_DOMAINS=company.com,trusted.com          # Approved external domains
BLOCKED_DOMAINS=spam.com,suspicious.com          # Blocked domains
```
Performance Metrics

The system tracks and reports the following key performance indicators:

**Processing Efficiency**
- Time saved per processing batch (estimated minutes)
- Average processing time per email
- Throughput (emails processed per minute)

**Accuracy Metrics**
- Priority classification accuracy rate
- Intent detection confidence scores
- False positive rate for spam detection

**Safety Metrics**
- Approval rejection rate (quality indicator)
- PII detection true positive rate
- Missed VIP communications (target: <1%)

**Operational Metrics**
- Draft generation success rate
- API call efficiency and caching utilization
- System uptime and error rates

## Safety and Compliance

### Operational Guidelines

**Required Practices**
- All decisions must include evidence (message IDs, thread links)
- External communications default to draft-only mode
- Clarification requests for ambiguous scenarios
- Batch processing to minimize API overhead
- Comprehensive audit logging for all actions

**Prohibited Actions**
- Automatic sending to external recipients without explicit approval
- Response generation without sufficient context
- Recipient inference when sender intent is ambiguous
- Processing of emails flagged with critical security violations

### Security Posture

**Data Handling**
- NTesting

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/

# Run specific test module
python -m pytest tests/test_classifier.py
```

### Demo Mode

The included demo script provides interactive testing:

```bash
python demo.py
```

Available demo options:
1. Basic Run - Complete pipeline demonstration
2. VIP Only - VIP filtering demonstration
3. DND Mode - Do Not Disturb mode demonstration
4. Custom Filters - Gmail query syntax demonstration
5. Check Permissions - API access verification

## Troubleshooting

### Common Issues

**Authentication Errors**
- Verify `credentials.json` is in project root
- Delete `tokens/token.json` and re-authenticate
- Confirm Gmail API is enabled in Google Cloud Console

**Missing Dependencies**
- Run `pip install -r requirements.txt`
- Verify Python version is 3.8 or higher

**API Rate Limits**
- Implement exponential backoff (built-in)
- Reduce `MAX_EMAILS_TO_PROCESS` value
- Increase time between batch runs

**Permission Issues**
- Run `python demo.py` and select option 5
- Re-authorize with all required scopes
- Check operating mode (should be "full")

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes with descriptive messages
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request with detailed description

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For bug reports and feature requests, please open an issue on the GitHub repository.

For security vulnerabilities, please contact the maintainers directly
- Legal and financial content escalation
- Domain-based access controls
- Approval workflow enforcementximum external recipients without approval
```

### Integration Configuration

**Slack Integration**
```env
SLACK_ENABLED=false
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#email-agent
```

**Notion Integration**
```env
NOTION_ENABLED=false
NOTION_TOKEN=secret_token
NOTION_DATABASE_ID=database_id
```
      }
    ],
    "blocked_items": [
      {
        "message_id": "msg_id",
        "reason": "PII detected - requires manual review",
        "security_flags": [...]
      }
    ],
    "warnings": [
      "High-risk content detected in 1 email"
    ]
  },
  "metrics": {
    "total_emails": 42,
    "high_priority": 5,
    "drafts_created": 3,
    "time_saved_minutes": 210,
    "vip_emails": 3,
    "approval_required_count": 2,
    "categories": {
      "action": 8,
      "fyi": 25,
      "waiting": 5,
      "spam": 2,
      "legal": 1,
      "finance": 1
    }
  },
  "batch_info": {
    "batch_id": "unique-batch-identifier",
    "started_at": "2026-01-10T09:00:00Z",
    "completed_at": "2026-01-10T09:02:15Z",
    "command": "Process inbox and prioritize urgent items"
The agent returns a structured response with:

```json
{
  "queue": {
    "batch_id": "abc123",
    "summary": {
      "total_processed": 42,
      "high_priority": 5,
      "drafts_created": 3,
      "needs_approval": 2,
      "blocked": 1
    },
    "high_priority_emails": [...],
    "draft_replies": [...],
    "follow_ups": [...],
    "blocked_items": [...]
  },
  "metrics": {
    "total_emails": 42,
    "time_saved_minutes": 210,
    "vip_emails": 3,
    "categories": {...}
  }
}
```

## Configuration Options

### Priority Scoring
- `PRIORITY_THRESHOLD`: Score threshold for high priority (default: 70)

### Domains
- `VIP_DOMAINS`: Comma-separated list of VIP domains
- `ALLOWED_DOMAINS`: Domains allowed for external communication
- `BLOCKED_DOMAINS`: Domains to block

### Security
- `REQUIRE_APPROVAL_FOR_EXTERNAL`: Require approval for external emails (default: true)
- `ENABLE_PII_DETECTION`: Enable PII scanning (default: true)
- `ENABLE_DOMAIN_RESTRICTIONS`: Enable domain checking (default: true)
- `ENABLE_TONE_ENFORCEMENT`: Enable tone checking (default: true)

## Success Metrics

The agent tracks:
- ⏱️ Time saved per day
- ✅ % of important emails correctly surfaced
- 📊 Approval rejection rate
- ⭐ Missed VIP items (target: near zero)

## Safety & Compliance

### DO
- ✅ Always show evidence (thread links, message IDs)
- ✅ Default to draft-only for external sending
- ✅ Ask clarifying questions when unclear
- ✅ Batch actions to reduce noise

### DON'T
- ❌ Never send external emails without approval
- ❌ Never hallucinate facts not in context
- ❌ Never guess recipients when ambiguous

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.
