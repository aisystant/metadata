import requests
import logging
import os
import re
import sys
import json
import dotenv
import yaml
from langsmith import Client
from openai import OpenAI
from langchain_core.messages import convert_to_openai_messages
from slugify import slugify


# Load environment variables from .env file
dotenv.load_dotenv()


# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_URL = os.getenv('BASE_URL')
AISYSTANT_SESSION_TOKEN = os.getenv('AISYSTANT_SESSION_TOKEN')
HEADERS = {'Session-Token': AISYSTANT_SESSION_TOKEN}

def send_get_request(path):
    url = f'{BASE_URL}/{path}'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error while sending GET request to {url}: {e}")
        return None

def get_course_structure(version_id):
    try:
        return send_get_request(f'courses/course-versions/{version_id}')
    except Exception as e:
        logger.error(f"Failed to fetch course structure for version ID {version_id}: {e}")
        return None


def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)


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
        logger.error(f"Error writing to file {file_path}: {e}")
        return None
    

def find_section_by_title(title, sections):
    for section in sections:
        if section["title_ru"] == title:
            return section
        if "children" in section:
            found = find_section_by_title(title, section["children"])
            if found:
                return found
    return None


client = Client()           # LangSmith client
oai_client = OpenAI()       # OpenAI client
prompt = client.pull_prompt("translatetitlesv2")


def translate_title(title, context=""):
    """
    Translate the title to English using LangSmith for prompt retrieval and OpenAI for generation.
    The result is cached and saved immediately after each new translation.
    """
    try:
        # Prepare the data for the prompt
        doc = {
            "title": title,
            "context": context,
        }
        # Invoke the prompt to format the request
        formatted_prompt = prompt.invoke(doc)
        # Send the request to OpenAI by converting messages to the required format
        response = oai_client.chat.completions.create(
            model="gpt-4o",  # Change to "gpt-4" if needed
            messages=convert_to_openai_messages(formatted_prompt.messages)
        )
        translated_title = response.choices[0].message.content.strip()
        if not translated_title:
            logger.error("Translation returned an empty result.")
            sys.exit(1)

        return translated_title
    except Exception as e:
        logger.error(f"Error translating title '{title}': {e}")
        sys.exit(1)


def build_section_info(section):
    section_type = section["type"]
    section_title = remove_number_prefix(section["title"])
    section_id = section["id"]
    section_old_id = section["prevVersionSectionId"]
    old_section = find_section_by_title(section_title, old_sections)
    logger.info(f"Old section: {old_section}")
    if old_section:
        section_title = old_section["title_ru"]
        section_type = old_section["type"]
        section_title_en = old_section["title_en"]
        section_slug = old_section["slug"]
    else:
        section_title_en = translate_title(section_title)
        section_slug = slugify(section_title_en, separator="-", lowercase=True)
    logger.info(f"Section ID: {section_id}, Title: {section_title}, Type: {section_type}, Slug: {section_slug}")
    return {
        "type": section_type,
        "title_ru": section_title,
        "title_en": section_title_en,
        "slug": section_slug,
        "section_id": section_id,
    }


def build_hierarchical_structure(sections):
    result = []
    current_header = None

    for section in sections:
        print(section)
        section_data = build_section_info(section)

        if section["type"] == "HEADER":
            current_header = section_data
            current_header["children"] = []
            result.append(current_header)
        else:
            if current_header:
                current_header["children"].append(section_data)
            else:
                result.append(section_data)

    return result


if __name__ == "__main__":
    course_id = sys.argv[1]
    version = sys.argv[2]
    version_id = sys.argv[3]
    course_data = get_course_structure(version_id)

    old_course_data = read_yaml_file(f"{course_id}.yaml")
    if old_course_data is None:
        old_course_data = dict()
    
    old_sections = old_course_data.get("sections", [])

    if course_data and "sections" in course_data:
        hierarchical_structure = build_hierarchical_structure(course_data["sections"])
        doc = {
            "course_id": course_id,
            "version": version,
            "version_id": version_id,
            "sections": hierarchical_structure
        }
        print(yaml.dump(doc, allow_unicode=True, default_flow_style=False, sort_keys=False))
        write_yaml_file(f"{course_id}.yaml", doc)
        #print(json.dumps(hierarchical_structure, indent=4, ensure_ascii=False))
    else:
        logger.error(f"Failed to fetch or process sections for version ID {version_id}")
        sys.exit(1)