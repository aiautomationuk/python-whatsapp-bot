# Multi-Company WhatsApp Bot Setup

This guide explains how to set up and manage multiple company instances of the WhatsApp bot.

## Overview

The system is designed to support multiple companies, each with their own:
- WhatsApp Business API integration
- OpenAI Assistant
- Knowledge base
- Configuration

## Setup Process

1. **Prepare Company Information**
   - Create a text file with the company's information
   - Include details like:
     - Company name
     - Contact information
     - Services/products
     - Business hours
     - FAQ

2. **Run Setup Script**
   ```bash
   python setup_new_company.py
   ```
   - Enter company name
   - Provide path to company info file
   - Enter Meta Business API token (if available)
   - Enter Meta Phone Number ID (if available)

3. **Meta Business Setup**
   - Create a Meta Business account for each company
   - Set up WhatsApp Business API
   - Get API token and Phone Number ID
   - Update company's .env file with these values

4. **Deployment**
   - Each company gets its own directory under `companies/`
   - Deploy each instance separately to Render.com
   - Update render.yaml with company-specific settings

## Directory Structure

```
companies/
├── company1/
│   ├── app/
│   ├── start/
│   ├── .env
│   ├── requirements.txt
│   └── SETUP.md
├── company2/
│   ├── app/
│   ├── start/
│   ├── .env
│   ├── requirements.txt
│   └── SETUP.md
└── ...
```

## Pricing and Billing

1. **Setup Fee**
   - Initial setup and configuration
   - Knowledge base creation
   - Meta Business integration

2. **Monthly Fee**
   - OpenAI API usage
   - Hosting costs
   - Maintenance and updates

3. **Additional Services**
   - Knowledge base updates
   - Custom feature development
   - Training and support

## Support and Maintenance

- Each company instance is managed independently
- Updates can be applied to all instances or individually
- Support is provided through a central system
- Regular backups of all instances

## Security

- Each company has its own:
  - API keys
  - WhatsApp Business account
  - OpenAI Assistant
  - Vector store
  - Environment variables

## Best Practices

1. **Company Information**
   - Keep information up to date
   - Regular reviews of responses
   - Update knowledge base as needed

2. **Monitoring**
   - Track usage and costs
   - Monitor response quality
   - Check system health

3. **Backup**
   - Regular backups of all instances
   - Version control of knowledge bases
   - Configuration backups

## Contact

For support or to set up a new company instance:
- Email: support@infobot.tech
- Website: https://infobot.tech 