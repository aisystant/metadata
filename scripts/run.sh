# Get a list of cources from the api (run get_all_cources.sh, that return a list of cources)

# python scripts/import_docs/get_all_cources.py | while read -r course; do
python scripts/get_all_cources.py | grep ontologics-sobr | while read -r course; do
    # course=name:version:authors:changelog
    echo "Course: $course"
    name=$(echo $course | cut -d: -f1)
    version=$(echo $course | cut -d: -f2)
    versionId=$(echo $course | cut -d: -f3)
    authors=$(echo $course | cut -d: -f4)
    changelog=$(echo $course | cut -d: -f5-)
    python scripts/load_structure.py "$name" "$version" "$versionId"
    break
done
