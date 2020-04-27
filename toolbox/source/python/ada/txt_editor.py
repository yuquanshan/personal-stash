import copy
import curses
import curses.textpad

VIEW_STR = "[VIEW MODE]"
CMD_STR = "[CMD MODE]"
INSERT_STR = "[INSERT MODE]"
UNKNOWN_STR = "[UNKNOW STATE!!!]"

MOVE_KEYS = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
BORDER_LINES = 2


class Line:
    def __init__(self, content_pair, width):
        self.content_ = content_pair[0]
        self.ineditable_content_ = content_pair[1]
        self.width_ = width


    def get_content(self):
        return copy.copy(self.content_)


    def get_ineditable_content(self):
        return copy.copy(self.ineditable_content_)


    def get_breaks(self):
        if len(self.content_) == 0 or len(self.content_) % self.width_ > 0:
            return len(self.content_) / self.width_ + 1
        else:
            return len(self.content_) / self.width_


    def get_corrected_yx(self, i):
        if self.width_ > 0:
            return [i / self.width_, i % self.width_]
        else:
            return [0, 0]


    def set_width(self, width):
        self.width_ = width


    def content_len(self):
        return len(self.content_)


    def ineditable_content_len(self):
        return len(self.ineditable_content_)


    def total_len(self):
        return self.content_len() + self.ineditable_content_len()


    def to_formatted(self):
        working_content = []
        content = self.ineditable_content_ + self.content_
        acc_size = -1
        total_size = len(content)
        while acc_size < total_size:
            acc_size = max(0, acc_size)
            stretch = min(self.width_, total_size - acc_size)
            working_content.append(content[acc_size: acc_size + stretch])
            acc_size = min(total_size, acc_size + self.width_)
        return '\n'.join(working_content)


    def to_string(self):
        return self.ineditable_content_ + self.content_


    # del a char in front of n th char
    def delete(self, n):
        i = n - len(self.ineditable_content_)
        if i > 0 and i <= self.content_len():
            self.content_ = self.content_[0:i - 1] + self.content_[i:]
            return True
        return False


    # insert a char in front of n th char
    def insert(self, n, c):
        i = n - len(self.ineditable_content_)
        if i <= self.total_len():
            self.content_ = self.content_[0:i] + c + self.content_[i:]
            return True
        return False


class LinesManager:
    def __init__(self, contents, width):
        self.width_ = width
        self.lines_ = [Line(c, width) for c in contents]
        # (logical) cursor position
        if len(self.lines_) > 0:
            self.cur_yx_ = [0, self.lines_[0].ineditable_content_len()]
        else:
            self.cur_yx_ = [0, 0]


    def del_line(self, i):
        if i < len(self.lines_):
            del self.lines_[i]


    def to_corrected_yx(self):
        acc_lines = 0
        for i in range(0, self.cur_yx_[0]):
            acc_lines = acc_lines + self.lines_[i].get_breaks()
        yx = self.lines_[self.cur_yx_[0]].get_corrected_yx(self.cur_yx_[1])
        yx[0] = yx[0] + acc_lines
        return yx


    def move_up(self):
        if self.cur_yx_[0] > 0:
            self.cur_yx_[0] = self.cur_yx_[0] - 1
            self.cur_yx_[1] = max(self.lines_[self.cur_yx_[0]].ineditable_content_len(), min(self.cur_yx_[1], self.lines_[self.cur_yx_[0]].total_len()))


    def move_down(self):
        if self.cur_yx_[0] < len(self.lines_) - 1:
            self.cur_yx_[0] = self.cur_yx_[0] + 1
            self.cur_yx_[1] = max(self.lines_[self.cur_yx_[0]].ineditable_content_len(), min(self.cur_yx_[1], self.lines_[self.cur_yx_[0]].total_len()))


    def move_left(self):
        if self.cur_yx_[1] > self.lines_[self.cur_yx_[0]].ineditable_content_len():
            self.cur_yx_[1] = self.cur_yx_[1] - 1


    def move_right(self):
        if self.cur_yx_[1] < self.lines_[self.cur_yx_[0]].total_len():
            self.cur_yx_[1] = self.cur_yx_[1] + 1


    def delete(self):
        if self.cur_yx_[0] < len(self.lines_):
            if self.lines_[self.cur_yx_[0]].delete(self.cur_yx_[1]):
                self.move_left()


    def insert(self, c):
        if self.cur_yx_[0] < len(self.lines_):
            if self.lines_[self.cur_yx_[0]].insert(self.cur_yx_[1], c):
                self.move_right()


    def to_formatted(self):
        ctt = [l.to_formatted() for l in self.lines_]
        return '\n'.join(ctt)


    def yeild_contents(self):
        return [[l.get_content() for l in self.lines_], [l.get_ineditable_content() for l in self.lines_]]


