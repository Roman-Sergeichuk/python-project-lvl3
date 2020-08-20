import argparse


def get_parse_args():
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='',
        help='set output directory'
    )
    return parser
