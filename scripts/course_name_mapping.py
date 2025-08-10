# Course name mapping from old API names to new site names
# Add mappings here as: "old_api_name": "new_site_name"
# Only courses listed here will be processed (serves as both mapping and whitelist)

COURSE_NAME_MAPPING = {
    "ontologics-sobr": "rational-work",
    "systems-thinking-introduction": "systems-thinking-introduction",
    # Add more mappings here as needed
    # "old-course-name": "new-course-name",
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