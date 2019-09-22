import os

def process_show(*args):
    this_dir, _ = os.path.split(__file__)
    if 'yourself' in args:
        file_path = os.path.join(this_dir, 'data', 'ada.dat')
        print open(file_path, 'r').read()
    else:
        print('Unable to show...')
