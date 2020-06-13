import sys
from datetime import timedelta
import srt
import ctypes

def get_text_from_file(filename):
    if not filename.endswith(".txt"):
        ctypes.windll.user32.MessageBoxW(0, "can only process .txt files not %s" % filename, "Text 2 subtitles", 1 + 0x30)
        return


    txt_file = open(r'C:\Users\butler\Desktop\FootprintWords.txt', 'rb')
    if txt_file == None:
        ctypes.windll.user32.MessageBoxW(0, "cannot open %s permission denied" % filename, "Text 2 subtitles", 1 + 0x30)
        return

    data = txt_file.read()
    txt_file.close()
    return data
    
def file_to_srt(filename):
    data = get_text_from_file(filename)
    if len(data) < 1:
        return
    
    srt_filename = filename[:-3] + 'srt'


    fancyopen=bytes([0xe2, 0x80, 0x9c])
    fancyclose=bytes([0xe2, 0x80, 0x9d])
    doublequote=0x22.to_bytes(1, 'little')

    data = data.replace(fancyopen, doublequote)
    data = data.replace(fancyclose, doublequote)

    text_data = data.decode(encoding='ascii', errors='ignore')
   
    lines = text_data.split('\n')

    time_now = timedelta()
    time_delta = timedelta(seconds=10)

    subtitles = []
    buffer = ""
    subtitle_number = 1
    for line in lines:
        line = line.strip()

        if line.endswith('\\'):
             # explicit line continuation
            buffer += line[:-1] + '\n'
            continue
        else:
            # last line of this subtitle
            text = srt.make_legal_content(buffer + line)
            buffer = ''
            subtitles.append(srt.Subtitle(subtitle_number, time_now, time_now+time_delta,text))
            time_now += time_delta
            subtitle_number += 1

    if len(buffer) > 0:
        text = srt.make_legal_content(buffer)
        subtitles.append(srt.Subtitle(subtitle_number, time_now, time_now+time_delta,text))

    srt_file = open(srt_filename, 'w')
    if srt_file == None:
        ctypes.windll.user32.MessageBoxW(0, "cannot write %s permission denied" % srt_filename, "Text 2 subtitles", 1 + 0x30)
        return
    print(srt.compose(subtitles), file=srt_file)
    srt_file.close()

message = \
'Drag text file onto executable to create SRT file.\n\
Each line of text file becomes a distinct caption.\n\
Lines ending with "\\" character" will result in a\n\
multi-line caption.  Captions will each be 10 seconds'
def usage():
        ctypes.windll.user32.MessageBoxW(0, message, "Text 2 subtitles", 1)

        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    for f in sys.argv[1:]:
        file_to_srt(f)