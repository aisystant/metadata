# Course name mapping from old API names to new site names
# Add mappings here as: "old_api_name": "new_site_name"

COURSE_NAME_MAPPING = {
    "ontologics-sobr": "rational-work",
    # Add more mappings here as needed
    # "old-course-name": "new-course-name",
}

def get_mapped_name(original_name):
    """
    Return the mapped course name if it exists in the mapping,
    otherwise return the original name.
    """
    return COURSE_NAME_MAPPING.get(original_name, original_name)