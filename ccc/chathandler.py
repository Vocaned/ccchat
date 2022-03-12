import asyncio

HELP_TEXT = """&cHelp text TODO"""

def handle_chat(text: str) -> str:
    if text.startswith('/client '):
        args = text.lstrip('/client ').split()
        if args[0] == 'help':
            return HELP_TEXT
        if args[0] == 'quit':
            asyncio.get_event_loop().stop()

    return None
