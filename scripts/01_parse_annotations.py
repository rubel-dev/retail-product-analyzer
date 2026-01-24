from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter


DATA_DIR = Path("data/raw")
XML_PATH = DATA_DIR / "annotations.xml"


def parse_points(points_str: str):
    """
    points_str looks like:
    "8.24,430.94;212.74,429.60;228.40,637.40;21.50,645.90"

    We convert it to list of (x, y) floats.
    """
    pts = []
    pairs = points_str.split(";")
    for p in pairs:
        x_str, y_str = p.split(",")
        pts.append((float(x_str), float(y_str)))
    return pts


def points_to_bbox(points):
    """
    points = [(x1,y1), (x2,y2), ...]
    returns (xmin, ymin, xmax, ymax)
    """
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    return min(xs), min(ys), max(xs), max(ys)


def main():
    # 1) Check XML exists
    if not XML_PATH.exists():
        raise FileNotFoundError(f"annotations.xml পাওয়া যায়নি: {XML_PATH}")

    # 2) Load XML
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    # 3) Find all image tags
    images = root.findall(".//image")
    print("✅ XML Loaded Successfully")
    print(f"🖼️ Total <image> entries in XML: {len(images)}")

    # 4) Count polylines (objects)
    label_counter = Counter()
    total_polylines = 0

    # store some examples
    examples = []

    for img_tag in images:
        img_name = img_tag.attrib.get("name", "NO_NAME")

        # IMPORTANT: we look for polyline, not box
        polys = img_tag.findall(".//polyline")
        total_polylines += len(polys)

        for poly in polys:
            label = poly.attrib.get("label", "UNKNOWN")
            points_str = poly.attrib.get("points", "")

            label_counter[label] += 1

            # save first few examples to show later
            if len(examples) < 5:
                pts = parse_points(points_str)
                bbox = points_to_bbox(pts)
                examples.append((img_name, label, bbox))

    print(f"📦 Total polylines (objects) in dataset: {total_polylines}")

    print("\n🏷️ Classes & counts:")
    for label, count in label_counter.most_common():
        print(f" - {label}: {count}")

    # 5) Print some bbox examples
    print("\n🔎 Sample objects (polyline -> bbox):")
    for img_name, label, (xmin, ymin, xmax, ymax) in examples:
        print(f"🖼️ {img_name} | {label} | bbox=({xmin:.1f},{ymin:.1f},{xmax:.1f},{ymax:.1f})")


if __name__ == "__main__":
    main()
