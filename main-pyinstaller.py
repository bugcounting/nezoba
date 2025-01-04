import sys
from src.nezoba.nezoba import main, cmd_parser

if __name__ == '__main__':
    parser = cmd_parser()
    args = parser.parse_args(sys.argv[1:])
    main(args)
