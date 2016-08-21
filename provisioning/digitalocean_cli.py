#!/usr/bin/env python2.7

import yaml
from optparse import OptionParser, OptionError
import requests
from requests_toolbelt.utils import dump
import os

DO_TOKEN = os.environ["DO_TOKEN"]


def get_command_line_parser():
    parser = OptionParser()
    parser.add_option('-n','--node', \
        dest='node', \
        help='the path of a digitalocean node creation report')
    parser.add_option('-a','--action', \
        dest='action', \
        help='the action to be performed on a digitalocean node', \
        choices=['start','stop'])
    parser.add_option('-v','--verbose', \
        action="store_true", \
        dest="verbose")

    return parser


def validate_user_options(parser, options):
    if not options.node:
        parser.error('please supply a node info file path [-n]')
    if not options.action:
        parser.error('please supply an action to be performed [-a]')


def load_node_info(info_path):
    with open(info_path, 'r') as info_file:
        configuration = yaml.load(info_file)
    return configuration


def send_action(action_type, url, debug=False):
    payload = { "type" : action_type }
    headers = {
        "Authorization": "Bearer {0}".format(DO_TOKEN),
        "Content-Type": "application/json"
    }
    print("{0} -> {1}".format(action_type,url))
    resp = requests.post(url, json=payload, headers=headers)
    if debug:
        data = dump.dump_all(resp)
        print(data.decode('utf-8'))


if __name__ == '__main__':

    available_actions = {
        "start": "power_on",
        "stop": "power_off"
    }

    try:
        parser = get_command_line_parser()
        (options, args) = parser.parse_args()
        validate_user_options(parser, options)
        configuration = load_node_info(options.node)
        send_action(available_actions[options.action], \
            configuration['node']['url'], \
            options.verbose)
        exit(0)
    except OptionError as opt_error:
        print(opt_error)
        exit(1)
    except IOError as io:
        print(io)
        exit(1)
