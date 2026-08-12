import shlex

from px7_music.utility import ANSI


class CommandParser:
    def __init__(self):
        self.commands = {} # dict[str, function]
    
    def register(self, name: str, handler): # handler: function
        self.commands[name] = handler
    
    def parse(self, raw_input: str):
        try:
            parts = shlex.split(raw_input)
        except ValueError:
            print("Invalid input format.")
            return

        if not parts:
            return

        # ── Pipe operator:  <source> [args] -> 'playlist name' ───────────────
        if "->" in parts:
            cmd_candidate = parts[0].lower() if parts else ""
            is_pl_rename = cmd_candidate == "pl" and len(parts) > 1 and parts[1].lower() == "rename"

            if not is_pl_rename:
                arrow_idx = parts.index("->")

                source_cmd  = parts[0].lower() if parts else ""
                source_args = parts[1:arrow_idx]
                dest_parts  = parts[arrow_idx + 1:]

                playlist_name = " ".join(dest_parts).strip()

                if not source_cmd:
                    print(f"{ANSI.YELLOW}Usage: <source> -> <playlist name>{ANSI.RESET}")
                    return

                if not playlist_name:
                    print(f"{ANSI.YELLOW}Missing playlist name after ->{ANSI.RESET}")
                    return

                from px7_music.core.pipe import handle_pipe
                handle_pipe(source_cmd, source_args, playlist_name)
                return

        # ── Normal command dispatch ───────────────────────────────────────────
        cmd  = parts[0].lower()
        args = parts[1:]

        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                print(f"{ANSI.RED}Error: {e}{ANSI.RESET}")
        else:
            print(f"{ANSI.YELLOW}Unknown command: {cmd}{ANSI.RESET}")


def break_args(args: list[str]):
    flags       = {}
    query_parts = []

    for part in args:
        if part.startswith("--"):
            if "=" in part:
                key, value = part[2:].split("=", 1)
                flags[key] = value
            else:
                flags[part[2:]] = True
        else:
            query_parts.append(part)

    query = " ".join(query_parts) if query_parts else None
    return query, flags


def parse_flags(flags: dict, schema: dict):
    parsed = {}

    for key, value in flags.items():
        if key not in schema:
            raise ValueError(f"Unknown flag: --{key}")

        expected_type = schema[key]

        if expected_type is bool:
            if value is not True:
                raise ValueError(f"--{key} does not take a value")
            parsed[key] = True
        else:
            if value is True:
                raise ValueError(f"--{key} requires a value")
            try:
                parsed[key] = expected_type(value)
            except (ValueError,  TypeError):
                raise ValueError(f"Invalid value for --{key}")

    return parsed


def extract_keyword(args: list[str], skip: int = 0) -> tuple[str | None, list[str]]:
    # Pulls a '/keyword phrase' out of an argument list, wherever it appears first
    for i in range(skip, len(args)):
        tok = args[i]
        if tok.startswith("/") and len(tok) > 1:
            words = [tok[1:]]
            rem   = list(args[:i])
            for later in args[i+1:]:
                if later.startswith("--"):
                    rem.append(later)
                else:
                    words.append(later)
            return (" ".join(words).strip() or None, rem)
    return None, args
