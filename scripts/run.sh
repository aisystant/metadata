# Get a list of cources from the api (run get_all_cources.sh, that return a list of cources)

# python scripts/import_docs/get_all_cources.py | while read -r course; do
python scripts/get_all_cources.py | grep selfdev | while read -r course; do
    # course=name:version:authors:changelog
    echo "Course: $course"
    name=$(echo $course | cut -d: -f1)
    course_name=$(echo $course | cut -d: -f2 | base64 --decode)
    version=$(echo $course | cut -d: -f3)
    versionId=$(echo $course | cut -d: -f4)
    authors=$(echo $course | cut -d: -f5)
    changelog=$(echo $course | cut -d: -f6-)
    echo "ID: $name"
    echo "Course Name: $course_name"
    echo "Version: $version"
    echo "Version ID: $versionId"
    echo "Authors: $authors"
    echo "Changelog: $changelog"
    echo "Loading structure for $name"
    # Load the structure of the course
    python scripts/load_structure.py "$name" "$course_name" "$version" "$versionId"
    # break
done