# a simple vim like editor
# Each line contains two parts: 1. non-editable content and editable content;
# doesn't support line deletion
class LineFixedTxtEditor:
    def __init__(self, width, content, ineditable_content = None):
        assert width > 0
        self.content_ = content
        self.width_ = width
        if len(self.content_) == 0:
            self.content_.append('')
        if not ineditable_content or len(content) == 0:
            self.ineditable_content_ = ['' for x in self.content_]
        else:
            assert len(content) == len(ineditable_content)
            self.ineditable_content_ = ineditable_content
        self.lines_manager = LinesManager(zip(self.content_, self.ineditable_content_), self.width_)
        ## 0 is view mode, 1 is cmd mode, 2 is insert mode
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing_ = True
        self.dump_backup_ = False
        # cursor pos
        self.yx_ = self.lines_manager.to_corrected_yx()
        self.yx_[0] = self.yx_[0] + BORDER_LINES


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
        window.addstr(BORDER_LINES, 0, self.lines_manager.to_formatted())


    def _render(self, window):
        self._render_state(window)
        self._render_content(window)


    def _take_and_process_view(self, window):
        c = window.getch()
        if c == ord('i'):
            self.state_ = 2
        elif c == ord(':'):
            self.state_ = 1
            self.cmd_buff_ = ":"
            self.yx_ = [BORDER_LINES - 1, len(self.cmd_buff_)]
        elif c in MOVE_KEYS:
            self._move_cursor(c)


    def _take_and_process_cmd(self, window):
        c = window.getch()
        if c >= 97 and c <= 122:
            self.cmd_buff_ = self.cmd_buff_ + chr(c)
            self.yx_ = [BORDER_LINES - 1, len(self.cmd_buff_)]
        elif c == 10: # ENTER
            if self.cmd_buff_ == ":wq":
                self.stay_editing_ = False
                self.cmd_buff_ = ""
            if self.cmd_buff_ == ":w":
                window.clear()
                self._reset_state()
                yx = self.lines_manager.to_corrected_yx()
                yx[0] = yx[0] + BORDER_LINES
                self.yx_ = yx
            elif self.cmd_buff_ == ":q":
                self.stay_editing_ = False
                self.cmd_buff_ = ""
                self.dump_backup_ = True
        elif c == 27: # ESC
            window.clear()
            self._reset_state()
        elif c == 127:
            window.clear()
            self.cmd_buff_ = self.cmd_buff_[:-1]
            self.yx_ = [BORDER_LINES - 1, len(self.cmd_buff_)]


    def _take_and_process_insert(self, window):
        c = window.getch()
        if c == 27: # ESC
            window.clear()
            self._reset_state()
        elif c in MOVE_KEYS:
            self._move_cursor(c)
        elif c == 127: # delete
            # we delete char with idx lc[1] - 1 of the line
            self.lines_manager.delete()
            yx = self.lines_manager.to_corrected_yx()
            yx[0] = yx[0] + BORDER_LINES
            self.yx_ = yx
            window.clear()
        elif c >= 32 and c <= 126:
            self.lines_manager.insert(chr(c))
            yx = self.lines_manager.to_corrected_yx()
            yx[0] = yx[0] + BORDER_LINES
            self.yx_ = yx
            window.clear()


    def _reset_state(self):
        self.state_ = 0
        self.cmd_buff_ = ""
        self.stay_editing_ = True


    def _move_cursor(self, move):
        assert move in MOVE_KEYS, "UNKNOWN MOVE KEYS"
        if move == MOVE_KEYS[0]:
            self.lines_manager.move_up()
            yx = self.lines_manager.to_corrected_yx()
            yx[0] = yx[0] + BORDER_LINES
            self.yx_ = yx
        elif move == MOVE_KEYS[1]:
            self.lines_manager.move_down()
            yx = self.lines_manager.to_corrected_yx()
            yx[0] = yx[0] + BORDER_LINES
            self.yx_ = yx
        elif move == MOVE_KEYS[2]:
            self.lines_manager.move_left()
            yx = self.lines_manager.to_corrected_yx()
            yx[0] = yx[0] + BORDER_LINES
            self.yx_ = yx
        elif move == MOVE_KEYS[3]:
            self.lines_manager.move_right()
            yx = self.lines_manager.to_corrected_yx()
            yx[0] = yx[0] + BORDER_LINES
            self.yx_ = yx


    def run(self):
        self._reset_state()
        scr = curses.initscr()
        curses.noecho()
        scr.keypad(True)
        scr.clearok(True)
        self._render(scr)
        while self.stay_editing_:
            scr.move(*self.yx_)
            if self.state_ == 0:
                self._take_and_process_view(scr)
            elif self.state_ == 1:
                self._take_and_process_cmd(scr)
            elif self.state_ == 2:
                self._take_and_process_insert(scr)
            self._render(scr)
        scr.clear()
        curses.endwin()
        self._reset_state()
        if not self.dump_backup_:
            return self.lines_manager.yeild_contents()
        return [self.content_, self.ineditable_content_]
