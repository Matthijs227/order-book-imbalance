"""Download the free LOBSTER sample files (Nasdaq TotalView-ITCH, reconstructed order book, 2012-06-21).

The samples are hosted on the LOBSTER legacy site: https://php.lobsterdata.com/info/DataSamples.php
Files are saved to data/raw and unzipped to data/unzipped (both git-ignored).

    python download_samples.py
"""
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://php.lobsterdata.com/info/sample/"
FILES = [f"LOBSTER_SampleFile_{t}_2012-06-21_10.zip" for t in ["AAPL", "AMZN", "GOOG", "INTC", "MSFT"]]
RAW = Path(__file__).parent / "data" / "raw"
OUT = Path(__file__).parent / "data" / "unzipped"


def safe_extract(z: zipfile.ZipFile, dest: Path) -> None:
    """Extract without letting an archive path escape the destination folder."""
    dest = dest.resolve()
    for m in z.namelist():
        target = (dest / m).resolve()
        if dest not in target.parents and target != dest:
            raise ValueError(f"unsafe path in archive: {m}")
    z.extractall(dest)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        f = RAW / name
        if not f.exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(BASE + name, f)
        with open(f, "rb") as fh:
            if fh.read(2) != b"PK":
                raise RuntimeError(f"{name} is not a zip file; the download location may have moved")
        with zipfile.ZipFile(f) as z:
            safe_extract(z, OUT / name.removesuffix(".zip"))
    print(f"done: {OUT}")


if __name__ == "__main__":
    main()
