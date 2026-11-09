"""Install only the rstack entry point; never replace a foreign path."""
from pathlib import Path

from .catalog import SKILL_DIR


def change_links(targets, apply=False, remove=False, source=SKILL_DIR):
    source = Path(source).resolve(strict=True)
    if not (source / "SKILL.md").is_file():
        raise ValueError("installation source has no SKILL.md")
    actions = []
    seen = set()
    for target in targets:
        parent = Path(target).expanduser().absolute()
        dest = parent / "rstack"
        if dest in seen:
            continue
        seen.add(dest)
        exists = dest.exists() or dest.is_symlink()
        owned = dest.is_symlink() and dest.resolve() == source
        if exists and not owned:
            raise ValueError(f"refusing foreign path: {dest}")
        action = ("remove" if owned else "absent") if remove else ("unchanged" if owned else "create")
        actions.append({"path": str(dest), "action": action, "source": str(source)})
    if apply:
        created = []
        try:
            for item in actions:
                dest = Path(item["path"])
                if item["action"] == "create":
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.symlink_to(source, target_is_directory=True)
                    created.append(dest)
                elif item["action"] == "remove":
                    dest.unlink()
        except OSError:
            for dest in created:
                if dest.is_symlink() and dest.resolve() == source:
                    dest.unlink()
            raise
    return {"applied": apply, "actions": actions}
