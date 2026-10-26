"""Generate class references and category pages from the plugin XML snapshot."""
import argparse
from classref_generator import ROOT, VENDOR, MANIFEST, generate, check_inputs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path in generate(check=args.check):
        print(path.relative_to(ROOT))
