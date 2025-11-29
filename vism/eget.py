import subprocess
import shutil
import os
from typing import List, Optional

class EgetWrapper:
    """
    Wraps the 'eget' command line tool.
    """
    def __init__(self):
        self.eget_path = shutil.which("eget")
        if not self.eget_path:
            raise FileNotFoundError("eget not found in PATH. Please install eget first.")

    def install(self, repo: str, target_path: str, asset_filters: List[str] = None, 
                tag: str = None, upgrade_only: bool = False, file_only: str = None,
                download_only: bool = False, all_files: bool = False) -> None:
        """
        Runs eget to install a package.
        """
        cmd = [self.eget_path, repo]

        if target_path:
            cmd.extend(["--to", target_path])
        
        if tag:
            cmd.extend(["--tag", tag])
            
        if upgrade_only:
            cmd.append("--upgrade-only")
            
        if download_only:
            cmd.append("--download-only")
            
        if all_files:
            cmd.append("--all")

        if file_only:
            cmd.extend(["--file", file_only])

        if asset_filters:
            for asset in asset_filters:
                cmd.extend(["--asset", asset])

        # Run the command
        # We allow stdout/stderr to flow to the terminal so the user sees eget's progress bars
        subprocess.check_call(cmd)

    def download(self, repo: str, dest_dir: str, asset_filters: List[str] = None, tag: str = None) -> str:
        """
        Downloads the asset to the destination directory and returns the path to the downloaded file.
        """
        # We use --to dest_dir and --download-only
        # We need to find out what file was downloaded.
        # Eget doesn't easily tell us the filename unless we parse stdout.
        # So we'll list the directory before and after? 
        # Or just assume dest_dir is empty.
        
        cmd = [self.eget_path, repo, "--to", dest_dir, "--download-only"]
        
        if tag:
            cmd.extend(["--tag", tag])
            
        if asset_filters:
            for asset in asset_filters:
                cmd.extend(["--asset", asset])
                
        subprocess.check_call(cmd)
        
        # Find the file
        files = os.listdir(dest_dir)
        if not files:
            raise FileNotFoundError("Eget did not download any file.")
        if len(files) > 1:
            # If multiple files, maybe we picked up something else?
            # But if we created a temp dir, it should be the only one.
            pass
            
        return os.path.join(dest_dir, files[0])

    def get_version(self) -> str:
        """Returns the version of eget."""
        result = subprocess.run([self.eget_path, "--version"], capture_output=True, text=True)
        return result.stdout.strip()
