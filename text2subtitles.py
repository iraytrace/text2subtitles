import sys
from datetime import timedelta
import srt
import ctypes

max_line_length_default = 61
max_caption_lines_default = 2
seconds_default = 10

message = \
'Drag text file onto executable to create SRT file.\n\
Lines of text will be word-concatenated to create captions\n\
Blank lines force caption completion\n\
Command line options:\n\
    -max_line_length=num_char (default=61)\n\
    -max_caption_lines=num_lines (default=2)\n\
    -seconds=caption_display_time (default=10)\n\
        '

class Captioner:
    def __init__(self):
        global max_line_length_default
        global max_caption_lines_default
        global seconds_default
        self.subtitles = []
        self.caption = []
        self.buffer = ''
        self.srt = None
        self.max_line_length = max_line_length_default
        self.max_caption_lines = max_caption_lines_default
        self.seconds = seconds_default
        self.time_now = timedelta()
        print(self.seconds)
        self.time_delta = timedelta(seconds=self.seconds)

    def set_option(self, txt):
        tokens =txt.split('=')
        if len(tokens) != 2:
            print('cannot set %s ' % txt)
            return
        else:
            if tokens[0] in ['max_line_length', 'max_caption_lines', 'seconds']:
                setattr(self, tokens[0], int(tokens[1]))
                if tokens[0] == 'seconds':
                    self.time_delta = timedelta(seconds=self.seconds)

    def finish_curent_buffer_and_caption(self):
        if len(self.buffer) > 0:
            self.add_buffer_to_caption()
        if len(self.caption) > 0:
            self.generate_new_subtitle()
        

    def write_srt(self, srt_filename):
        srt_file = open(srt_filename, 'w')
        if srt_file == None:
            ctypes.windll.user32.MessageBoxW(0, "cannot write %s permission denied" % srt_filename, "Text 2 subtitles", 1 + 0x30)
            return
        print(srt.compose(self.subtitles), file=srt_file)
        srt_file.close()


    def get_text_from_file(self, filename):
        if not filename.endswith(".txt"):
            ctypes.windll.user32.MessageBoxW(0, "can only process .txt files not %s" % filename, "Text 2 subtitles", 1 + 0x30)
            return
    
        txt_file = open(filename, 'rb')
        if txt_file == None:
            ctypes.windll.user32.MessageBoxW(0, "cannot open %s permission denied" % filename, "Text 2 subtitles", 1 + 0x30)
            return
    
        data = txt_file.read()
        txt_file.close()
        return data

    def convert_unicode_to_lines(self, data):
        
        # replace fancy unicode quotes with regular double-quote
        fancyopen=bytes([0xe2, 0x80, 0x9c])
        fancyclose=bytes([0xe2, 0x80, 0x9d])
        doublequote=0x22.to_bytes(1, 'little')
    
        data = data.replace(fancyopen, doublequote)
        data = data.replace(fancyclose, doublequote)
    
        text_data = data.decode(encoding='ascii', errors='ignore')
       
        # split text into lines
        return text_data.split('\n')

    def generate_new_subtitle(self ):
        subtitle_text = '\n'.join(self.caption)
        
        subtitle_text = srt.make_legal_content(subtitle_text)

        start = self.time_now
        stop = start + self.time_delta
        self.subtitles.append(
            srt.Subtitle(len(self.subtitles)+1, 
                         start, 
                         stop,
                         subtitle_text)
            )

        self.time_now = stop
        self.caption.clear()

    def add_buffer_to_caption(self):
        self.caption.append(self.buffer)
        if len(self.caption) >= self.max_caption_lines:
            self.generate_new_subtitle()
        self.buffer = ''


    def parcel_words_into_buffer(self, line):
        words = line.split()
        for w in words:
            if len(self.buffer) + len(w) + 1 < self.max_line_length:
                if len(self.buffer) == 0:
                    self.buffer = w
                else:
                    self.buffer += ' ' + w
            else:
                self.add_buffer_to_caption()
                self.buffer = w

    def add_line_to_caption_buffer(self, line):
        if len(self.buffer)+ len(line) + 1 < self.max_line_length:
            self.buffer += ' ' + line
            self.buffer = self.buffer.strip()
        else:
            self.parcel_words_into_buffer(line)
        if len(self.buffer) > (self.max_line_length // 2) + 1:
            self.add_buffer_to_caption()


    def add_line_to_current_caption(self, line):
        if len(line) == 0:
            self.finish_curent_buffer_and_caption()
        self.add_line_to_caption_buffer(line)


    def file_to_srt(self, filename):
        print(filename)
        data = self.get_text_from_file(filename)
        if len(data) < 1:
            return

        lines = self.convert_unicode_to_lines(data)
        
        for l in lines:
            line = l.strip()
            self.add_line_to_current_caption(line)
        
        self.finish_curent_buffer_and_caption()
        
        srt_filename = filename[:-3] + 'srt'
        self.write_srt(srt_filename)
        



def usage():
        ctypes.windll.user32.MessageBoxW(0, message, "Text 2 subtitles", 1)

        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    captioner = Captioner()
    
    for f in sys.argv[1:]:
        if f.startswith('-'):
            captioner.set_option(f[1:])
        else:
            captioner.file_to_srt(f)