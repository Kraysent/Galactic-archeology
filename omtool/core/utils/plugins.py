import glob
import importlib
import pathlib
import sys
from zlog import logger


def import_modules(imports: list[str], has_globs: bool = True):
    if has_globs:
        filenames = []

        for imp in imports:
            filenames.extend(glob.glob(imp))

        imports = filenames

    for filename in imports:
        path = pathlib.Path(filename)
        sys.path.append(str(path.parent))

        try:
            importlib.import_module(path.stem)
        except ImportError as e:
            logger.error().string("path", str(path)).exception("error", e).msg("cannot import file")
