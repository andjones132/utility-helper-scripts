#!/usr/bin/env python3
"""
Compress Folders Filtered — Repo Archiver (7-Zip GUI)

Purpose
-------
Create individual .7z archives for each "repo" folder located directly under a chosen
parent directory. Designed as a "push here" one-click archiver for developers who want
to back up multiple project folders in a single operation.

Inputs (via GUI)
----------------
- **Repos parent folder** : The folder that *contains* the repo subfolders to archive.
  Each immediate subdirectory becomes its own .7z archive.
- **Output folder**       : Destination where .7z files are written.
  Created automatically if it does not exist.
- **7z.exe path**         : Optional. If left blank the script searches PATH and the
  Windows default install location automatically.
- **Dictionary size**     : LZMA2 -md setting (default: 256m).
- **Threads**             : 7-Zip -mmt setting (default: on = auto).
- **Solid archive**       : Checkbox to enable -ms=on (better ratio for many small files).
- **Exclude .git**        : Checkbox to omit .git directories (smaller archives; no history).

Outputs
-------
- One <repo_folder_name>.7z per immediate subdirectory in the chosen parent folder.

Requirements
------------
- Python 3.11+ (Tkinter included with standard CPython)
- 7-Zip installed OR 7z/7za/7zr on PATH
  Windows default search path: %ProgramFiles%\\7-Zip\\7z.exe

Run
---
    python scripts/compress_folders_filtered.py

Version History
---------------
See CHANGELOG.md
"""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ─────────────────────────────────────────────────────────────────────────────
# Defaults (edit here or override in the GUI)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_EXCLUDE_DIRS: list[str] = [
    ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules",
    "dist", "build", "out", "target",
    ".next", ".nuxt", ".cache",
    ".tox", ".eggs",
    ".idea", ".vscode",
]

DEFAULT_EXCLUDE_GLOBS: list[str] = [
    "*.pyc", "*.pyo", "*.log", "*.tmp", "*.temp",
    "*.obj", "*.o", "*.class",
]

DEFAULT_DICT_SIZE: str = "256m"
DEFAULT_THREADS: str = "on"

# subprocess timeout per archive (seconds). Increase for very large repos.
SUBPROCESS_TIMEOUT: int = 3600


# ─────────────────────────────────────────────────────────────────────────────
# Pure functions (fully testable without a GUI)
# ─────────────────────────────────────────────────────────────────────────────

def find_7z(explicit_path: str | None = None) -> str:
    """
    Locate a 7-Zip executable.

    Search order
    ------------
    1. ``explicit_path`` if provided and the file exists.
    2. PATH search for ``7z``, ``7za``, ``7zr``.
    3. Windows default: ``%ProgramFiles%\\7-Zip\\7z.exe``.

    Parameters
    ----------
    explicit_path : str | None
        Optional override path supplied by the user.

    Returns
    -------
    str
        Absolute path to the 7-Zip executable.

    Raises
    ------
    FileNotFoundError
        If no 7-Zip executable can be found anywhere.
    ValueError
        If ``explicit_path`` is provided but the file does not exist.
    """
    if explicit_path:
        p = Path(explicit_path)
        if p.is_file():
            return str(p.resolve())
        raise ValueError(
            f"Specified 7-Zip path does not exist or is not a file: {explicit_path}"
        )

    exe = shutil.which("7z") or shutil.which("7za") or shutil.which("7zr")
    if exe:
        return exe

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    candidate = Path(program_files) / "7-Zip" / "7z.exe"
    if candidate.is_file():
        return str(candidate)

    raise FileNotFoundError(
        "Could not find a 7-Zip executable (7z / 7za / 7zr). "
        "Install 7-Zip from https://7-zip.org or specify the path in the GUI."
    )


