import os
import shutil
import glob
from pathlib import Path
from typing import Optional, Dict, Any

class DesktopIntegrator:
    """
    Handles finding, fixing, and installing .desktop files and icons.
    """
    def __init__(self, applications_dir: Path, icons_dir: Path):
        self.applications_dir = applications_dir
        self.icons_dir = icons_dir

    def integrate(self, app_dir: Path, binary_path: Path, metadata: Dict[str, Any] = None) -> None:
        """
        Scans the app directory for .desktop files and icons, fixes them, and links them.
        If no .desktop file is found, generates one.
        """
        # Find icons first so we have an icon for the desktop file
        main_icon_name = self._process_icons(app_dir, binary_path.name)

        # Find .desktop files
        desktop_files = list(app_dir.glob("**/*.desktop"))
        if desktop_files:
            for desktop_file in desktop_files:
                self._process_desktop_file(desktop_file, binary_path, app_dir)
        else:
            print("No .desktop file found. Generating one...")
            self._generate_desktop_file(app_dir, binary_path, metadata, main_icon_name)

    def _generate_desktop_file(self, app_dir: Path, binary_path: Path, metadata: Dict[str, Any] = None, icon_name: str = None) -> None:
        """
        Generates a .desktop file for the application.
        """
        app_name = binary_path.name.capitalize()
        comment = None
        
        if metadata:
            if "name" in metadata:
                app_name = metadata["name"]
            
            # Construct comment from description or vendor
            if "description" in metadata:
                comment = metadata["description"]
            elif "vendor" in metadata:
                comment = f"Provided by {metadata['vendor']}"

        content = [
            "[Desktop Entry]\n",
            "Type=Application\n",
            f"Name={app_name}\n",
            f"Exec={binary_path}\n",
            "Terminal=false\n",
            "Categories=Utility;\n"
        ]
        
        if comment:
            content.append(f"Comment={comment}\n")
        
        if icon_name:
            content.append(f"Icon={icon_name}\n")
            
        dest_path = self.applications_dir / f"{binary_path.name}.desktop"
        with open(dest_path, 'w') as f:
            f.writelines(content)
        print(f"Generated desktop file: {dest_path}")

    def _process_desktop_file(self, desktop_file: Path, binary_path: Path, app_dir: Path) -> None:
        """
        Fixes the Exec and Icon paths in a .desktop file and installs it.
        """
        with open(desktop_file, 'r') as f:
            lines = f.readlines()

        new_lines = []
        
        for line in lines:
            if line.startswith("Exec="):
                parts = line.split("=", 1)
                cmd_parts = parts[1].strip().split(" ", 1)
                args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                new_lines.append(f"Exec={binary_path} {args}\n")
            elif line.startswith("Icon="):
                # We assume icons are installed to standard locations
                new_lines.append(line)
            else:
                new_lines.append(line)

        # Write the fixed file to ~/.local/share/applications/
        dest_path = self.applications_dir / desktop_file.name
        with open(dest_path, 'w') as f:
            f.writelines(new_lines)
        print(f"Installed desktop file: {dest_path}")

    def _process_icons(self, app_dir: Path, app_name: str) -> Optional[str]:
        """
        Finds icons and links them to ~/.local/share/icons/.
        Returns the name of the main icon if found/created.
        """
        # Look for common icon formats
        extensions = ["*.png", "*.svg", "*.xpm", "*.ico"]
        found_icons = []
        for ext in extensions:
            found_icons.extend(app_dir.glob(f"**/{ext}"))
        
        if not found_icons:
            return None

        # Sort icons by size (heuristic: larger file size ~ higher resolution)
        # This helps prefer high-res pngs over tiny ones.
        found_icons.sort(key=lambda p: p.stat().st_size, reverse=True)

        main_icon_name = None
        
        for icon in found_icons:
            dest = self.icons_dir / icon.name
            if not dest.exists():
                shutil.copy2(icon, dest)
                print(f"Installed icon: {dest}")
            
            # Check if this icon matches the app name
            if icon.stem.lower() == app_name.lower():
                main_icon_name = icon.stem

        # If we didn't find an icon named exactly like the app,
        # pick the largest one and symlink/copy it to app_name.ext
        if not main_icon_name and found_icons:
            best_icon = found_icons[0]
            extension = best_icon.suffix
            target_name = f"{app_name}{extension}"
            target_path = self.icons_dir / target_name
            
            if not target_path.exists():
                shutil.copy2(best_icon, target_path)
                print(f"Created main icon alias: {target_path}")
            
            main_icon_name = app_name

        return main_icon_name
