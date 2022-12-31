import argparse
import subprocess
import shutil
from lxml import etree

# Convert svg exported from solvespace to an svg that can be used with a laser cutter
# Usage: python main.py input.svg [output.svg]

# Conversions steps:
# 1. Fill should be no fill everywhere
# 2. All lines should be black
# 3. All lines should be 0.3mm wide


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input", help="input file")
parser.add_argument("output", nargs='?', help="output file")
parser.add_argument("-m", "--margin", help="margin in mm",
                    type=float, default=0.3)
args = parser.parse_args()

input_file = args.input
output_file = args.output if args.output else input_file.replace(
    ".svg", "_out.svg")

shutil.copyfile(input_file, output_file)

subprocess.run(["inkscape", "--export-type=svg", "--export-overwrite", f"--export-margin=0",
                "--export-area-drawing", output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Parse XML file
tree = etree.parse(output_file)
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
tree.write(output_file, pretty_print=True)
