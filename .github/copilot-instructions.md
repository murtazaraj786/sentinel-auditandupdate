<!-- Workspace-specific custom instructions for Microsoft Sentinel Audit and Update Tool -->

## Project Overview
This project audits Microsoft Sentinel data connectors and analytic rules for available updates, and provides deployment capabilities.

## Key Technologies
- Python 3.8+
- Azure SDK for Python
- Microsoft Sentinel API
- Azure Authentication (DefaultAzureCredential)

## Development Guidelines
- Follow Python PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Handle Azure exceptions gracefully with proper error messages
- Use logging for debugging and operational insights
- Store configuration in environment variables or config files

## Code Organization
- Keep authentication logic separate from API calls
- Modularize functionality (data connectors, analytic rules, deployment)
- Use dataclasses or Pydantic models for structured data
- Implement proper retry logic for API calls

## Security Best Practices
- Never hardcode credentials
- Use Azure Managed Identity when possible
- Follow least privilege principle for Azure permissions
- Validate user inputs to prevent injection attacks