def build_7z_command(
    sevenzip: str,
    archive_path: Path,
    repo_path: Path,
    dict_size: str,
    threads: str,
    solid: bool,
    exclude_dirs: list[str],
    exclude_globs: list[str],
) -> list[str]:
    """
    Build the 7-Zip command list to archive a single folder.

    Parameters
    ----------
    sevenzip : str
        Absolute path to the 7z executable.
    archive_path : Path
        Destination .7z file path.
    repo_path : Path
        Source folder to archive (must exist and be a directory).
    dict_size : str
        LZMA2 dictionary size (e.g. ``"128m"``, ``"256m"``).
    threads : str
        Thread count string for ``-mmt`` (e.g. ``"on"`` or ``"8"``).
    solid : bool
        ``True`` to enable solid mode (``-ms=on``).
    exclude_dirs : list[str]
        Directory names to exclude recursively (passed as ``-xr!<name>``).
    exclude_globs : list[str]
        File glob patterns to exclude recursively (passed as ``-xr!<glob>``).

    Returns
    -------
    list[str]
        Full command list ready for ``subprocess.run()``.

    Raises
    ------
    ValueError
        If ``dict_size`` or ``threads`` is empty.
    FileNotFoundError
        If ``repo_path`` does not exist or is not a directory.
    """
    if not dict_size:
        raise ValueError("dict_size must not be empty.")
    if not threads:
        raise ValueError("threads must not be empty.")
    if not repo_path.is_dir():
        raise FileNotFoundError(f"Source folder does not exist: {repo_path}")

    cmd: list[str] = [
        sevenzip, "a",
        "-t7z",
        "-m0=lzma2",
        "-mx=9",
        f"-md={dict_size}",
        "-mfb=64",
        f"-mmt={threads}",
        "-ms=on" if solid else "-ms=off",
    ]

    for d in exclude_dirs:
        cmd.append(f"-xr!{d}")
    for g in exclude_globs:
        cmd.append(f"-xr!{g}")

    cmd.append(str(archive_path))
    cmd.append(str(repo_path))
    return cmd


def list_repo_subfolders(parent: Path) -> list[Path]:
    """
    Return a sorted list of immediate subdirectories of *parent*.

    Parameters
    ----------
    parent : Path
        The parent directory to inspect.

    Returns
    -------
    list[Path]
        Sorted list of subdirectory paths (empty list if none).

    Raises
    ------
    FileNotFoundError
        If ``parent`` does not exist.
    NotADirectoryError
        If ``parent`` exists but is not a directory.
    """
    if not parent.exists():
        raise FileNotFoundError(f"Parent folder does not exist: {parent}")
    if not parent.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {parent}")
    return sorted(p for p in parent.iterdir() if p.is_dir())


