"""
Decrypt .env.enc via SOPS ke memory.
Tidak pernah menulis plaintext ke disk.
Auto-cari keys.age di folder backend/.
"""

import os
import subprocess
from pathlib import Path


def load_sops_env():
    """Decrypt SOPS file → os.environ. Coba .env.enc dulu, fallback ke .env."""
    base = Path(__file__).parent.parent  # backend/
    candidates = [base / ".env.enc", base / ".env"]

    env_file = None
    for f in candidates:
        if f.exists():
            env_file = f
            break

    if env_file is None:
        raise RuntimeError(
            "No .env.enc found. Create with: sops edit .env"
        )

    key_file = base / "keys.age"
    env = os.environ.copy()

    # Production (Coolify): SOPS_AGE_KEY set via env var — no file needed
    if "SOPS_AGE_KEY" in env:
        pass  # sops auto-detects this env var
    # Dev: use keys.age file
    elif key_file.exists():
        env["SOPS_AGE_KEY_FILE"] = str(key_file)
    else:
        raise RuntimeError(
            "No SOPS key found. Set SOPS_AGE_KEY env var (production) or create keys.age (dev)."
        )

    result = subprocess.run(
        ["sops", "-d", str(env_file)],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"SOPS decrypt gagal: {result.stderr.strip()}")

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value
