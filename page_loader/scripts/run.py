#!usr/bin/env python3
from page_loader.load import load_content, make_filename
from page_loader.cli import get_parse_args


def main():
    parser = get_parse_args()
    args = parser.parse_args()
    response = load_content(args.url)
    directory = args.output
    if directory:
        directory += '/'
    file_name = make_filename(args.url)
    with open(f'{directory}{file_name}', 'w') as file:
        file.write(response.text)


if __name__ == '__main__':
    main()
