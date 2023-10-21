import logging
from optparse import OptionParser

from scoring_api.api.server import run_server


def main():
    op = OptionParser()
    op.add_option('-g', '--host', action='store', type=str, default='localhost')
    op.add_option('-p', '--port', action='store', type=int, default=8080)
    op.add_option('-l', '--log', action='store', default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S'
    )
    run_server(host=opts.host, port=opts.port)


if __name__ == '__main__':
    main()
