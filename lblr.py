#!/usr/bin/env python
import sys
import json
import codecs
import argparse

if int(sys.version[2]) < 3:
    reload(sys)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stdin = codecs.getreader('utf-8')(sys.stdin)

try:
    import tty, termios
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        # FIXME what to do on other platforms?
        # Just give up here.
        raise ImportError('getch not available')
    else:
        getch = msvcrt.getch
else:
    def getch():
        """getch() -> key character

        Read a single keypress from stdin and return the resulting character. 
        Nothing is echoed to the console. This call will block if a keypress 
        is not already available, but will not wait for Enter to be pressed. 

        If the pressed key was a modifier key, nothing will be detected; if
        it were a special function key, it may return the first character of
        of an escape sequence, leaving additional characters in the buffer.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def getseqch(n=3, reserved=['q']):
        c = getch()
        if c not in reserved:
            for i in range(n-1):
                c = getch()
        return c

class TweetLabeler:
    def __init__(self,
            json_input = True,
            delimiter = ',',
            left_arrow = 0,
            right_arrow = 1, 
            history_size = 10):
        self.json_input = json_input
        self.history_size = history_size
        self.history = []
        self.last_rated = ' '
        self.left_arrow = left_arrow
        self.right_arrow = right_arrow
        self.output_sink = []

    def setup_file_io(self,input_file,output_file):
        if self.json_input:
            self.input_source = [json.loads(item.strip()) for item in input_file]
        else:
            self.input_source = [item.strip() for item in input_file]
        self.output_sink = output_file

    def write_output(self,popped_item):
        if self.json_input:
            tmp = json.dumps(popped_item)
        else:
            tmp = popped_item
        try:
            self.output_sink.write(tmp + '\n') 
        except AttributeError:
            self.output_sink.append(popped_item)


    def label_tweet(self,row_cnt,row):
        char, value = '',''
        if len(self.history) > self.history_size:
            # remove the oldest record
            self.write_output(self.history.pop(0))
        # put in the dummy value
        if self.json_input:
            row["LBLR_label"] = value
        else:
            row += "%s%s"%(self.delimiter, value) 
        self.history.append(row)
        # looking at the last record in the history
        idx = len(self.history) - 1
        get_next_rec = False
        while not get_next_rec:
            print(u"[%s%2d] (%4d):"%(
                    self.last_rated
                    , idx-len(self.history)+1
                    , row_cnt-len(self.history)+idx+1), self.history[idx])
            char = getseqch()
            if char == 'q':
                # if you quit, the last item in history wasn't rated
                self.history.pop(-1)
                break
            if char == 'A':
                # up
                if idx > 0:
                    idx -= 1
                self.last_rated = ' '
                continue
            elif char == 'B':
                # down
                if idx < len(self.history)-1:
                    idx += 1
                self.last_rated = ' '
                continue
            elif char == 'C':
                # right
                value = self.right_arrow
            elif char == 'D':
                                                                          # left
                value = self.left_arrow
            # value set, overwrite existing
            if value != '':
                self.last_rated = '*'
                if self.json_input:
                    self.history[idx]["LBLR_label"] = value
                else:
                    tmp = self.history[idx].split(self.delimiter)
                    tmp[-1] = "%s"%value
                    self.history[idx] = self.delimiter.join(tmp)
            if idx == len(self.history) - 1:
                # no navigation and last record labeled, so move on
                get_next_rec = True
        if char == 'q':
            sys.stderr.write("Quitting without labeling all records\n")
            return False
        else:
            return True

    def label_tweets(self):

        for item_cnt, item in enumerate(self.input_source):
            
            if not self.label_tweet(item_cnt,item):
                break

        # if it is still in the the history, it hasn't been written yet
        [self.write_output(x) for x in self.history ]
        return self.output_sink

##########

if __name__ == '__main__':

    WIDTH = 80
    docstr = '*'*WIDTH + """

    Welcome to the minimalist lblr!  This application takes rows of
    content in JSON or csv form, presents each line individually, and
    allows a user to quickly label each row with 1 of two values.

    The history stack contains the last few values rated. You can
    navigate to these records and re-score them as necessary.

    Navigation:

                last record
                     ^
                     | 
                     | 
    left value  <---   -->  right value
                     |
                     |
                     v
             skip to next record


    Prefix is [* #](#) where * appears if last record viewed was scored.
    The first # is the history stack index. The second number is the row 
    number being processed.

    Use q to quit.

    """ + '*'*WIDTH

    descr = "Labeler is a simple command line record labeling tool."

    def args():
        cmd_args = argparse.ArgumentParser(description=descr)
        cmd_args.add_argument("-r", "--right_arrow", dest="right_arrow", 
            default=1, 
            help="Value to assign when right arrow --> key is pressed")
        cmd_args.add_argument("-d", "--delimiter", dest="delimiter", 
            default=",", 
            help="Delimiter of output")
        cmd_args.add_argument("-l", "--left_arrow", dest="left_arrow", 
            default=0, 
            help="Value to assign when left arrow <-- key is pressed")
        cmd_args.add_argument("-j", "--json", dest="json_input", 
            action = "store_true",
            default=False, 
            help="Input is JSON. This will add \"LBLR_label\" to the root.")
        cmd_args.add_argument("-o", "--ofilename", dest="out_file_name", 
            default= None, 
            help="Output file name. Will be created from input file name if omitted.")
        cmd_args.add_argument("-i", "--ifilename", dest="in_file_name", 
            default= None, 
            help="Input file name. Required.")
        cmd_args.add_argument("-m", "--manual", 
            dest="manual", 
            action = "store_true",
            default=False, 
            help="View the very simple manual")
        return cmd_args

    ##########

    options = args().parse_args()

    if options.manual:
        print(docstr)
        sys.exit()

    if options.in_file_name is None:
        sys.stderr.write("Input file name required. Exiting!\n")
        sys.exit()

    with codecs.open(options.in_file_name, "rb", "utf-8") as infile:
        if options.out_file_name is None:
            ofn = options.in_file_name + ".labels"
        else:
            ofn = options.out_file_name
        with codecs.open(ofn, "wb", "utf-8") as outfile: 
            labeler = TweetLabeler(json_input = options.json_input,
                    delimiter = options.delimiter,
                    left_arrow = options.left_arrow,
                    right_arrow = options.right_arrow
                    )
            labeler.setup_file_io(infile,outfile)
            labeler.label_tweets()


