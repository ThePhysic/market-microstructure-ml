"""Run the extension CLI without changing the original study entry point."""
import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

from .cli import main

raise SystemExit(main())
