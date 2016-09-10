#!/usr/bin/env python2.7

__author__ = 'gunisalvo'

import yaml
from optparse import OptionParser, OptionError
import requests
from requests_toolbelt.utils import dump
import os
import json
import logging

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
        "uri-postfix": "/actions"},
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler()
stdout.setLevel(logging.INFO)

logger.addHandler(stdout)


def get_command_line_parser():
    parser = OptionParser()
    parser.add_option('-n', '--node', dest='node', help='the path of a digital ocean node creation report')
    parser.add_option('-a', '--action', dest='action', help='the action to be performed on a digital ocean node',
                      choices=['status', 'start', 'stop', 'snapshot', 'delete'])
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose")
    parser.add_option('-x', '--extra', dest="extra",
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

    return resp


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
    resp = requests.post(full_url, json=payload, headers=headers)
    if debug:
        data = dump.dump_all(resp)
        print(data.decode('utf-8'))

    return resp


def _DELETE(action, url, extra_args, volumes, debug=False):
    full_url = "{0}{1}".format(url, action['uri-postfix'])
    resp = __http_delete(full_url, debug)

    if volumes:

        for volume in volumes:
            full_url = "{0}{1}".format(volume, action['uri-postfix'])
            __http_delete(full_url, debug)

    return resp


def __http_delete(full_url, debug):
    headers = {
        "Authorization": "Bearer {0}".format(DO_TOKEN),
    }
    resp = requests.delete(full_url, headers=headers)
    if debug:
        data = dump.dump_all(resp)
        logger.info(data.decode('utf-8'))

    return resp


def client_call(info, action_name, extra_args={}, debug=False):
    action = available_actions[action_name]

    node_calls = []
    response_bodies = []

    extra_json = None
    if action['extra-args']:
        extra_json = json.loads(extra_args)

    for node in info['nodes']:
        result = globals()[action['method']](action, node['url'], extra_json, node['volumes'], debug)

        if result.ok:
            if result.text:
                json_response = result.json()
                if 'droplet' in json_response:
                    logger.info(json.dumps(json_response['droplet'], indent=2))
                elif 'action' in json_response:
                    logger.info(json.dumps(json_response['action'], indent=2))
                response_bodies.append(json_response)
            else:
                json_response = {'message': 'ok'}
                logger.info(json.dumps(json_response, indent=2))
                response_bodies.append(json_response)

            node_calls.append(True)

        else:
            json_response = result.json()
            logger.info(json.dumps(json_response, indent=2))

            node_calls.append(False)
            response_bodies.append(json_response)

    return all(node_calls), response_bodies


if __name__ == '__main__':

    try:
        parser = get_command_line_parser()
        (options, args) = parser.parse_args()
        validate_user_options(parser, options)
        info = load_node_info(options.node)
        extra_args = options.extra

        call_result, payloads = client_call(info, options.action, extra_args, options.verbose)

        if call_result:
            exit(0)
        else:
            exit(1)

    except OptionError as opt_error:
        logger.error(opt_error)
        exit(2)
    except IOError as io:
        logger.error(io)
        exit(3)
