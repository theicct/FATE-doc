"""
Convert the FATE documentation from raw Word conversion to Jekyll page format.

Caleb Braun
5/19/2021
"""
import regex as re
import sys
import subprocess


# NOTE: If you have added images, you MUST fix this mapping! Images in the Word
# version are parsed by pandoc as "media/imageX.emf", where X matches the order
# the images appear in the document.
IMG_MAP = {
    "media/image1.png": "/fate-doc/assets/usa_nox_pm25_adjoint_sensitivities.png",
    "media/image2.png": "/fate-doc/assets/pm_map_cropped.svg",
    "media/image4.png": "/fate-doc/assets/o3_map.svg",
    "media/image6.png": "/fate-doc/assets/pm_relative_risks.png",
}

DOC_RAW = "documentation_raw.md"
DOC_OUT = "documentation.md"


def get_version(lines):
    """Find the version number."""
    l = lines[2]
    v = re.search(r"(v([\d]+[.]?)+)", l)
    if v:
        return v.group(1)
    else:
        raise ValueError("Version not found.")


def get_date(lines):
    """Find the date of the documentation."""
    l = lines[4]
    date_regex = r"^(0?[1-9]|1[012])/(0[1-9]|[12][0-9]|3[01])/20\d\d"
    d = re.search(date_regex, l)
    if d:
        return d.group(0)
    else:
        raise ValueError("Date not found.")


def fix_headers(lines):
    """Change case and heading level of all headers."""
    for i, l in enumerate(lines):
        if l.startswith("#"):
            if l.startswith("# "):
                words = l.lower().split()
                words[1] = words[1].capitalize()  # Capitalize first non "#" word
                l = " ".join(words)

            l = l.replace("#", "##", 1)  # Make headings one level lower
            lines[i] = l

    return lines


def fix_footnotes(lines):
    notes = {}
    for i, l in enumerate(lines):
        footnotes = re.findall(r"(\\\[(\d)\\\])", l)
        if footnotes:
            for footnote in footnotes:
                notes[footnote] = i

    refs = lines[-len(notes) * 2:]  # x2 because each note has a new line
    refs = [r.split()[-1] for r in refs if r != "\n"]
    refs = [r.replace("\\", "") for r in refs]  # don't escape anything in URL

    for note, line in notes.items():
        n = int(note[1])
        replace = f"<sup><a href='{refs[n - 1]}'>{n}</a></sup>"
        lines[line] = lines[line].replace(note[0], replace)

    lines = lines[:-len(notes) * 2]

    return lines


def remove_toc(lines):
    """Remove table of contents."""
    # We're going to build our own table of contents, so strip everything before the
    # introduction section.
    i = 0
    while "# INTRODUCTION" not in lines[i]:
        i += 1
    lines = lines[i:]

    # Insert tags so that gh-md-toc works
    toc_start = "<!--ts-->"
    toc_end = "<!--te-->"
    lines.insert(0, toc_start + "\n")
    lines.insert(1, toc_end + "\n")

    return lines


def add_date(lines, date):
    lines.insert(0, f"_{date}_\n")
    return lines


def add_front_matter(lines, version):
    lines.insert(0, "---\n")
    lines.insert(1, "layout: page\n")
    lines.insert(2, f"title: 'FATE {version} Documentation'\n")
    lines.insert(3, f"permalink: /versions/{version}/\n")
    lines.insert(4, "---\n")
    return lines


def get_file_names():
    try:
        in_fname = sys.argv[1]
    except IndexError:
        in_fname = DOC_RAW

    try:
        out_fname = sys.argv[2]
    except IndexError:
        out_fname = DOC_OUT

    return in_fname, out_fname


def add_toc(outdoc):
    """Add table of contents using gh-md-toc utility."""
    cmd = f"gh-md-toc --insert --no-backup {outdoc}"
    subprocess.run(cmd, shell=True, check=True)

    # When we added the TOC it inserted too much whitespace
    with open(outdoc) as f:
        toc = f.readlines()

        for i, l in enumerate(toc):
            if "<!--te-->" in l:
                break
            else:
                toc[i] = l.replace("    *", "*", 1)

        toc.insert(toc.index("<!--ts-->\n"), "## Table of contents\n")  # Add TOC header

    with open(outdoc, "w") as f:
        f.writelines(toc)


def _fix_inline(l):
    istart = 0
    iend = 0
    for i in range(len(l)):
        if l[i:i + 2] == "\(":
            istart = i
        if l[i:i + 2] == "\)":
            iend = i

    l = l[:istart] + l[istart:iend].replace("_", "\_") + l[iend:]
    l = l.replace(r"\(", r"\\(")
    l = l.replace(r"\)", r"\\)")

    return l


def fix_math(doc):
    """Fix how mathjax escapes work with markdown/jekyll."""
    for i, l in enumerate(doc):
        if r"\(" in l:
            l = _fix_inline(l)
        l = l.replace(r"\[", r"$$")
        l = l.replace(r"\]", r"$$")  # display math
        l = l.replace("{{", "{ {")  # double braces are liquid syntax
        doc[i] = l

    return doc


def rename_images(doc):
    """Point images to the correct file."""
    for i, l in enumerate(doc):
        if "media" in l:
            for orig, new in IMG_MAP.items():
                if orig in l:
                    doc[i] = l.replace(orig, new)

    return doc


def add_download_button(doc, version):
    """Add HTML download button to end of file."""
    btn = (
        f"<button name='download' onclick=\"location.href='../FATE {version} "
        "Documentation.pdf'\">Download as PDF</button>\n"
    )
    doc.append("\n")
    doc.append(btn)
    return doc


def main():
    indoc, outdoc = get_file_names()

    with open(indoc) as f:
        doc = f.readlines()

    # Get the model version
    version = get_version(doc)
    date = get_date(doc)

    # Remove Word verions's TOC (we'll add Markdown version in at end)
    doc = remove_toc(doc)

    # Make headings one level lower and fix capitalization
    doc = fix_headers(doc)

    # Convert footnotes into links
    doc = fix_footnotes(doc)

    # Add the date to the top
    doc = add_date(doc, date)

    # Front matter is the header text needed for Jekyll to recognize the page
    doc = add_front_matter(doc, version)

    # Fix how MathJax (the javascript library that formats equations) escaping
    # characters work with markdown/jekyll.
    doc = fix_math(doc)

    # The pandoc Word export gives the images automatic names which need fixing
    doc = rename_images(doc)

    # Add a download button at the bottom of the page
    doc = add_download_button(doc, version)

    # Add version number to the filename
    outdoc = outdoc.split(".")
    assert len(outdoc) == 2
    outdoc = f"{outdoc[0]}_{version}.{outdoc[1]}"

    # Write the new documentation Markdown file
    with open(outdoc, "w") as f:
        f.writelines(doc)

    # Call gh-md-toc utility to add final table of contents
    add_toc(outdoc)

    # The version number needs to be printed for copy_doc.sh
    print(version)


if __name__ == '__main__':
    main()
