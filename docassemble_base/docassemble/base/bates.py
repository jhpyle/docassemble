import argparse
from docassemble.base.marisol import Area, Marisol

parser = argparse.ArgumentParser(description='Bates number documents')
parser.add_argument("files", help="files to Bates number", nargs='*')
parser.add_argument("--prefix", help="prefix for Bates numbers")
parser.add_argument("--digits", help="number of digits in Bates numbers", type=int)
parser.add_argument("--start", help="starting number", type=int)
parser.add_argument("--area", help="area of page")
parser.add_argument("--offset-horizontal", help="how far to offset the number from the side of the page", type=float)
parser.add_argument("--offset-vertical", help="how far to offset the number from the side of the page", type=float)
parser.add_argument("--font-size", help="How big the numbers are", type=float)


def bates_number(docs, prefix, digits, start_number, area, offset_horizontal, offset_vertical, font_size):
    m = Marisol(prefix, digits, start_number, area=getattr(Area, area), offset_horizontal=offset_horizontal, offset_vertical=offset_vertical, font_size=font_size)
    for doc in docs:
        m.append(doc)
    m.save()

if __name__ == "__main__":
    args = parser.parse_args()
    bates_number(args.files, args.prefix, args.digits, args.start, args.area, args.offset_horizontal, args.offset_vertical, args.font_size)
