from marisol import Area, Marisol
import argparse

parser = argparse.ArgumentParser(description='Bates number documents')
parser.add_argument("files", help="files to Bates number", nargs='*')
parser.add_argument("--prefix", help="prefix for Bates numbers")
parser.add_argument("--digits", help="number of digits in Bates numbers", type=int)
parser.add_argument("--start", help="starting number", type=int)
parser.add_argument("--area", help="area of page")

def bates_number(docs, prefix, digits, start_number, area):
    m = Marisol(prefix, digits, start_number, area=getattr(Area, area))
    for doc in docs:
        m.append(doc)
    m.save()

if __name__ == "__main__":
    args = parser.parse_args()
    bates_number(args.files, args.prefix, args.digits, args.start, args.area)
