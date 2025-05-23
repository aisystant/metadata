import os
import re
import sys
import json
import yaml
import dotenv
import logging
import requests

from slugify import slugify
from openai import OpenAI
from langsmith import Client
from langchain_core.messages import convert_to_openai_messages


# ------------------------- Configuration & Setup -------------------------

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)


def load_env():
    dotenv.load_dotenv()
    return {
        "BASE_URL": os.getenv('BASE_URL'),
        "SESSION_TOKEN": os.getenv('AISYSTANT_SESSION_TOKEN')
    }


logger = setup_logging()
config = load_env()
HEADERS = {'Session-Token': config["SESSION_TOKEN"]}

# ------------------------- HTTP & File IO -------------------------

def send_get_request(path):
    url = f'{config["BASE_URL"]}/{path}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"GET request failed: {e}")
        return None


def read_yaml_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None


def write_yaml_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")

# ------------------------- Section Utilities -------------------------

def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)


def find_section_by_title(title, sections):
    for section in sections:
        if section.get("title_ru") == title:
            return section
        if "children" in section:
            found = find_section_by_title(title, section["children"])
            if found:
                return found
    return None

# ------------------------- Translation -------------------------

def init_clients():
    return Client(), OpenAI()


client, oai_client = init_clients()
prompt = client.pull_prompt("translatetitlesv2")


def translate_title(title, context=""):
    try:
        doc = {"title": title, "context": context}
        formatted = prompt.invoke(doc)
        response = oai_client.chat.completions.create(
            model="gpt-4o",
            messages=convert_to_openai_messages(formatted.messages)
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Translation failed for '{title}': {e}")
        return None

# ------------------------- Section Building -------------------------

def build_section_info(section, old_sections):
    title = remove_number_prefix(section["title"])
    section_id = section["id"]
    old_section = find_section_by_title(title, old_sections)

    if old_section:
        return {
            "type": old_section["type"],
            "title_ru": old_section["title_ru"],
            "title_en": old_section["title_en"],
            "slug": old_section["slug"],
            "section_id": section_id,
        }

    translated_title = translate_title(title)
    if not translated_title:
        logger.error(f"Could not translate title: {title}")
        return None

    slug = slugify(translated_title, separator="-", lowercase=True)
    return {
        "type": section["type"],
        "title_ru": title,
        "title_en": translated_title,
        "slug": slug,
        "section_id": section_id,
    }


def build_hierarchical_structure(sections, old_sections):
    result = []
    current_header = None

    for section in sections:
        data = build_section_info(section, old_sections)
        if data is None:
            continue

        if section["type"] == "HEADER":
            current_header = data
            current_header["children"] = []
            result.append(current_header)
        elif current_header:
            current_header["children"].append(data)
        else:
            result.append(data)

    return result

# ------------------------- Main -------------------------

def main():
    if len(sys.argv) != 4:
        logger.error("Usage: script.py <course_id> <version> <version_id>")
        sys.exit(1)

    course_id, version, version_id = sys.argv[1:4]
    course_data = send_get_request(f'courses/course-versions/{version_id}')
    if not course_data or "sections" not in course_data:
        logger.error("Invalid course data")
        sys.exit(1)

    old_data = read_yaml_file(f"{course_id}.yaml") or {}
    old_sections = old_data.get("sections", [])

    new_structure = build_hierarchical_structure(course_data["sections"], old_sections)
    doc = {
        "course_id": course_id,
        "version": version,
        "version_id": version_id,
        "sections": new_structure
    }

    print(yaml.dump(doc, allow_unicode=True, default_flow_style=False, sort_keys=False))
    write_yaml_file(f"{course_id}.yaml", doc)


if __name__ == "__main__":
    main()