from faers_lib.download import load_all_files, extract_all_files


if __name__ == '__main__':
    """Download all files from the begining (2012 to now)
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start',
                        required=False,
                        default=2012)
    parser.add_argument('-e', '--end',
                        required=False,
                        default=0)
    args = parser.parse_args()
    if args.end == 0:
        end = None
    else:
        end = int(args.end)
    start = int(args.start)

    load_all_files(start, end)
    extract_all_files()
