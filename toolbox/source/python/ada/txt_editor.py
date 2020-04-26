import copy
import curses
import curses.textpad

# a simple vim like editor
VIEW_STR = "[VIEW MODE]"
CMD_STR = "[CMD MODE]"
INSERT_STR = "[INSERT MODE]"
UNKNOWN_STR = "[UNKNOW STATE!!!]"

MOVE_KEYS = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
BORDER_LINES = 2

# class Textbox(curses.textpad.Textbox):
#     def do_command(self, ch):
#         if ch == 127:
#             super(curses.textpad.Textbox, self).do_command(4)
#         else:
#             super(curses.textpad.Textbox, self).do_command(ch)


# heler function to get the code of key
def keyLookup():
    stdscr = curses.initscr()
    stdscr.keypad(True)
    ch = stdscr.getkey()
    curses.endwin()
    print(ch)


class TxtEditor:
    def __init__(self, content):
        self.content_ = content
        if len(self.content_) == 0:
            self.content_.append('')
        ## 0 is view mode, 1 is cmd mode, 2 is insert mode
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing_ = True
        # cursor pos
        self.yx_ = [BORDER_LINES, 0]


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
        yx = curses.getsyx()
        window.addstr(BORDER_LINES, 0, '\n'.join(self.content_))


    def _take_and_process_view(self, window):
        c = window.getch()
        if c == ord('i'):
            self.state_ = 2
            self.yx_ = [BORDER_LINES, 0]
        elif c == ord(':'):
            self.state_ = 1
            self.cmd_buff_ = ":"
            self.yx_ = [BORDER_LINES - 1, len(self.cmd_buff_)]
        elif c in MOVE_KEYS:
            self._move_cursor(c)


    def _take_and_process_cmd(self, window):
        # window.move(BORDER_LINES - 1, len(self.cmd_buff_))
        c = window.getch()
        if c >= 97 and c <= 122:
            self.cmd_buff_ = self.cmd_buff_ + chr(c)
            self.yx_ = [BORDER_LINES - 1, len(self.cmd_buff_)]
        elif c == 10: # ENTER
            if self.cmd_buff_ == ":q":
                self.stay_editing_ = False
                self.cmd_buff_ = ""
        elif c == 27: # ESC
            window.clear()
            self._reset_state()


    def _take_and_process_insert(self, window):
        c = window.getch()
        lc = copy.copy(self.yx_)
        lc[0] = lc[0] - BORDER_LINES
        if c == 27: # ESC
            window.clear()
            self._reset_state()
        elif c in MOVE_KEYS:
            self._move_cursor(c)
        elif c == 127:
            # we delete char with idx lc[1] - 1 of the line
            if lc[1] - 1 >= 0:
                self.content_[lc[0]] = self.content_[lc[0]][:lc[1] - 1] + self.content_[lc[0]][lc[1]:]
            self._move_cursor(curses.KEY_LEFT)
        elif c >= 32 and c <= 126:
            self.content_[lc[0]] = self.content_[lc[0]][:lc[1]] + chr(c) + self.content_[lc[0]][lc[1]:]
            self._move_cursor(curses.KEY_RIGHT)


    def _reset_state(self):
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing_ = True
        self.yx_ = [BORDER_LINES, 0]


    def _move_cursor(self, move):
        assert move in MOVE_KEYS, "UNKNOWN MOVE KEYS"
        if move == MOVE_KEYS[0]:
            self.yx_[0] = max(BORDER_LINES, self.yx_[0] - 1)
            self.yx_[1] = min(len(self.content_[self.yx_[0] - BORDER_LINES]), self.yx_[1])
        elif move == MOVE_KEYS[1]:
            self.yx_[0] = min(BORDER_LINES + len(self.content_) - 1,  self.yx_[0] + 1)
            self.yx_[1] = min(len(self.content_[self.yx_[0] - BORDER_LINES]), self.yx_[1])
        elif move == MOVE_KEYS[2]:
            self.yx_[1] = max(0, self.yx_[1] - 1)
        elif move == MOVE_KEYS[3]:
            self.yx_[1] = min(len(self.content_[self.yx_[0] - BORDER_LINES]), self.yx_[1] + 1)


    def run(self):
        self._reset_state()
        scr = curses.initscr()
        curses.noecho()
        scr.keypad(True)
        scr.clearok(True)
        self._render_state(scr)
        self._render_content(scr)
        while self.stay_editing_:
            scr.move(*self.yx_)
            if self.state_ == 0:
                self._take_and_process_view(scr)
            elif self.state_ == 1:
                self._take_and_process_cmd(scr)
            elif self.state_ == 2:
                self._take_and_process_insert(scr)
            self._render_state(scr)
            self._render_content(scr)
        scr.clear()
        curses.endwin()
        self._reset_state()
        return self.content_
