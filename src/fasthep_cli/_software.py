"""Functions for finding FAST-HEP software"""
from __future__ import annotations

import pkg_resources


def _is_fasthep_package(package_name: str) -> bool:
    """
    Check if a package is a FAST-HEP package
    """
    fast_hep_prefixes = ["fasthep-", "fast-", "scikit-validate"]
    for prefix in fast_hep_prefixes:
        if package_name.startswith(prefix):
            return True
    return False


def _find_fast_hep_packages() -> list[tuple[str, str]]:
    """
    Find all FAST-HEP packages
    """
    fasthep_packages = {}
    installed_packages = list(pkg_resources.working_set)
    for installed_package in installed_packages:
        if _is_fasthep_package(installed_package.key):
            fasthep_packages[installed_package.key] = installed_package.version
    return sorted(fasthep_packages.items(), key=lambda x: (x[0], x[1]))
