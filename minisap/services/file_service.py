import csv
import shutil
from contextlib import contextmanager
from pathlib import Path
import fcntl


class CSVFileService:
    def __init__(self, base_dir: Path, logger):
        self.base_dir = base_dir
        self.logger = logger

    @contextmanager
    def _locked_file(self, path: Path, mode: str):
        with open(path, mode, newline="", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yield f
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def ensure_csv(self, rel_path: str, headers: list[str], seed_rows: list[dict] | None = None):
        full = self.base_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        if not full.exists():
            with open(full, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in seed_rows or []:
                    writer.writerow(row)
            self.logger.info("CSV created: %s", full)

    def read_csv(self, rel_path: str) -> list[dict]:
        full = self.base_dir / rel_path
        with open(full, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def write_csv(self, rel_path: str, headers: list[str], rows: list[dict]):
        full = self.base_dir / rel_path
        if full.exists():
            backup = full.with_suffix(full.suffix + ".bak")
            shutil.copy2(full, backup)
            self.logger.info("Backup created: %s", backup)
        with self._locked_file(full, "w") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                safe = {k: row.get(k, "") for k in headers}
                writer.writerow(safe)
        self.logger.info("CSV updated: %s (%s rows)", rel_path, len(rows))
