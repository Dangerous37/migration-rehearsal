import argparse
import json
import sys
from pathlib import Path

from engine import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = evaluate(data)
        output = json.dumps(result, indent=2, allow_nan=False)
    except (ValueError, TypeError, KeyError, AttributeError, OSError, ArithmeticError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
