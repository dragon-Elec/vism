import os
from pathlib import Path

class PathManager:
    """
    Manages the filesystem paths following XDG Base Directory standards.
    """
    def __init__(self):
        self.home = Path.home()
        self.local_bin = self.home / ".local" / "bin"
        self.data_dir = self.home / ".local" / "share" / "vism"
        self.apps_dir = self.data_dir / "apps"
        self.config_dir = self.home / ".config" / "vism"
        self.manifests_dir = self.config_dir / "manifests"
        
        # Desktop integration paths
        self.applications_dir = self.home / ".local" / "share" / "applications"
        self.icons_dir = self.home / ".local" / "share" / "icons"

    def ensure_dirs(self) -> None:
        """Creates all necessary directories."""
        self.local_bin.mkdir(parents=True, exist_ok=True)
        self.apps_dir.mkdir(parents=True, exist_ok=True)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.applications_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)

    def get_app_dir(self, app_name: str) -> Path:
        """Returns the installation directory for a specific app."""
        return self.apps_dir / app_name

    def get_bin_path(self, binary_name: str) -> Path:
        """Returns the path where the symlink should be created."""
        return self.local_bin / binary_name
