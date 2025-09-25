# False Positives/Negatives Database

A collaborative Flask web application for reporting and validating false positives and false negatives from algorithmic predictions, with a focus on tools like NetMHCPan and other bioinformatics algorithms.

## Features

### Core Functionality
- **Homepage**: Displays count of approved public records
- **Two-step user registration**: Email signup → verification code → account activation
- **Record submission**: Authenticated users can submit false positive/negative reports
- **Browse & Search**: Filter and search through approved records
- **Individual record view**: Detailed view of each approved record

### Integrations
- **Sheety API**: Google Sheets integration for data storage
- **Mailjet API**: Email notifications for verification codes
- **Slack Webhooks**: Approval workflow notifications

## Screenshots

### Homepage
![Homepage](https://github.com/user-attachments/assets/7d949e4b-82b7-480c-b38e-f155ae3151cf)

### Browse Records
![Browse Records](https://github.com/user-attachments/assets/759dc05f-4990-47b6-8230-f80ce3d0a997)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/drchristhorpe/falsepositivesfalsenegatives_prototype.git
cd falsepositivesfalsenegatives_prototype
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy `.env.example` to `.env` and configure):
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Environment Configuration

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here

# Sheety API Configuration (for Google Sheets integration)
SHEETY_API_URL=https://api.sheety.co/your-api-endpoint
SHEETY_TOKEN=your-sheety-token

# Mailjet API Configuration (for email notifications)
MAILJET_API_KEY=your-mailjet-api-key
MAILJET_SECRET_KEY=your-mailjet-secret-key

# Slack Webhook Configuration (for approval notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

## Usage Workflow

1. **Sign Up**: Users register with email and institution
2. **Verify**: Users receive and enter verification code from email
3. **Submit**: Verified users can submit false positive/negative reports
4. **Review**: Submissions are reviewed (via Slack notifications)
5. **Approve**: Approved records become publicly searchable
6. **Browse**: Anyone can search and view approved records

## API Integrations

### Demo Mode
When API credentials are not configured, the application runs in demo mode:
- Verification codes are printed to console
- Sheet/email/Slack integrations are simulated with console output

### Production Setup
- **Sheety**: Configure Google Sheets API endpoint for data storage
- **Mailjet**: Set up email service for verification codes
- **Slack**: Configure webhook for approval notifications

## Data Structure

Each record contains:
- Algorithm name (NetMHCPan, NetMHC, etc.)
- Error type (false positive/negative)
- Peptide sequence
- HLA allele
- Expected vs actual results
- Description/evidence
- Submission and approval metadata

## Future Enhancements

- Bulk data download functionality
- More sophisticated search/filtering
- User management dashboard
- API endpoints for programmatic access
- Database persistence (currently uses in-memory storage)

## Contributing

This is a prototype application. For production use, consider:
- Implementing proper database storage
- Adding comprehensive testing
- Enhancing security measures
- Scaling considerations
