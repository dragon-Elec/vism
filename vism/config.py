import os
import yaml
from typing import Dict, List, Optional

class ConfigManager:
    """
    Manages the reading and writing of application manifests.
    Manifests are stored as YAML files in ~/.config/vism/manifests/
    """
    def __init__(self, manifests_dir: str):
        self.manifests_dir = manifests_dir
        os.makedirs(self.manifests_dir, exist_ok=True)

    def _get_manifest_path(self, app_name: str) -> str:
        return os.path.join(self.manifests_dir, f"{app_name}.yml")

    def save_manifest(self, app_name: str, data: Dict) -> None:
        """Saves the manifest for an app."""
        path = self._get_manifest_path(app_name)
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)

    def load_manifest(self, app_name: str) -> Optional[Dict]:
        """Loads the manifest for an app. Returns None if not found."""
        path = self._get_manifest_path(app_name)
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def delete_manifest(self, app_name: str) -> None:
        """Deletes the manifest for an app."""
        path = self._get_manifest_path(app_name)
        if os.path.exists(path):
            os.remove(path)

    def list_apps(self) -> List[Dict]:
        """Lists all installed apps and their manifests."""
        apps = []
        if not os.path.exists(self.manifests_dir):
            return apps
            
        for filename in os.listdir(self.manifests_dir):
            if filename.endswith(".yml"):
                path = os.path.join(self.manifests_dir, filename)
                try:
                    with open(path, 'r') as f:
                        data = yaml.safe_load(f)
                        if data:
                            data['name'] = filename[:-4]
                            apps.append(data)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        return apps

