import os
import re
import sys
import yaml
import dotenv
import logging
import requests
import hashlib

from slugify import slugify
from openai import OpenAI
from langsmith import Client
from langchain_core.messages import convert_to_openai_messages

# ------------------------- Configuration & Setup -------------------------

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

def load_env():
    dotenv.load_dotenv()
    return {
        "BASE_URL": os.getenv("BASE_URL"),
        "SESSION_TOKEN": os.getenv("AISYSTANT_SESSION_TOKEN"),
        "IMAGES_URL": os.getenv("IMAGES_URL")
    }

logger = setup_logging()
config = load_env()
HEADERS = {'Session-Token': config["SESSION_TOKEN"]}

# ------------------------- HTTP & File IO -------------------------

def send_get_request(url):
    logger.info(f"GET {url}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response

def read_yaml_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"YAML file not found: {file_path}")
        return None

def write_yaml_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

# ------------------------- Utilities -------------------------

def remove_number_prefix(text):
    return re.sub(r'^\d+\.\s*', '', text)

def find_section_by_title(title, sections, section_type=None):
    for section in sections:
        if section.get("title_ru") == title:
            if section_type is None or section.get("type") == section_type:
                return section
        if "children" in section:
            result = find_section_by_title(title, section["children"], section_type)
            if result:
                return result
    return None

# ------------------------- Translation -------------------------

client, oai_client = Client(), OpenAI()
prompt = client.pull_prompt("translatetitlesv2")

def translate_title(title, context=""):
    try:
        doc = {"title": title, "context": context}
        formatted = prompt.invoke(doc)
        response = oai_client.chat.completions.create(
            model="gpt-4o",
            messages=convert_to_openai_messages(formatted.messages),
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Failed to translate '{title}': {e}")
        return None

# ------------------------- Image Processing -------------------------

IMAGE_PATTERN = re.compile(r'<img\s+src="(.*?)"\s+alt=".*?">', re.DOTALL)

def extract_attachments(html):
    return IMAGE_PATTERN.findall(html)

def get_images_from_section(section_id):
    html = send_get_request(f"{config['BASE_URL']}/courses/text/{section_id}").text
    return extract_attachments(html)

def get_image_hash(image_url):
    content = send_get_request(image_url).content
    return hashlib.sha256(content).hexdigest()

def find_image_by_hash(image_hash, images):
    return next((img for img in images if img.get("orig_hash") == image_hash), None)

def build_image_structure(image_path, images):
    image_url = f"{config['IMAGES_URL']}{image_path}"
    filename = os.path.basename(image_path)
    image_hash = get_image_hash(image_url)
    existing = find_image_by_hash(image_hash, images)
    if existing:
        existing["orig_path"] = image_path
        return existing
    return {
        "filename": filename,
        "title_ru": "",
        "title_en": "",
        "orig_path": image_path,
        "orig_hash": image_hash
    }

# ------------------------- Section Processing -------------------------

def build_section_info(section, old_sections):
    title = remove_number_prefix(section["title"])
    section_id = section["id"]
    old = find_section_by_title(title, old_sections)

    if old:
        doc = {
            "type": old["type"],
            "title_ru": old["title_ru"],
            "title_en": old["title_en"],
            "slug": old["slug"],
            "section_id": section_id
        }
    else:
        translated = translate_title(title)
        if not translated:
            return None
        doc = {
            "type": section["type"],
            "title_ru": title,
            "title_en": translated,
            "slug": slugify(translated, separator="-", lowercase=True),
            "section_id": section_id
        }

    if section["type"] == "TEXT":
        images = get_images_from_section(section_id)
        if images:
            if old and "images" in old:
                old_images = old["images"]
            else:
                old_images = []
            doc["images"] = [build_image_structure(img, old_images) for img in images]

    return doc

def build_hierarchy(sections, old_sections):
    result = []
    current_header = None

    for sec in sections:
        data = build_section_info(sec, old_sections)
        if not data:
            continue
        if sec["type"] == "HEADER":
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
    if len(sys.argv) != 6:
        logger.error("Usage: script.py <course_id> <original_course_id> <course_name> <version> <version_id>")
        sys.exit(1)

    course_id, original_course_id, course_name, version, version_id = sys.argv[1:6]
    course_data = send_get_request(f"{config['BASE_URL']}/courses/course-versions/{version_id}").json()
    if not course_data or "sections" not in course_data:
        logger.error("Invalid course data")
        sys.exit(1)

    old_data = read_yaml_file(f"yaml/{course_id}.yaml") or {}
    old_sections = old_data.get("sections", [])

    # Check if version has changed
    if old_data.get("version") == version:
        logger.info(f"Version {version} unchanged for course {course_id}, skipping update")
        return

    structure = build_hierarchy(course_data["sections"], old_sections)
    doc = {
        "course_id": course_id,
        "original_course_id": original_course_id,
        "course_name": course_name,
        "version": version,
        "version_id": version_id,
        "sections": structure
    }

    #print(yaml.dump(doc, allow_unicode=True, default_flow_style=False, sort_keys=False))
    write_yaml_file(f"yaml/{course_id}.yaml", doc)

if __name__ == "__main__":
    main()
