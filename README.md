# Course Metadata Extraction System

A comprehensive system for extracting and processing course metadata from the Aisystant API, generating bilingual (Russian/English) YAML files with complete course structures and metadata.

## Overview

This project fetches course information from the Aisystant platform, processes hierarchical course structures, translates Russian content to English using OpenAI GPT-4, and generates structured YAML output files containing course metadata with bilingual content.

## Features

- **Automated Course Discovery**: Fetches complete course catalog from Aisystant API
- **Hierarchical Structure Processing**: Handles complex course structures with headers, content sections, and tests
- **Bilingual Translation**: Automatic Russian-to-English translation using OpenAI GPT-4
- **Image Processing**: Extracts and processes course images with hash-based deduplication
- **YAML Output**: Generates clean, structured YAML files with complete course metadata
- **Translation Preservation**: Avoids re-processing existing translations for efficiency

## Prerequisites

- Python 3.7+
- Required API keys (see setup section below)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:aisystant/metadata.git
cd metadata
```

2. Install dependencies:
```bash
cd scripts
pip install -r requirements.txt
```

## Setup and Configuration

### Required API Keys

You need to set up the following environment variables:

#### 1. OpenAI API Key
Required for translating Russian course content to English.

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**How to get OpenAI API Key:**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save the key securely

#### 2. LangSmith API Key
Required for translation prompt management.

```bash
export LANGSMITH_API_KEY="your-langsmith-api-key-here"
```

**How to get LangSmith API Key:**
1. Go to [LangSmith](https://smith.langchain.com/)
2. Sign up or log in to your account
3. Navigate to Settings → API Keys
4. Create a new API key
5. Copy and save the key securely

#### 3. Aisystant Session Token
Required for accessing the Aisystant course API.

```bash
export AISYSTANT_SESSION_TOKEN="your-aisystant-session-token"
```

**How to get Aisystant Session Token:**
1. Log into your Aisystant account in a web browser
2. Open browser developer tools (F12)
3. Go to Network tab and find API requests
4. Look for the Session-Token in request headers
5. Copy the token value

#### 4. Optional Environment Variables

```bash
export BASE_URL="https://api.aisystant.com"  # API base URL (optional)
export IMAGES_URL="https://images.aisystant.com"  # Images base URL (optional)
```

### Environment Variables Setup

Create a `.env` file in the project root:

```bash
# .env file
OPENAI_API_KEY=your-openai-api-key-here
LANGSMITH_API_KEY=your-langsmith-api-key-here
AISYSTANT_SESSION_TOKEN=your-aisystant-session-token
BASE_URL=https://api.aisystant.com
IMAGES_URL=https://images.aisystant.com
```

Or set them in your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.bashrc
echo 'export LANGSMITH_API_KEY="your-langsmith-api-key-here"' >> ~/.bashrc
echo 'export AISYSTANT_SESSION_TOKEN="your-aisystant-session-token"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Quick Start

Run the complete extraction pipeline:

```bash
bash scripts/run.sh
```

This will:
1. Fetch all available courses from the Aisystant API
2. Process course structures and translate content
3. Generate YAML files in the `/yaml` directory

### Individual Scripts

#### 1. Get All Courses
Fetch the complete course catalog:

```bash
python scripts/get_all_cources.py
```

#### 2. Process Specific Course
Process a specific course structure:

```bash
python scripts/load_structure.py <course_id> <course_name> <version> <version_id>
```

Example:
```bash
python scripts/load_structure.py 123 "systems-thinking-introduction" "v1.0" 456
```

## Architecture

### Core Components

1. **Course Data Fetching** (`get_all_cources.py`)
   - Connects to Aisystant API using session tokens
   - Retrieves base64-encoded course metadata
   - Outputs structured course data for pipeline processing

2. **Structure Processing** (`load_structure.py`)
   - Processes hierarchical course structures from API
   - Handles different section types (HEADER, TEXT, TEST)
   - Translates Russian titles to English using OpenAI GPT-4
   - Extracts and processes images with metadata
   - Preserves existing translations to avoid redundant processing

3. **Pipeline Orchestration** (`run.sh`)
   - Orchestrates the complete extraction workflow
   - Parses course data and processes each course individually
   - Currently filtered for specific courses (configurable)

### Data Flow

```
get_all_cources.py → Course List with Metadata
         ↓
run.sh → Parse and Iterate Courses
         ↓
load_structure.py → Process Structure + Translate + Extract Images
         ↓
YAML Output → /yaml directory
```

### Output Structure

The system generates YAML files in the `/yaml` directory with the following structure:

```yaml
name: "Course Name"
authors: ["Author 1", "Author 2"]
changelog: "Version information"
structure:
  - type: "HEADER"
    title:
      ru: "Русский заголовок"
      en: "English Translation"
    children:
      - type: "TEXT"
        title:
          ru: "Русский текст"
          en: "English Translation"
        images:
          - path: "image-path.jpg"
            hash: "sha256-hash"
            title:
              ru: "Описание изображения"
              en: "Image Description"
```

## Data Types

- **HEADER**: Container sections with child elements
- **TEXT**: Content sections with text and images
- **TEST**: Assessment sections with questions

## Configuration

### Translation Settings
- **Model**: GPT-4o for high-quality translations
- **Prompt**: Uses LangSmith prompt "translatetitlesv2"
- **Temperature**: 0 for consistent translations

### Image Processing
- Hash-based deduplication prevents redundant downloads
- Preserves original paths and metadata
- Generates bilingual image descriptions

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify all API keys are correctly set
   - Check if Aisystant session token is still valid
   - Ensure environment variables are properly loaded

2. **Translation Failures**
   - Verify OpenAI API key has sufficient credits
   - Check LangSmith prompt "translatetitlesv2" exists
   - Review network connectivity

3. **Missing Dependencies**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

### Debug Mode

Enable detailed logging by modifying the scripts to include debug information or run with verbose output.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions, please refer to the project documentation or contact the development team.