import datetime
import sys
import os

__all__ = ['get_rel_path', 'get_prov', 'status_note']


def get_rel_path(input_path, basedir):
    # this is the path for output and display, relative to --basedir flag
    output_path = os.path.relpath(os.path.join(input_path), basedir).replace('\\', '/')
    return output_path


def get_prov(path_file):
    return {path_file: ''.join((sys._getframe(1).f_globals['__name__'], '_', sys._getframe(1).f_code.co_name))}


def status_note(msg, **kwargs):
    if type(msg) is list:
        msg_str_lst = []
        for n in msg:
            msg_str_lst.append(str(n))
        msg = ''.join(msg_str_lst)
    else:
        msg = str(msg)
    log_buffer = kwargs.get('b', None)
    debug_arg = kwargs.get('d', None)
    #date_txt = str(' {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
    date_txt = str(' {:%Y%m%d.%H%M%S}'.format(datetime.datetime.now()))
    if debug_arg:
        debug_txt = ''.join(('[debug: ', sys._getframe(1).f_globals['__name__'], ' @ ', sys._getframe(1).f_code.co_name, ']'))
    else:
        debug_txt = ''
    if not log_buffer:
        print(''.join(('[o2rmeta]', debug_txt, date_txt, ' ', msg)))
