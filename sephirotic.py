#!/usr/bin/env python3
"""
Sephirotic Interface — Root-linked direct access to every project file.
Reads sephirotic-root.json and provides zero-relative-path resolution.

Usage:
    from sephirotic import root, sephira, resolve
    
    # List all files in a sephira
    sephira('KETER')  # -> [{"path": "sephirotic-root.json", ...}, ...]
    
    # Resolve a manifest path to absolute path
    resolve('server/main.py')  # -> /home/tehlappy/.../server/main.py
    
    # Direct read
    root.read('GDD.md')  # -> contents of GDD.md
    
    # Access ecosystem projects
    root.ecosystem('pub')  # -> /home/tehlappy/Desktop/AI/Pub
    
    # API interfaces
    root.api('server-api', 'health')  # -> {"method": "GET", "path": "/health"}
"""

import json
import os
from pathlib import Path
from typing import Any, List, Optional


_SELF = Path(__file__).resolve().parent
MANIFEST_PATH = _SELF / "sephirotic-root.json"


class SephiroticRoot:
    """Root manifest — every file indexed, directly resolvable."""
    
    def __init__(self, manifest_path: Path = MANIFEST_PATH):
        if not manifest_path.exists():
            raise FileNotFoundError(f"Sephirotic root manifest not found: {manifest_path}")
        self._data = json.loads(manifest_path.read_text())
        self._root = Path(self._data["root"]).resolve()
    
    @property
    def root(self) -> Path:
        return self._root
    
    @property
    def version(self) -> str:
        return self._data.get("version", "unknown")
    
    def sephira(self, name: str) -> List[dict]:
        """Get all files in a sephira by name (KETER, CHOKMAH, etc)."""
        name = name.upper()
        seph = self._data.get("sephira", {}).get(name)
        if not seph:
            raise KeyError(f"Unknown sephira: {name}. Known: {list(self._data.get('sephira', {}).keys())}")
        return seph.get("files", [])
    
    def all_files(self) -> List[dict]:
        """Every file across all sephirot."""
        files = []
        for seph_name, seph_data in self._data.get("sephira", {}).items():
            for f in seph_data.get("files", []):
                files.append({**f, "sephira": seph_name})
        return files
    
    def resolve(self, rel_path: str) -> Path:
        """Resolve a manifest-relative path to an absolute path."""
        return (self._root / rel_path).resolve()
    
    def read(self, rel_path: str) -> str:
        """Read a file by its manifest path."""
        abs_path = self.resolve(rel_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"File not found: {abs_path}")
        return abs_path.read_text()
    
    def exists(self, rel_path: str) -> bool:
        return self.resolve(rel_path).exists()
    
    def ecosystem(self, name: str) -> Optional[Path]:
        """Get path to an ecosystem project (pub, invite, abyssal-assets, evidence)."""
        entry = self._data.get("ecosystem", {}).get(name)
        if entry:
            return Path(entry["path"]).resolve()
        return None
    
    def api(self, interface: str, endpoint: str = None) -> Any:
        """Get API interface details."""
        iface = self._data.get("interfaces", {}).get(interface)
        if not iface:
            raise KeyError(f"Unknown interface: {interface}")
        if endpoint:
            ep = iface.get("endpoints", {}).get(endpoint)
            if not ep:
                raise KeyError(f"Unknown endpoint {endpoint} in interface {interface}")
            base = iface.get("base", "")
            return {
                **ep,
                "url": f"{base}{ep['path']}",
            }
        return iface
    
    def api_url(self, interface: str, endpoint: str) -> str:
        """Get full URL for an API endpoint."""
        result = self.api(interface, endpoint)
        return result["url"]
    
    def skills(self) -> List[dict]:
        """Get all deployed opencode skills."""
        return self._data.get("opencode-skills", {}).get("agents", [])
    
    def sephira_tree(self) -> dict:
        """Get the full sephirotic tree structure (names and descriptions)."""
        return {
            name: {
                "name": data["name"],
                "description": data["description"],
                "file_count": len(data.get("files", [])),
            }
            for name, data in self._data.get("sephira", {}).items()
        }
    
    def summary(self) -> str:
        """Print a summary of the manifest."""
        sep = self.sephira_tree()
        total_files = len(self.all_files())
        lines = [
            f"Sephirotic Root v{self.version}",
            f"Root: {self._root}",
            f"Total files indexed: {total_files}",
            f"Sephira: {len(sep)}/{len(self._data.get('sephira', {}))}",
            "",
            "Tree:",
        ]
        for name, info in sep.items():
            marker = "●" if info["file_count"] > 0 else "○"
            lines.append(f"  {marker} {name} ({info['name']}) — {info['file_count']} files")
        lines.append("")
        lines.append("Ecosystem:")
        for name, entry in self._data.get("ecosystem", {}).items():
            lines.append(f"  ● {name} — {entry['purpose']}")
        lines.append("")
        lines.append(f"Skills deployed: {len(self.skills())}/10")
        return "\n".join(lines)


root = SephiroticRoot()

def sephira(name: str) -> List[dict]:
    return root.sephira(name)

def resolve(rel_path: str) -> Path:
    return root.resolve(rel_path)


if __name__ == "__main__":
    print(root.summary())
    
    # CLI: resolve and read any file
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "resolve" and len(sys.argv) > 2:
            print(root.resolve(sys.argv[2]))
        elif cmd == "read" and len(sys.argv) > 2:
            print(root.read(sys.argv[2]))
        elif cmd == "sephira" and len(sys.argv) > 2:
            files = root.sephira(sys.argv[2])
            for f in files:
                print(f"  {f['path']} — {f['purpose']}")
        elif cmd == "api" and len(sys.argv) > 2:
            if len(sys.argv) > 3:
                print(json.dumps(root.api(sys.argv[2], sys.argv[3]), indent=2))
            else:
                print(json.dumps(root.api(sys.argv[2]), indent=2))
        elif cmd == "ecosystem":
            for name in root._data.get("ecosystem", {}):
                print(f"  {name}: {root.ecosystem(name)}")
