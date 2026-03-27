from pathlib import Path

from server.utils.logger import log


class folder:
    """文件夹路径常量"""

    ROOT = Path(__file__).parent.parent.parent
    PUBLIC = ROOT / "public"
    DATAS = ROOT / "datas"
    IMAGES = DATAS / "images"


def copy(src: Path, dst: Path, force: bool = False):
    """复制文件"""
    if not src.exists():
        log("file").error("source file %s does not exist", src)
        raise FileNotFoundError(f"Source file does not exist: {src}")
    if not dst.exists() or force:
        dst.write_bytes(src.read_bytes())
        log("file").info("copied %s to %s", src, dst)
    else:
        log("file").info("file %s already exists, skipping copy", dst)
        raise FileExistsError(f"File already exists: {dst}")
