#!/usr/bin/env bash

# This script converts the shared FATE documentation into the Markdown format
# needed by Jekyll to render the page correctly. The script doc_to_page.py
# contains most of the processing, which focuses on formatting the table of
# contents, headers, and equations correctly.
#
# Requirements:
#   - pandoc
#   - gh-md-toc (https://github.com/ekalinin/github-markdown-toc)
#
# Caleb Braun <c.braun@theicct.org>
# 5/19/21
echo "========================="
echo "* Documentation Updater *"
echo "========================="
echo "Running this script will update FATE's documentation. Before running, confirm that "
echo "you have done all the manual steps required: "
echo "  1. Saved the documentation as a .pdf file to the versions directory"
echo "  2. Updated the image mapping in doc_to_page.py, if any new images were added"
read -rsp $'\nPress any key to continue (or ctrl-C to exit)...\n' -n1 key

DOC_RAW="documentation_raw.md"
DOC_INT="documentation"  # intermediate file name (no extension!)
DOC_SHARED="FATE Documentation.docx"  # the file name of the shared version

# Load reference to the authoritative version on Teams and make a copy
source shared_version.sh
echo "Copying documentation from $shared_version"
cp "$shared_version" .

# Convert to Markdown
pandoc -f docx -t gfm --wrap=preserve "$DOC_SHARED" -o $DOC_RAW

# Run the Markdown processing script (model version is last thing printed)
version=$(python doc_to_page.py $DOC_RAW "$DOC_INT.md" | tail -1)

# Move to versions directory
mv "${DOC_INT}_${version}.md" "versions/${version}.md"

echo "Documentation successfully written to versions/${version}.md"

# Remove all intermediate files
rm $DOC_RAW "$DOC_SHARED"
