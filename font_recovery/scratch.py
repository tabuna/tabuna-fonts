"""Keep native raster searches bounded in disk usage."""
from pathlib import Path
import re
import shutil


def require_free_space(workspace: Path, minimum_gib: float = 2.0) -> None:
    free = shutil.disk_usage(workspace).free
    if free < minimum_gib * 2**30:
        raise RuntimeError(
            f"Raster search stopped: only {free / 2**30:.2f} GiB free; "
            f"at least {minimum_gib:.1f} GiB required."
        )


def retain_trial_artifacts(directory: Path, keep: set[int]) -> int:
    """Remove expendable trial renders, retaining numeric results separately.

    Only direct, nonsymlink trial-NNNN directories beneath this workspace's
    build/font-recovery tree can be removed. Call after saving the search JSON.
    """
    allowed = Path(__file__).resolve().parents[1] / 'build' / 'font-recovery'
    directory = directory.resolve()
    if not directory.is_relative_to(allowed.resolve()):
        raise ValueError('Trial cleanup must stay inside build/font-recovery')
    removed = 0
    for path in directory.iterdir():
        match = re.fullmatch(r'trial-(\d{4,})', path.name)
        if (match and int(match[1]) not in keep and path.is_dir()
                and not path.is_symlink()):
            shutil.rmtree(path)
            removed += 1
    return removed
