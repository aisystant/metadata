# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a course metadata extraction and processing system that fetches course information from the Aisystant API, processes course structures, and generates YAML files containing course metadata with bilingual (Russian/English) content.

## Key Commands

### Setup and Dependencies
```bash
cd scripts
pip install -r requirements.txt
```

### Main Workflow
```bash
# Extract and process all courses (or filter specific ones)
bash scripts/run.sh
```

### Individual Scripts
```bash
# Get list of all courses from API
python scripts/get_all_cources.py

# Process specific course structure
python scripts/load_structure.py <course_id> <course_name> <version> <version_id>
```

## Architecture

### Core Components

1. **Course Data Fetching** (`get_all_cources.py`)
   - Fetches course list from Aisystant API using session tokens
   - Returns base64-encoded course metadata (name, authors, changelog)
   - Outputs course data in structured format for pipeline processing

2. **Structure Processing** (`load_structure.py`)
   - Processes individual course structures from API
   - Handles hierarchical course sections (HEADER, TEXT, TEST types)
   - Translates Russian titles to English using OpenAI GPT-4o
   - Manages image extraction and metadata from course content
   - Preserves existing translations to avoid re-processing

3. **Pipeline Orchestration** (`run.sh`)
   - Orchestrates the complete extraction workflow
   - Currently filtered to process only 'systems-thinking-introduction' course
   - Parses course data and calls structure processing for each course

### Data Flow

1. `get_all_cources.py` → API course list with encoded metadata
2. `run.sh` → Parse course data and iterate through courses  
3. `load_structure.py` → Process each course structure, translate content, extract images
4. Output → YAML files in `/yaml` directory with complete course metadata

### Key Configuration

- **Environment Variables**: `AISYSTANT_SESSION_TOKEN`, `BASE_URL`, `IMAGES_URL`
- **Translation**: Uses LangSmith prompt "translatetitlesv2" with OpenAI GPT-4o
- **Output Format**: YAML files with hierarchical course structure, bilingual titles, and image metadata

### Data Structures

- Course sections maintain hierarchy (headers with children)
- Image metadata includes original path, hash for deduplication, and bilingual titles
- Section types: HEADER (containers), TEXT (content), TEST (assignments)

## Working with the Codebase

- YAML files in `/yaml/` contain processed course metadata - these are the main output artifacts
- The system is designed to preserve existing translations and avoid re-processing unchanged content
- Image processing includes hash-based deduplication to avoid redundant downloads
- Translation context is preserved to maintain consistency across course updates