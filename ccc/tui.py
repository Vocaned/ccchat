from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition, has_focus, to_filter, is_done
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import HSplit, ConditionalContainer
from prompt_toolkit.layout.processors import ConditionalProcessor, AppendAutoSuggestion, BeforeInput, PasswordProcessor, Processor
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.widgets import SearchToolbar, TextArea, Label
from prompt_toolkit.history import InMemoryHistory

import launcher
import cclexer
from consts import MOTD_TEXT, HELP_TEXT

CLIENT = None

class Data:
    username = ''
    cookie_jar = None
    server_list = []

class State:
    NONE = 0
    USERNAME = 1
    PASSWORD = 2
    WAITING = 3
    SERVERLIST = 4
    INGAME = 5

    state = NONE

def edit_input_processors(control: BufferControl, prompt: str = '>>> ', password = False):
    control.input_processors = [
        ConditionalProcessor(
            AppendAutoSuggestion(), has_focus(control.buffer) & ~is_done
        ),
        ConditionalProcessor(
            processor=PasswordProcessor(), filter=to_filter(password)
        ),
        BeforeInput(prompt, style="class:text-area.prompt"),
    ]

async def main():
    in_history = InMemoryHistory()
    lexer = cclexer.CCLexer()

    chat_out = TextArea(
        text=MOTD_TEXT,
        scrollbar=True,
        focusable=False,
        lexer=lexer
    )
    chat_in = TextArea(
        prompt='>>> ',
        height=1,
        style="bg:#000000 #ffffff",
        multiline=False,
        wrap_lines=False,
        history=in_history,
    )

    layout = Layout(HSplit(
        [
            chat_out,
            chat_in
        ]
    ), focused_element=chat_in)

    def append_out(text):
        new_text = chat_out.text + '\n' + text

        chat_out.buffer.document = Document(
            text=new_text, cursor_position=len(new_text)
        )

    async def accept():
        text = chat_in.buffer.text

        if State.state == State.USERNAME:
            Data.username = text
            State.state = State.PASSWORD
            append_out('Enter your password')
            edit_input_processors(chat_in.control, 'Password: ', True)

        elif State.state == State.PASSWORD:
            State.state = State.WAITING
            chat_in.buffer.document = Document() # Clear buffer immediately to not leak password
            edit_input_processors(chat_in.control)
            append_out('Logging in...')
            data = await launcher.login(Data.username, text)
            if data[1]: #err
                append_out('&4Could not log in!\n&c' + data[1] + '\n&fTry logging in again with &e/client login&f.')
                State.state = State.NONE
            else:
                Data.username = data[0][0]
                Data.cookie_jar = data[0][1]
                append_out('Getting server list\n')
                data = await launcher.serverlist(Data.cookie_jar)
                Data.server_list = data
                State.state = State.SERVERLIST
                for i,s in enumerate(data):
                    append_out(f'&8[&f{len(data)-i}&8]&f {s[0]}')
                append_out('\nEnter a server number to connect.')
                edit_input_processors(chat_in.control, 'Server: ')

        elif State.state == State.SERVERLIST:
            if not text.isnumeric(): # TODO: better check
                append_out(f'Invalid number "{text}"')
            else:
                edit_input_processors(chat_in.control)
                num = int(text)
                server = Data.server_list[len(Data.server_list)-num][1]
                append_out(str(server))
                State.state = State.INGAME


        elif text.startswith('/client '):
            args = text[8:].split()
            if args[0].lower() == 'help':
                append_out(HELP_TEXT)
            elif args[0].lower() == 'quit':
                application.exit()
            elif args[0].lower() == 'login':
                append_out('ClassiCube Login\nEnter your username')
                State.state = State.USERNAME
                edit_input_processors(chat_in.control, 'Username: ')

        else:
            append_out(text)

    chat_in.accept_handler
    chat_in.accept_handler = accept

    kb = KeyBindings()
    @kb.add("c-c")
    @kb.add("c-q")
    def _(event):
        event.app.exit()

    @kb.add('enter')
    async def _(event):
        await accept()
        chat_in.buffer.document = Document()

    application = Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=True,
        full_screen=True,
        enable_page_navigation_bindings=True,
    )

    await application.run_async()
