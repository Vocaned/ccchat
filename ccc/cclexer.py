from typing import Callable, Dict

from prompt_toolkit.lexers import Lexer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.base import StyleAndTextTuples


class CCLexer(Lexer):
    """
    Lexer for turning Classic color codes into prompt_toolkit styles
    """

    colors = {
        '0': 'fg:#000000',
        '1': 'fg:#0000AA',
        '2': 'fg:#00AA00',
        '3': 'fg:#00AAAA',
        '4': 'fg:#AA0000',
        '5': 'fg:#AA00AA',
        '6': 'fg:#FFAA00',
        '7': 'fg:#AAAAAA',
        '8': 'fg:#555555',
        '9': 'fg:#5555FF',
        'a': 'fg:#55FF55',
        'b': 'fg:#55FFFF',
        'c': 'fg:#FF5555',
        'd': 'fg:#FF55FF',
        'e': 'fg:#FFFF55',
        'f': 'fg:#FFFFFF'
    }

    def __init__(self, custom_colors: Dict[str, str] = None) -> None:
        if custom_colors:
            self.colors |= custom_colors # Merge dicts

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        lines = document.lines

        def get_line(lineno: int) -> StyleAndTextTuples:
            "Return the tokens for the given line."
            if lineno > len(lines):
                return []

            styles = [[self.colors['f'],'']]
            line = lines[lineno]

            for i, c in enumerate(line):
                if line[i-1] == '&' and c in self.colors:
                    styles[len(styles)-1][1] = styles[len(styles)-1][1][:-1] # Remove last & from last style
                    styles.append(['',''])
                    styles[len(styles)-1][0] = self.colors[c]
                else:
                    styles[len(styles)-1][1] += c

            return styles

        return get_line
