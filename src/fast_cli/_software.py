from __future__ import annotations

import pkg_resources


def _find_fast_hep_packages() -> list[tuple[str, str]]:
    """
    Find all FAST-HEP packages
    """
    fasthep_packages = {}
    installed_packages = pkg_resources.working_set
    for installed_package in installed_packages:
        if installed_package.key.startswith(
            "fast-"
        ) or installed_package.key.startswith("scikit-validate"):
            fasthep_packages[installed_package.key] = installed_package.version
    return sorted(fasthep_packages.items(), key=lambda x: (x[0], x[1]))