def run_archive(
    cmd: list[str],
    timeout: int = SUBPROCESS_TIMEOUT,
) -> tuple[int, str, str]:
    """
    Execute a 7-Zip command and return results.

    Parameters
    ----------
    cmd : list[str]
        Command list from :func:`build_7z_command`.
    timeout : int
        Maximum seconds to wait for the subprocess (default: 3600).

    Returns
    -------
    tuple[int, str, str]
        ``(returncode, stdout, stderr)``

    Raises
    ------
    subprocess.TimeoutExpired
        If the process exceeds *timeout* seconds.
    FileNotFoundError
        If the executable in ``cmd[0]`` is not found.
    PermissionError
        If the process cannot be started due to permissions.
    """
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        raise subprocess.TimeoutExpired(
            cmd, timeout,
            output=f"Process exceeded {timeout}s timeout."
        ) from exc
    except PermissionError as exc:
        raise PermissionError(
            f"Permission denied launching 7-Zip: {cmd[0]}"
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# Tkinter GUI
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    """
    Tkinter GUI to archive multiple repo folders with 7-Zip.

    UI Flow
    -------
    1. Select the parent folder that *contains* the repo subfolders.
    2. Select the output folder for .7z archives.
    3. (Optional) specify the 7z executable path.
    4. Adjust compression options.
    5. Click **Start Archiving** — each subfolder is archived independently.

    Notes
    -----
    Compression runs on a background thread so the GUI remains responsive.
    The **Stop** button sets a flag; the worker finishes the current repo
    then exits gracefully.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Repo Archiver (7-Zip)")
        self.geometry("760x480")
        self.resizable(False, False)

        self._stop_requested: bool = False
        self.worker_thread: threading.Thread | None = None

        # StringVars / BooleanVars
        self.repos_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.sevenz_path = tk.StringVar()
        self.dict_size = tk.StringVar(value=DEFAULT_DICT_SIZE)
        self.threads = tk.StringVar(value=DEFAULT_THREADS)
        self.solid = tk.BooleanVar(value=True)
        self.exclude_git = tk.BooleanVar(value=True)

        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        pad: dict[str, int] = {"padx": 10, "pady": 6}

        # Folder selection
        frm_paths = ttk.LabelFrame(self, text="Folders")
        frm_paths.pack(fill="x", padx=10, pady=10)

        ttk.Label(frm_paths, text="Repos parent folder (contains repo subfolders):").grid(
            row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm_paths, textvariable=self.repos_dir, width=85).grid(
            row=1, column=0, sticky="w", **pad)
        ttk.Button(frm_paths, text="Browse…", command=self.pick_repos_dir).grid(
            row=1, column=1, sticky="e", **pad)

        ttk.Label(frm_paths, text="Output folder (archives will be created here):").grid(
            row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm_paths, textvariable=self.output_dir, width=85).grid(
            row=3, column=0, sticky="w", **pad)
        ttk.Button(frm_paths, text="Browse…", command=self.pick_output_dir).grid(
            row=3, column=1, sticky="e", **pad)

        ttk.Label(frm_paths, text="7z.exe path (optional — leave blank if 7z is on PATH):").grid(
            row=4, column=0, sticky="w", **pad)
        ttk.Entry(frm_paths, textvariable=self.sevenz_path, width=85).grid(
            row=5, column=0, sticky="w", **pad)
        ttk.Button(frm_paths, text="Browse…", command=self.pick_7z_path).grid(
            row=5, column=1, sticky="e", **pad)

        # Compression options
        frm_opts = ttk.LabelFrame(self, text="Compression options")
        frm_opts.pack(fill="x", padx=10, pady=6)

        ttk.Checkbutton(
            frm_opts,
            text="Solid archive (-ms=on) — better compression for many small files",
            variable=self.solid,
        ).grid(row=0, column=0, columnspan=4, sticky="w", **pad)

        ttk.Label(frm_opts, text="Dictionary size (-md):").grid(
            row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm_opts, textvariable=self.dict_size, width=15).grid(
            row=1, column=1, sticky="w", **pad)

        ttk.Label(frm_opts, text="Threads (-mmt):").grid(
            row=1, column=2, sticky="w", **pad)
        ttk.Entry(frm_opts, textvariable=self.threads, width=10).grid(
            row=1, column=3, sticky="w", **pad)

        ttk.Checkbutton(
            frm_opts,
            text="Exclude .git directory (smaller archive — repo history NOT preserved)",
            variable=self.exclude_git,
        ).grid(row=2, column=0, columnspan=4, sticky="w", **pad)

        # Action buttons
        frm_run = ttk.Frame(self)
        frm_run.pack(fill="x", padx=10, pady=8)

        self.btn_start = ttk.Button(frm_run, text="▶  Start Archiving", command=self.start)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(frm_run, text="■  Stop", command=self.stop, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        # Status panel
        frm_status = ttk.LabelFrame(self, text="Status")
        frm_status.pack(fill="both", expand=True, padx=10, pady=10)

        self.progress = ttk.Progressbar(
            frm_status, orient="horizontal", mode="determinate", length=720)
        self.progress.pack(padx=10, pady=8)

        self.lbl_status = ttk.Label(frm_status, text="Ready.")
        self.lbl_status.pack(anchor="w", padx=10)

        self.txt_log = tk.Text(frm_status, height=8, width=92, state="disabled")
        self.txt_log.pack(padx=10, pady=6)

    # ── Folder / file pickers ──────────────────────────────────────────────

    def pick_repos_dir(self) -> None:
        """Open a folder chooser for the repos parent directory."""
        d = filedialog.askdirectory(title="Select the folder that contains the repo folders")
        if d:
            self.repos_dir.set(d)

    def pick_output_dir(self) -> None:
        """Open a folder chooser for the archive output directory."""
        d = filedialog.askdirectory(title="Select the output folder for the .7z archives")
        if d:
            self.output_dir.set(d)

    def pick_7z_path(self) -> None:
        """Open a file chooser for the 7-Zip executable (optional)."""
        f = filedialog.askopenfilename(
            title="Select 7z executable",
            filetypes=[("7-Zip executable", "7z.exe;7z;7za;7zr"), ("All files", "*.*")],
        )
        if f:
            self.sevenz_path.set(f)

    # ── Input validation ───────────────────────────────────────────────────

    def validate_inputs(self) -> tuple[Path, Path, str]:
        """
        Validate user-supplied folder paths and locate 7-Zip.

        Returns
        -------
        tuple[Path, Path, str]
            ``(repos_path, out_path, sevenzip_exe)``

        Raises
        ------
        ValueError
            If repos or output folder fields are empty.
        FileNotFoundError
            If the repos path is not a directory, or 7-Zip cannot be found.
        """
        repos_raw = self.repos_dir.get().strip()
        out_raw = self.output_dir.get().strip()

        if not repos_raw:
            raise ValueError("Please select the repos parent folder.")
        if not out_raw:
            raise ValueError("Please select an output folder.")

        repos_path = Path(repos_raw).resolve()
        out_path = Path(out_raw).resolve()

        if not repos_path.is_dir():
            raise FileNotFoundError(f"Repos parent folder is not a directory:\n{repos_path}")

        out_path.mkdir(parents=True, exist_ok=True)

        explicit = self.sevenz_path.get().strip() or None
        sevenzip = find_7z(explicit)
        return repos_path, out_path, sevenzip

    # ── Start / stop ───────────────────────────────────────────────────────

    def start(self) -> None:
        """Validate inputs and launch the background archiving thread."""
        try:
            repos_path, out_path, sevenzip = self.validate_inputs()
        except (ValueError, FileNotFoundError, OSError) as exc:
            messagebox.showerror("Input error", str(exc))
            return

        try:
            repos = list_repo_subfolders(repos_path)
        except (FileNotFoundError, NotADirectoryError) as exc:
            messagebox.showerror("Folder error", str(exc))
            return

        if not repos:
            messagebox.showinfo(
                "Nothing to archive",
                f"No subfolders found inside:\n{repos_path}",
            )
            return

        self._stop_requested = False
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.progress.configure(maximum=len(repos), value=0)
        self.lbl_status.config(text=f"Starting… {len(repos)} folder(s) to archive.")
        self.log(f"7-Zip: {sevenzip}")
        self.log(f"Source: {repos_path}")
        self.log(f"Output: {out_path}")
        self.log("")

        self.worker_thread = threading.Thread(
            target=self._run_archives,
            args=(repos, out_path, sevenzip),
            daemon=True,
        )
        self.worker_thread.start()
        self.after(200, self._poll_thread)

    def stop(self) -> None:
        """Request a graceful stop after the current archive finishes."""
        self._stop_requested = True
        self.lbl_status.config(text="Stop requested — finishing current archive…")
        self.log("Stop requested by user.")

    def _poll_thread(self) -> None:
        """Poll the worker thread and re-enable controls when it finishes."""
        if self.worker_thread and self.worker_thread.is_alive():
            self.after(200, self._poll_thread)
        else:
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            final = "Stopped by user." if self._stop_requested else "Done — all archives complete."
            self.lbl_status.config(text=final)
            self.log(f"\n{final}")

    # ── Worker ─────────────────────────────────────────────────────────────

    def _run_archives(self, repos: list[Path], out_path: Path, sevenzip: str) -> None:
        """Archive each repo folder sequentially (runs on a background thread)."""
        exclude_dirs = list(DEFAULT_EXCLUDE_DIRS)
        if self.exclude_git.get():
            exclude_dirs.append(".git")

        exclude_globs = list(DEFAULT_EXCLUDE_GLOBS)
        dict_size = self.dict_size.get().strip() or DEFAULT_DICT_SIZE
        threads = self.threads.get().strip() or DEFAULT_THREADS
        solid = bool(self.solid.get())

        for i, repo in enumerate(repos, start=1):
            if self._stop_requested:
                break

            archive_path = out_path / f"{repo.name}.7z"
            self._ui_set_status(f"[{i}/{len(repos)}] Archiving {repo.name}…")
            self._ui_log(f"==> {repo.name}  →  {archive_path.name}")

            try:
                cmd = build_7z_command(
                    sevenzip=sevenzip,
                    archive_path=archive_path,
                    repo_path=repo,
                    dict_size=dict_size,
                    threads=threads,
                    solid=solid,
                    exclude_dirs=exclude_dirs,
                    exclude_globs=exclude_globs,
                )
                returncode, stdout, stderr = run_archive(cmd)
            except (ValueError, FileNotFoundError, NotADirectoryError) as exc:
                self._ui_log(f"  SKIPPED — {exc}\n")
                self._ui_progress(i)
                continue
            except subprocess.TimeoutExpired:
                self._ui_log(
                    f"  ERROR — timed out after {SUBPROCESS_TIMEOUT}s. "
                    "Try reducing dictionary size or disabling solid mode.\n"
                )
                self._ui_progress(i)
                continue
            except PermissionError as exc:
                self._ui_log(f"  ERROR — {exc}\n")
                self._ui_progress(i)
                continue

            if returncode != 0:
                self._ui_log("  FAILED:")
                if stdout:
                    self._ui_log(f"  stdout: {stdout.strip()}")
                if stderr:
                    self._ui_log(f"  stderr: {stderr.strip()}")
                self._ui_log(f"  Exit code: {returncode}\n")
            else:
                size_mb = archive_path.stat().st_size / 1_048_576 if archive_path.exists() else 0
                self._ui_log(f"  OK  ({size_mb:.1f} MB)\n")

            self._ui_progress(i)

    # ── Thread-safe UI helpers ─────────────────────────────────────────────

    def log(self, msg: str) -> None:
        """Append *msg* to the log text widget (call from main thread only)."""
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def _ui_set_status(self, text: str) -> None:
        """Thread-safe status label update."""
        self.after(0, lambda: self.lbl_status.config(text=text))

    def _ui_progress(self, value: int) -> None:
        """Thread-safe progress bar update."""
        self.after(0, lambda: self.progress.configure(value=value))

    def _ui_log(self, msg: str) -> None:
        """Thread-safe log append."""
        self.after(0, lambda: self.log(msg))


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
