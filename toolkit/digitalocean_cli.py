#!/usr/bin/env python2.7

import yaml
from optparse import OptionParser, OptionError
import requests
from requests_toolbelt.utils import dump
import os
import json

DO_TOKEN = os.environ["DO_TOKEN"]

available_actions = {
    "status": {
        "method": "_GET",
        "type": None,
        "extra-args": [],
        "uri-postfix": ""},
    "start": { 
        "method": "_POST",
        "type": "power_on",
        "extra-args": [],
        "uri-postfix": "/actions"},
    "stop": { 
        "method": "_POST",
        "type": "power_off",
        "extra-args": [],
        "uri-postfix":
        "/actions"},
    "snapshot": { 
        "method": "_POST",
        "type": "snapshot",
        "extra-args": ["name"],
        "uri-postfix": "/actions"},
    "delete": { 
        "method": "_DELETE",
        "type": None,
        "extra-args": [],
        "uri-postfix": ""}
}


def get_command_line_parser():
    parser = OptionParser()
    parser.add_option('-n', '--node', dest='node', help='the path of a digital ocean node creation report')
    parser.add_option('-a', '--action', dest='action', help='the action to be performed on a digital ocean node',
                      choices=['status', 'start', 'stop', 'snapshot', 'delete'])
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose")
    parser.add_option('-x','--extra', dest="extra",
                      help='JSON formatted dictionary of extra arguments for specific action')

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


def _GET(action, url, extra_args, volumes, debug=False):
    full_url = "{0}{1}".format(url, action['uri-postfix'])
    headers = {
        "Authorization": "Bearer {0}".format(DO_TOKEN),
    }

    resp = requests.get(full_url, headers=headers)
    if debug:
        data = dump.dump_all(resp)
        print(data.decode('utf-8'))

    return json.dumps(resp.json()['droplet'], indent=2)


def _POST(action, url, extra_args, volumes, debug=False):
    payload = { "type" : action['type'] }
    
    if extra_args:
        for arg in action['extra-args']:
            payload[arg] = extra_args[arg]

    headers = {
        "Authorization": "Bearer {0}".format(DO_TOKEN),
        "Content-Type": "application/json"
    }
    full_url = "{0}{1}".format(url, action['uri-postfix'])
    print("{0} -> {1}".format(action['type'], full_url))
    resp = requests.post(full_url, json=payload, headers=headers)
    if debug:
        data = dump.dump_all(resp)
        print(data.decode('utf-8'))


def _DELETE(action, url, extra_args, volumes, debug=False):
    full_url = "{0}{1}".format(url, action['uri-postfix'])
    __http_delete(full_url, debug)

    for volume in volumes:
        full_url = "{0}{1}".format(volume, action['uri-postfix'])
        __http_delete(full_url, debug)


def __http_delete(full_url, debug):
    headers = {
        "Authorization": "Bearer {0}".format(DO_TOKEN),
    }
    print("{0} -> {1}".format(action['type'], full_url))
    resp = requests.delete(full_url, headers=headers)
    if debug:
        data = dump.dump_all(resp)
        print(data.decode('utf-8'))


if __name__ == '__main__':

    try:
        parser = get_command_line_parser()
        (options, args) = parser.parse_args()
        validate_user_options(parser, options)
        configuration = load_node_info(options.node)
        action = available_actions[options.action]
        
        extra_args = None
        if action['extra-args']:
            extra_args = json.loads(options.extra)
        for node in configuration['nodes']:
            result = locals()[action['method']](action, node['url'], extra_args, node['volumes'], options.verbose)
            print(result)
        
        exit(0)
    except OptionError as opt_error:
        print(opt_error)
        exit(1)
    except IOError as io:
        print(io)
        exit(1)
