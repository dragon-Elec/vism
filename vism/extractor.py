import shutil
import os
import tarfile
import zipfile
from pathlib import Path

class Extractor:
    """
    Handles extraction of archives.
    """
    def extract(self, archive_path: str, dest_dir: str) -> None:
        """
        Extracts the archive to the destination directory.
        """
        archive_path = Path(archive_path)
        dest_dir = Path(dest_dir)
        
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
        elif archive_path.suffix in ['.tar', '.gz', '.xz', '.bz2', '.tgz']:
            # tarfile.is_tarfile check?
            if tarfile.is_tarfile(archive_path):
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(dest_dir)
            else:
                # Maybe it's just a compressed file (like .gz) but not a tar?
                # Eget usually handles extraction, but if we use --download-only, we get the raw asset.
                # If it's just a binary.gz, we should decompress it.
                # For now, let's assume it's an archive if we are in this flow.
                # If it's not an archive, we might just move it?
                pass
        else:
            # Not a known archive format. 
            # It might be an AppImage or a binary.
            # In that case, we just move it to the dest_dir.
            shutil.move(str(archive_path), str(dest_dir / archive_path.name))
