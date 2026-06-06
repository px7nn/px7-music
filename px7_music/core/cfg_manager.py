import json

import px7_music.config as config
from px7_music.utility import ANSI


_TUNABLE = {
    "DEFAULT_SEARCH_LIMIT": (int, "DEFAULT_SEARCH_LIMIT"),
    "DEFAULT_QUERY_POSTFIX": (str, "DEFAULT_QUERY_POSTFIX"),
    "COMPACT_THRESHOLD":  (int,   "COMPACT_THRESHOLD"),
}

_DEFAULTS = {k: getattr(config, k) for k in _TUNABLE}


# ── Persistence ───────────────────────────────────────────────────────────────

def _load_file() -> dict:
    if not config.PREF_FILE.exists():
        return {}
    try:
        with open(config.PREF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_file(data: dict) -> None:
    config.PREF_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.PREF_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _show_all() -> None:
    overrides = _load_file()
    print()
    for key in _TUNABLE:
        current = getattr(config, key)
        default = _DEFAULTS[key]
        changed = key in overrides
        print(
            f"{ANSI.BOLD}{key}{ANSI.RESET}"
            f"  =  {ANSI.GREEN}{current!r}{ANSI.RESET}"
            + (f"  {ANSI.DIM}(default: {default!r}){ANSI.RESET}" if changed else "")
        )
    print()


def _show_key(key: str) -> None:
    current = getattr(config, key)
    default = _DEFAULTS[key]
    overrides = _load_file()
    changed = key in overrides
    print(
        f"{ANSI.BOLD}{key}{ANSI.RESET}  =  {ANSI.GREEN}{current!r}{ANSI.RESET}"
        + (f"  {ANSI.DIM}(default: {default!r}){ANSI.RESET}" if changed else "")
    )


def _set_key(key: str, raw: str) -> None:
    expected_type, attr = _TUNABLE[key]
    raw = raw.strip()
    try:
        if expected_type is int:
            value = int(raw)
        elif expected_type is float:
            value = float(raw)
        else:
            value = raw.strip("\"'")
    except ValueError:
        print(f"{ANSI.YELLOW}Invalid value for {key}: expected {expected_type.__name__}{ANSI.RESET}")
        return

    setattr(config, attr, value)

    overrides = _load_file()
    overrides[key] = value
    _save_file(overrides)
    print(f"{ANSI.GREEN}{key}{ANSI.RESET}  =  {ANSI.BOLD}{value!r}{ANSI.RESET}  {ANSI.DIM}(saved){ANSI.RESET}")


def _reset_key(key: str) -> None:
    default = _DEFAULTS[key]
    attr = _TUNABLE[key][1]
    setattr(config, attr, default)

    overrides = _load_file()
    overrides.pop(key, None)
    _save_file(overrides)
    print(f"{ANSI.DIM}{key}{ANSI.RESET}  =  {ANSI.BOLD}{default!r}{ANSI.RESET}  {ANSI.DIM}(reset to default){ANSI.RESET}")


def _reset() -> None:
    if config.PREF_FILE.exists():
        config.PREF_FILE.unlink()
    for key, default in _DEFAULTS.items():
        attr = _TUNABLE[key][1]
        setattr(config, attr, default)
    print(f"{ANSI.DIM}Config reset to defaults.{ANSI.RESET}")


# ── Public API ───────────────────────────────────────────────────────────────

def apply_saved() -> None:
    overrides = _load_file()
    for key, value in overrides.items():
        if key in _TUNABLE:
            setattr(config, key, value)


def config_handler(args: list[str]) -> None:
    if not args:
        _show_all()
        return
    if args[0].strip().lower() == "reset":
        _reset()
        return

    key = args[0].strip().upper()
    if key not in _TUNABLE:
        print(
            f"{ANSI.YELLOW}Unknown config key: {args[0].strip()}\n"
            f"Valid keys: {', '.join(_TUNABLE)}{ANSI.RESET}"
        )
        return

    if len(args) == 1:
        _show_key(key)
        return

    value_raw = " ".join(args[1:]).strip()
    if value_raw == "*":
        _reset_key(key)
        return

    _set_key(key, value_raw)