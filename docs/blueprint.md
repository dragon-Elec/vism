This plan leverages `eget` as the heavy lifter while `vsim` provides the brain (state management) and the body (file organization).

### 1. Core Philosophy
**"The Stateful Brain for the Stateless Engine."**
*   **Engine (`eget`):** Handles network, GitHub API, asset detection, downloading, extraction, and verification.
*   **Manager (`vsim`):** Handles where files go, remembers what is installed, manages symbolic links, and allows clean uninstallation.

---

### 2. The Filesystem Architecture
`vsim` will strictly follow Linux standards (XDG Base Directory).

```text
/home/ray/
├── .local/
│   ├── bin/                      # 1. THE EXECUTABLES
│   │   ├── zen -> ...            #    (Symlinks created by vsim)
│   │   └── micro -> ...
│   │
│   └── share/
│       └── vsim/
│           └── apps/             # 2. THE STORAGE
│               ├── zen/          #    (Actual application files)
│               │   └── zen       #    (The binary downloaded by eget)
│               └── micro/
│                   └── micro
│
└── .config/
    └── vsim/
        └── manifests/            # 3. THE BRAIN
            ├── zen.yml           #    (One file per installed app)
            └── micro.yml
```

---

### 3. The Manifest Structure (YAML)
Each installed application gets a dedicated file in `~/.config/vsim/manifests/`.

**Example: `zen.yml`**
```yaml
app_name: "zen"                    # The name used for vsim commands
repo_url: "zen-browser/desktop"    # The GitHub source
install_date: "2025-05-20"
install_path: "/home/ray/.local/share/vsim/apps/zen/zen"
symlink_path: "/home/ray/.local/bin/zen"
eget_args: []                      # Any special flags used during install
```

---

### 4. The Command Workflow

#### A. `vsim install <repo_url> [alias]`
*   **Example:** `vsim install zen-browser/desktop zen`
*   **Step 1: Preparation**
    *   Checks if `eget` is installed.
    *   Checks if `~/.local/bin` is in the system PATH (warns if not).
    *   Determines the `app_name` (uses the alias "zen" if provided, otherwise infers from repo).
*   **Step 2: Execution (The `eget` handoff)**
    *   Constructs the target path: `~/.local/share/vsim/apps/zen/zen`
    *   Runs: `eget zen-browser/desktop --to ~/.local/share/vsim/apps/zen/zen`
*   **Step 3: Integration**
    *   Creates symlink: `ln -s .../apps/zen/zen ~/.local/bin/zen`
*   **Step 4: Memory**
    *   Creates `~/.config/vsim/manifests/zen.yml`.

#### B. `vsim uninstall <app_name>`
*   **Example:** `vsim uninstall zen`
*   **Step 1: Lookup**
    *   Reads `zen.yml` to find the paths.
*   **Step 2: Cleanup**
    *   Removes the symlink at `symlink_path`.
    *   Removes the entire directory containing `install_path`.
*   **Step 3: Amnesia**
    *   Deletes `zen.yml`.

#### C. `vsim update <app_name>`
*   **Example:** `vsim update zen`
*   **Step 1: Lookup**
    *   Reads `zen.yml` to get the `repo_url` and `install_path`.
*   **Step 2: Check & Upgrade (The `eget` handoff)**
    *   Runs: `eget <repo_url> --to <install_path> --upgrade-only`
    *   *Note:* `eget` handles the version comparison logic internally. If the GitHub release is newer than the local file, it downloads. If not, it does nothing.
*   **Step 3: Notify**
    *   Reports to the user if an update occurred or if they are already on the latest version.

#### D. `vsim list`
*   **Example:** `vsim list`
*   **Step 1: Scan**
    *   Loops through all `.yml` files in `~/.config/vsim/manifests/`.
*   **Step 2: Display**
    *   Prints a pretty table:
    ```text
    Name      Repo                   Installed
    ------------------------------------------
    zen       zen-browser/desktop    2025-05-20
    micro     zyedidia/micro         2025-05-21
    ```

---

### 5. Implementation Roadmap

This is how we will build it.

**Phase 1: Setup & Helper Classes (Python)**
*   Create `ConfigManager`: Handles reading/writing the YAML manifests.
*   Create `PathManager`: Ensures directories exist (`mkdir -p`).
*   Create `EgetWrapper`: A python class that constructs the `subprocess` calls to `eget`.

**Phase 2: The Core Commands**
*   Implement `install` logic (The glue between `EgetWrapper` and `ConfigManager`).
*   Implement `uninstall` logic.

**Phase 3: CLI Interface**
*   Use Python's `argparse` library to handle the user inputs (`vsim <command> <args>`).

**Phase 4: "Zen Mode" (Advanced)**
*   Add support for passing flags to `eget` (like `--all` or `--file`) so we can handle complex packages like Zen Browser that might be a folder rather than a single binary.

**Phase 5: Desktop Integration**
*   **Desktop Files:** Scan for `.desktop` files in downloaded assets.
*   **Path Fixing:** Automatically update `Exec=` and `Icon=` paths in `.desktop` files to point to the installed location.
*   **Installation:** Link `.desktop` files to `~/.local/share/applications/` and icons to `~/.local/share/icons/`.

**Phase 6: Future Considerations**
*   **System-wide Install (`--root`):** Allow installing to `/opt/vsim` and `/usr/local/bin` for all users. This will require root privileges.
*   **Conflict Detection:** Warn if an app is already installed via system package manager (e.g., `apt`, `dnf`) before installing.

### 6. Immediate Action Items
To get started, you need to:

1.  **Install `eget` manually** (The bootstrap step).
    ```bash
    curl https://zyedidia.github.io/eget.sh | sh
    mkdir -p ~/.local/bin
    mv eget ~/.local/bin/
    ```
2.  **Verify** it works: `eget --version`.
3.  **Confirm** you are ready to start coding `vsim.py`.