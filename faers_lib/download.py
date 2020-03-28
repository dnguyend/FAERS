"""Script to download TXT files from FDA Adverse events database
"""

import urllib.request
import os
from .common import main_data_path as download_path
from .common import zip_name_template


def download_one(yyyy, qq):
    """ download one single file form the FDA drug event site
    """
    url = zip_name_template % (yyyy, qq)
    fname = zip_name_template.split('/')[-1]
    short_name = fname % (yyyy, qq)
    out_file = os.path.join(download_path, short_name)
    if os.path.isfile(out_file):
        print('File exists %s, skip' % out_file)
        return None
    print('Doing %s' % out_file)
    # return None
    try:
        urllib.request.urlretrieve(url, out_file)
        return out_file
    except Exception as e:
        print(e)
        return None


def extract_one_file(fname, cleanup=False):
    """ extracting one downloaded zip file
    to the same folder.
    remove zip file if cleanup
    """
    out_dir = fname[:-4]
    if os.path.isdir(out_dir):
        print('Already exists %s. Skip' % (out_dir))
        return
    else:
        print('Extracting %s.' % (out_dir))
        try:
            os.system('unzip %s -d %s' % (fname, out_dir))
            if cleanup:
                os.remove(fname)
        except Exception as e:
            print(e)


def _get_current_year():
    """ get the current year - GMT time
    """
    import datetime
    return datetime.datetime.now().year


def load_all_files(d_from=2012, d_to=None):
    """Download all files from the FDA drug event site
    from begining (2012) to now)
    """
    if d_to is None:
        d_to = _get_current_year() + 1
    year_list = range(d_from, d_to)
    q_list = range(1, 5)
    for yyyy in year_list:
        for qq in q_list:
            download_one(yyyy, qq)


def extract_all_files():
    """Extracting all downloaded data.
    skip if an error occurs and move to the next file
    """
    for f in os.listdir(download_path):
        if f.endswith('.zip'):
            fname = os.path.join(download_path, f)
            extract_one_file(fname)


if __name__ == '__main__':
    pass
