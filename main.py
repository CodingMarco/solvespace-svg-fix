import argparse
import subprocess
import shutil
from lxml import etree

# Convert svgs exported from solvespace to svgs that can be used with a laser cutter

parser = argparse.ArgumentParser()
parser.add_argument(
    "input", help="Input file (will be overwritten)", nargs="+")
parser.add_argument("-m", "--margin", help="Margin in mm",
                    type=float, default=0.3)
args = parser.parse_args()

for file in args.input:
    subprocess.run(["inkscape", "--export-type=svg", "--export-overwrite",
                    "--export-margin=0", "--export-area-drawing", file],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Parse XML file
    tree = etree.parse(file)
    root = tree.getroot()

    # Remove style tag from root
    for style in root.xpath("//*[local-name()='style']"):
        style.getparent().remove(style)

    # Remove class attribute from all elements
    for element in root.xpath("//*"):
        if "class" in element.attrib:
            del element.attrib["class"]

    # Add above specified inline style to all path elements
    for path in root.xpath("//*[local-name()='path']"):
        path.attrib["style"] = "fill:none;stroke:#FF0000;stroke-width:0.3"

    # Increase the margin by 0.3mm by parsing and editing the viewbox as well as the width and height
    viewbox = root.attrib["viewBox"].split(" ")
    viewbox[0] = str(float(viewbox[0].replace("mm", "")) - args.margin)
    viewbox[1] = str(float(viewbox[1].replace("mm", "")) - args.margin)
    viewbox[2] = str(float(viewbox[2].replace("mm", "")) + 2 * args.margin)
    viewbox[3] = str(float(viewbox[3].replace("mm", "")) + 2 * args.margin)
    root.attrib["viewBox"] = " ".join(viewbox)
    root.attrib["width"] = str(
        float(root.attrib["width"].replace("mm", "")) + 2 * args.margin)
    root.attrib["height"] = str(
        float(root.attrib["height"].replace("mm", "")) + 2 * args.margin)

    # Write output
    tree.write(file, pretty_print=True)
