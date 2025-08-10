# Course name mapping from old API names to new site names
# Add mappings here as: "old_api_name": "new_site_name"
# Only courses listed here will be processed (serves as both mapping and whitelist)

COURSE_NAME_MAPPING = {
    # Personal Development (Личное развитие)
    "intro-online-2021": "systems-self-development",
    "selfdev": "self-development-methods",
    "systems-thinking-intro-2022": "systems-thinking-introduction",
    "sf": "systems-based-fitness",
    
    # Rational Work Program (Программа Рабочего развития)
    "ontologics-sobr": "rational-work",
    "practical-systems-thinking": "systems-thinking",
    "methodology": "methodology",
    "systems-engineering": "systems-engineering",
    "systems-teaching": "personality-engineering",
    "systems-management": "systems-management",
    
    # Research Development (Исследовательское развитие)
    "intelligence-stack": "intellect-stack",
}

def get_mapped_name(original_name):
    """
    Return the mapped course name if it exists in the mapping,
    otherwise return the original name.
    """
    return COURSE_NAME_MAPPING.get(original_name, original_name)

def is_course_allowed(original_name):
    """
    Check if a course is in the whitelist (mapping dictionary).
    Only courses in COURSE_NAME_MAPPING will be processed.
    """
    return original_name in COURSE_NAME_MAPPING