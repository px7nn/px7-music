import shlex
from px7_music.utility.utils import ANSI


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
        
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                print(f"{ANSI.RED}Error: {e}{ANSI.RESET}")
        else:
            print(f"{ANSI.YELLOW}Unknown command: {cmd}{ANSI.RESET}")


def break_args(args: list[str]):
    flags = {}
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
            except ValueError:
                raise ValueError(f"Invalid value for --{key}")

    return parsed