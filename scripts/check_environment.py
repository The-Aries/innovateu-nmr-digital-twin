"""Check generic scientific Python dependencies; no challenge solution here."""

import platform
from importlib import import_module

import numpy as np
from scipy import stats


def main() -> None:
    print(f"Python architecture: {platform.machine()}")
    for package in ("numpy", "scipy", "nibabel", "matplotlib"):
        module = import_module(package)
        print(f"{package}: {module.__version__}")
    sample = np.array([1.0, 2.0, 3.0])
    assert np.isfinite(sample.mean())
    assert np.isfinite(stats.norm.cdf(0.0))
    print("Scientific environment check: PASS")


if __name__ == "__main__":
    main()
