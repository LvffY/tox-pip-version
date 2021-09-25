from subprocess import check_output
from sys import argv

from packaging.specifiers import SpecifierSet
from packaging.version import Version

VERSION_RANGE_OPERATORS = ("==", "!=", "<", "<=", ">", ">=", "~=", "===")


def to_specifer_set(raw_version):
    if any(raw_version.startswith(op) for op in VERSION_RANGE_OPERATORS):
        return SpecifierSet(raw_version)
    return SpecifierSet(f"=={raw_version}")


def main():
    expected_set = to_specifer_set(argv[1])
    raw_setuptools_version = check_output(
        ["pip", "show", "setuptools"]
    ).decode()
    actual_version = Version(
        raw_setuptools_version.split("\n")[1].split(":")[1].strip()
    )
    if actual_version not in expected_set:
        print(f"FAIL: version '{actual_version}' not in set '{expected_set}'")
        return 1
    print(f"PASS: version '{actual_version}' is in set '{expected_set}'")
    return 0


if __name__ == "__main__":
    exit(main())
