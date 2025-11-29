import configparser
import json
import tomllib
from pathlib import Path
from typing import Optional, Dict, Any

class MetadataDetector:
    """
    Detects metadata (version, description) from application files.
    """
    def detect(self, app_dir: Path) -> Dict[str, Any]:
        """
        Scans the app directory for metadata files and returns a dictionary of found metadata.
        """
        metadata = {}
        
        # 1. Check for application.ini (Mozilla)
        app_ini = list(app_dir.rglob("application.ini"))
        if app_ini:
            # Use the first one found, or maybe prefer the one in root?
            # Zen has it in root.
            try:
                config = configparser.ConfigParser()
                config.read(app_ini[0])
                if "App" in config:
                    if "Version" in config["App"]:
                        metadata["version"] = config["App"]["Version"]
                    if "Name" in config["App"]:
                        metadata["name"] = config["App"]["Name"]
                    if "Vendor" in config["App"]:
                        metadata["vendor"] = config["App"]["Vendor"]
            except Exception as e:
                print(f"Failed to parse application.ini: {e}")

        # 2. Check for package.json (Node/Electron)
        if "version" not in metadata:
            pkg_json = list(app_dir.rglob("package.json"))
            if pkg_json:
                # Prefer root package.json
                # Sort by path length to find the one closest to root?
                pkg_json.sort(key=lambda p: len(str(p)))
                try:
                    with open(pkg_json[0], 'r') as f:
                        data = json.load(f)
                        if "version" in data:
                            metadata["version"] = data["version"]
                        if "name" in data:
                            metadata["name"] = data["name"]
                        if "description" in data:
                            metadata["description"] = data["description"]
                except Exception as e:
                    print(f"Failed to parse package.json: {e}")

        # 3. Check for Cargo.toml (Rust)
        if "version" not in metadata:
            cargo_toml = list(app_dir.rglob("Cargo.toml"))
            if cargo_toml:
                cargo_toml.sort(key=lambda p: len(str(p)))
                try:
                    with open(cargo_toml[0], "rb") as f:
                        data = tomllib.load(f)
                    if "package" in data and "version" in data["package"]:
                        metadata["version"] = data["package"]["version"]
                except Exception as e:
                    print(f"Failed to parse Cargo.toml: {e}")
                    
        return metadata
