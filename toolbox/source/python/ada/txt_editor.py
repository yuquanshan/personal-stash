import curses
import curses.textpad

# a simple vim like editor
VIEW_STR = "[VIEW MODE]"
CMD_STR = "[CMD MODE]"
INSERT_STR = "[INSERT MODE]"
UNKNOWN_STR = "[UNKNOW STATE!!!]"
#
# class Textbox(curses.textpad.Textbox):
#     def do_command(self, ch):
#         if ch == 127:
#             super(curses.textpad.Textbox, self).do_command(4)
#         else:
#             super(curses.textpad.Textbox, self).do_command(ch)


class TxtEditor:
    def __init__(self, content):
        self.content_ = content
        ## 0 is view mode, 1 is cmd mode, 2 is insert mode
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing = True


    def _render_state(self, window):
        if self.state_ == 0:
            stt_str = VIEW_STR
        elif self.state_ == 1:
            stt_str = CMD_STR
        elif self.state_ == 2:
            stt_str = INSERT_STR
        else:
            stt_str = UNKNOWN_STR
        window.addstr(0, 0, stt_str + '\n' + self.cmd_buff_)


    def _render_content(self, window):
        window.addstr(0, 0, '\n'.join(self.content_))


    def _take_and_process_view(self, window):
        c = window.getch()
        if c == ord('i'):
            self.state_ = 2
        elif c == ord(':'):
            self.state_ = 1
            self.cmd_buff_ = ":"


    def _take_and_process_cmd(self, window):
        c = window.getch()
        if c >= 97 and c <= 122:
            self.cmd_buff_ = self.cmd_buff_ + chr(c)
        elif c == 10:
            if self.cmd_buff_ == ":q":
                self.stay_editing = False
        window.move(2, len(self.cmd_buff_))


    def _take_and_process_insert(self, window):
        c = window.getch()
        self.stay_editing = True
        pass


    def run(self):
        stdscr = curses.initscr()
        txtscr = stdscr.subwin(2, 0)
        txtscr.keypad(True)
        self.stay_editing = True
        self._render_state(stdscr)
        self._render_content(txtscr)
        stdscr.move(1, 0)
        txtscr.move(0, 0)
        while self.stay_editing:
            if self.state_ == 0:
                self._take_and_process_view(txtscr)
            elif self.state_ == 1:
                self._take_and_process_cmd(stdscr)
            elif self.state_ == 2:
                self._take_and_process_insert(txtscr)
            self._render_state(stdscr)
            self._render_content(txtscr)
        curses.endwin()
        return self.content_
