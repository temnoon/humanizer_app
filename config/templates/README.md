# Configuration Templates

This directory contains template configuration files for the Humanizer project.

## Setup Instructions

1. **Copy templates to local directory:**
   ```bash
   cp config/templates/env_template config/local/.env
   ```

2. **Edit local configuration:**
   - Add your API keys
   - Adjust paths if needed
   - Customize settings for your environment

3. **Never commit local configs:**
   - The `config/local/` directory is excluded from git
   - This protects your API keys and personal settings

## File Locations

- **Templates** (public): `config/templates/`
- **Local configs** (private): `config/local/`
- **Environment-specific** (private): `config/environments/`

## Privacy Protection

All files in `config/local/` and `config/environments/` are automatically excluded from git commits to protect your private configuration and API keys.