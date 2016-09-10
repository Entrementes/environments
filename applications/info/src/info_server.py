#!/usr/bin/env python2.7

import logging
from flask import Flask, Response
from optparse import OptionParser, OptionError

__author__ = 'gunisalvo'

app = Flask(__name__)


def get_command_line_parser():
    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', help='info server port')
    parser.add_option('-l', '--log-file', dest='log_file',
                      default="../log/server.log", help='log file location')
    parser.add_option('-i', '--info-file', dest='info_file',
                      default="../conf/app_info.json", help='info file location')

    return parser


def validate_user_options(parser, options):
    if not options.port:
        parser.error('please supply an available port [-p]')


def setup_logger(app, file_path):
    logFormatStr = '[%(asctime)s] p%(process)s %(levelname)s - %(message)s'
    logging.basicConfig(format=logFormatStr, filename=file_path, level=logging.DEBUG)
    formatter = logging.Formatter(logFormatStr, '%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler(file_path)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    app.logger.addHandler(fileHandler)
    app.logger.addHandler(streamHandler)
    app.logger.info("Logging is set up.")

    return app.logger


@app.route("/info")
def get_info():
    with open(app.config['info_file'], 'r') as info_data:
        data = info_data.readlines()
        return Response(response=data, status=200, mimetype="application/json")


if __name__ == '__main__':
    try:
        parser = get_command_line_parser()
        (options, args) = parser.parse_args()
        validate_user_options(parser, options)

        logger = setup_logger(app, options.log_file)

        app.config['info_file'] = options.info_file

        app.run(port=int(options.port))

    except OptionError as opt_error:
        logger.error(opt_error)
        exit(2)
    except Exception as ex:
        logger.error(ex)
        exit(3)