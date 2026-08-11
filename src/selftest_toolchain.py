#!/usr/bin/env python3
"""Toolchain self-test — NOT A SCIENCE GATE.

This proves only that ``pdr`` can parse a PDS3 label + fixed-width table in this
environment, and that matplotlib can render a trace to PNG. It uses a synthetic
product generated here; it contains **no Cassini data and no archive content**.

Its only purpose is to separate two failure causes when kill-test 2 is blocked:

    "pdr does not work here"   vs   "the archive host is unreachable"

Passing this says nothing whatsoever about the reproduction. Kill-test 2 is
still ``UNRESOLVED`` until it runs against the real PSI archive.

Usage
-----
    python src/selftest_toolchain.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

N_ROWS = 32

LABEL = """PDS_VERSION_ID       = PDS3
RECORD_TYPE          = FIXED_LENGTH
RECORD_BYTES         = 24
FILE_RECORDS         = {n}
^TABLE               = "SELFTEST.TAB"
DATA_SET_ID          = "SYNTHETIC-SELFTEST-V1.0"
OBJECT               = TABLE
  ROWS               = {n}
  COLUMNS            = 2
  ROW_BYTES          = 24
  INTERCHANGE_FORMAT = ASCII
  OBJECT             = COLUMN
    NAME             = SAMPLE_INDEX
    DATA_TYPE        = ASCII_INTEGER
    START_BYTE       = 1
    BYTES            = 10
    DESCRIPTION      = "Dimensionless sample counter (synthetic)."
  END_OBJECT         = COLUMN
  OBJECT             = COLUMN
    NAME             = AMPLITUDE
    DATA_TYPE        = ASCII_INTEGER
    START_BYTE       = 12
    BYTES            = 10
    DESCRIPTION      = "Synthetic amplitude in arbitrary units."
  END_OBJECT         = COLUMN
END_OBJECT           = TABLE
END
"""


def main() -> int:
    import numpy as np
    import pdr

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rows = []
        for i in range(N_ROWS):
            amplitude = int(1000 * np.exp(-((i - 12) ** 2) / 18.0))
            rows.append(f"{i:>10} {amplitude:>10}\r\n")
        (root / "SELFTEST.TAB").write_text("".join(rows), encoding="ascii", newline="")
        (root / "SELFTEST.LBL").write_text(LABEL.format(n=N_ROWS), encoding="ascii")

        data = pdr.read(str(root / "SELFTEST.LBL"))
        keys = list(data.keys())
        table = None
        for key in keys:
            if hasattr(data[key], "columns"):
                table = data[key]
                break
        if table is None:
            print(f"SELFTEST FAIL — pdr returned no tabular object; keys={keys}", file=sys.stderr)
            return 1
        if len(table) != N_ROWS:
            print(f"SELFTEST FAIL — expected {N_ROWS} rows, got {len(table)}", file=sys.stderr)
            return 1

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(table["SAMPLE_INDEX"], table["AMPLITUDE"], lw=0.8)
        ax.set_xlabel("Sample index [dimensionless]")
        ax.set_ylabel("Amplitude [arbitrary units]")
        fig.tight_layout()
        out = root / "selftest.png"
        fig.savefig(out, dpi=80)
        rendered = out.stat().st_size

    print(f"SELFTEST PASS — pdr {pdr.__version__} parsed {len(table)} rows, "
          f"columns={list(table.columns)}; matplotlib wrote {rendered} bytes.")
    print("This is a TOOLCHAIN check only. It is NOT kill-test 2 and carries no "
          "scientific weight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
