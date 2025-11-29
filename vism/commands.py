import os
import sys
import shutil
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from vism.config import ConfigManager
from vism.paths import PathManager
from vism.eget import EgetWrapper
from vism.desktop import DesktopIntegrator

class CommandManager:
    def __init__(self):
        self.paths = PathManager()
        self.paths.ensure_dirs()
        self.config = ConfigManager(str(self.paths.manifests_dir))
        self.eget = EgetWrapper()
        self.desktop = DesktopIntegrator(self.paths.applications_dir, self.paths.icons_dir)

    def install(self, repo_url: str, alias: Optional[str] = None, 
                tag: Optional[str] = None, upgrade_only: bool = False,
                file_only: Optional[str] = None, download_only: bool = False,
                all_files: bool = False, asset_filters: List[str] = None) -> None:
        
        # 1. Determine app name
        if alias:
            app_name = alias
        else:
            # Infer from repo url (e.g. "zen-browser/desktop" -> "desktop" -> maybe bad? 
            # usually user/repo -> repo. But for "zen-browser/desktop", "desktop" is generic.
            # Let's use the repo name.
            app_name = repo_url.split("/")[-1]
        
        print(f"Installing {app_name} from {repo_url}...")

        # 2. Check if already installed
        if self.config.load_manifest(app_name) and not upgrade_only:
            print(f"Warning: '{app_name}' is already managed by vism. Use 'vism update {app_name}' to upgrade.")
            # We continue? Or abort? 
            # If user explicitly ran install, maybe they want to reinstall/overwrite.
            # Let's continue but warn.

        # 3. Prepare paths
        app_dir = self.paths.get_app_dir(app_name)
        # We install the binary as the app_name inside the app_dir
        # But if it's a folder install (like Zen), we might target the dir.
        # eget --to <path>
        # If <path> is a directory, eget extracts there.
        # If <path> is a file, eget extracts to that file.
        
        # For simplicity, we always target app_dir/app_name for the primary binary if single file,
        # or app_dir/ if multiple files.
        
        # If we don't know if it's a single binary or not, it's tricky.
        # Eget default: extracts to current dir.
        
        # Strategy:
        # Always extract to app_dir.
        # Then find the executable to link.
        
        if app_dir.exists():
            # If reinstalling, maybe clean up?
            # For now, let eget handle overwrites.
            pass
        else:
            app_dir.mkdir(parents=True, exist_ok=True)

        # 4. Run Eget and Extract
        # New workflow: Download to temp dir -> Extract -> Move to app_dir
        import tempfile
        from vism.extractor import Extractor
        
        extractor = Extractor()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Downloading to temporary directory {temp_dir}...")
            try:
                downloaded_file = self.eget.download(
                    repo=repo_url,
                    dest_dir=temp_dir,
                    tag=tag,
                    asset_filters=asset_filters
                )
                print(f"Downloaded: {downloaded_file}")
                
                print(f"Extracting to {app_dir}...")
                extractor.extract(downloaded_file, str(app_dir))
                
            except Exception as e:
                print(f"Installation failed: {e}")
                # Clean up app_dir if we created it?
                # Maybe not, user might want to inspect.
                return

        # 5. Post-Install: Find the binary to link
        # Now app_dir contains the full extracted structure.
        # We need to find the executable.
        
        # Heuristic:
        # 1. If there's a file with `app_name` (or `alias`), use that.
        # 2. If there's a `bin` folder, look in there.
        # 3. Recursive search for executable with app_name?
        
        # Let's look for executables in app_dir recursively?
        # Or just top level and one level down?
        
        # For Zen: app_dir/zen/zen is the binary.
        # So we should look recursively.
        
        binary_to_link = None
        
        # Helper to check if file is executable
        def is_exe(f: Path) -> bool:
            return f.is_file() and os.access(f, os.X_OK)
            
        # 1. Check exact match in root
        candidate = app_dir / app_name
        if is_exe(candidate):
            binary_to_link = candidate
            
        # 2. Check exact match in subdirs (depth 1)
        if not binary_to_link:
            for child in app_dir.iterdir():
                if child.is_dir():
                    candidate = child / app_name
                    if is_exe(candidate):
                        binary_to_link = candidate
                        break
        
        # 3. Search for any executable named app_name
        if not binary_to_link:
            for path in app_dir.rglob(app_name):
                if is_exe(path):
                    binary_to_link = path
                    break

        # 4. Fallback: If only one executable in root?
        if not binary_to_link:
             executables = [f for f in app_dir.iterdir() if is_exe(f)]
             if len(executables) == 1:
                 binary_to_link = executables[0]

        symlink_path = None
        if binary_to_link:
            symlink_path = self.paths.get_bin_path(app_name)
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
            
            os.symlink(binary_to_link, symlink_path)
            print(f"Linked {binary_to_link} to {symlink_path}")
        else:
            print(f"Could not determine main binary to link. You may need to link it manually from {app_dir}")

        # 6. Desktop Integration
        # Pass the app_dir (root of extraction)
        # Detect metadata (version)
        from vism.metadata import MetadataDetector
        detector = MetadataDetector()
        metadata = detector.detect(app_dir)
        
        self.desktop.integrate(app_dir, binary_to_link if binary_to_link else app_dir, metadata)

        # 7. Save Manifest
        
        manifest_data = {
            "repo": repo_url,
            "installed_at": datetime.now().isoformat(),
            "files": [], # TODO: Track installed files
            "version": metadata.get("version", "unknown")
        }
        if tag:
            manifest_data["tag"] = tag
            
        self.config.save_manifest(app_name, manifest_data)
        print(f"Successfully installed {app_name}!")
        if "version" in metadata:
            print(f"Detected version: {metadata['version']}")

    def remove(self, app_name: str) -> None:
        manifest = self.config.load_manifest(app_name)
        if not manifest:
            print(f"App '{app_name}' not found.")
            return

        print(f"Uninstalling {app_name}...")

        # 1. Remove symlink
        symlink_path = manifest.get("symlink_path")
        if symlink_path:
            p = Path(symlink_path)
            if p.exists() or p.is_symlink():
                p.unlink()
                print(f"Removed symlink: {symlink_path}")

        # 2. Remove app directory
        # We derived app_dir from paths manager, but let's check manifest install_path
        # install_path might be the binary file.
        # The app dir is self.paths.get_app_dir(app_name)
        app_dir = self.paths.get_app_dir(app_name)
        if app_dir.exists():
            shutil.rmtree(app_dir)
            print(f"Removed directory: {app_dir}")

        # 3. Remove desktop files/icons?
        # We didn't track exactly which ones we installed in the manifest (yet).
        # But we can look for ones with the app_name in ~/.local/share/applications
        # This is risky if we delete something else.
        # For now, let's leave them or try to be smart.
        # If we named the .desktop file same as app_name, we can delete it.
        desktop_file = self.paths.applications_dir / f"{app_name}.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
            print(f"Removed desktop file: {desktop_file}")
            
        # 4. Delete manifest
        self.config.delete_manifest(app_name)
        print(f"Uninstalled {app_name}.")

    def list(self) -> None:
        apps = self.config.list_apps()
        if not apps:
            print("No apps installed.")
            return

        print(f"{'Name':<20} {'Repo':<40} {'Version':<15} {'Installed':<15}")
        print("-" * 90)
        for app in apps:
            installed_date = app.get('installed_at', '')[:10]
            version = app.get('version', '')
            print(f"{app['name']:<20} {app['repo']:<40} {version:<15} {installed_date:<15}")
