#!/usr/bin/env python2.7

import os
import time
import logging
from optparse import OptionParser, OptionError

from toolkit.digitalocean_cli import client_call, load_node_info

__author__ = 'gunisalvo'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stdout = logging.StreamHandler()
stdout.setLevel(logging.INFO)

logger.addHandler(stdout)


def get_command_line_parser():
    parser = OptionParser()
    parser.add_option('-t', '--type', dest='type', help='the type of installation')
    parser.add_option('-a', '--action', dest='action', help='the action to be performed',
                      choices=['build', 'provision', 'delete', 'lifecycle_test'])

    return parser


def validate_user_options(parser, options):
    if not options.type:
        parser.error('please supply a node info file path [-t]')
    if not options.action:
        parser.error('please supply an action to be performed [-a]')


def build(type):
    logger.info("building {0} ...".format(type))
    os.system(" ansible-playbook build.digital_ocean.yml -i hosts.digital_ocean ")
    nodes_info = load_node_info('./digitalocean.info.yml')

    result = False
    while not result:
        result, responses = client_call(nodes_info, 'status')

    dns_entries = [(response['droplet']['networks']['v4'][0]['ip_address'],
                    response['droplet']['name'],
                    'do.entrementes.org')
                   for response in responses]

    with open('./host_mapping', 'w') as output_file:
        for entry in dns_entries:
            hostname = "{0}.{1}".format(entry[1], entry[2])
            output_file.write("{0}\t{1}\n".format(entry[0], hostname))

    os.system(" ansible-playbook register.digital_ocean.yml -i hosts.digital_ocean -t map_hosts ")


def is_ready(nodes_info):
    result, responses = client_call(nodes_info, 'status')

    ready = [False for r in responses]

    for i in range(len(responses)):
        ready[i] = responses[i]['droplet']['status'] == 'active'

    return ready


def provision(type):
    nodes_info = load_node_info('./digitalocean.info.yml')
    while not all(is_ready(nodes_info)):
        logger.info('waiting for nodes to be ready...')
        time.sleep(30)

    logger.info("provisioning {0} ...".format(type))
    os.system(" ansible-playbook ./provisioning/bootstrap/bootstrap.digital_ocean.yml -i hosts.digital_ocean ")
    os.system(" ansible-playbook -i hosts.digital_ocean '-e env_file=../../provisioning/vars/env.digital_ocean.yml' ./provisioning/blueprints/{0}.yml ".format(type))


def delete(type):
    logger.info("deleting {0} ...".format(type))
    nodes_info = load_node_info('./digitalocean.info.yml')
    client_call(nodes_info, 'delete')

    os.system(" ansible-playbook register.digital_ocean.yml -i hosts.digital_ocean -t unmap_hosts ")


def lifecycle_test(type):
    build(type)
    provision(type)
    delete(type)


if __name__ == "__main__":
    try:
        parser = get_command_line_parser()
        (options, args) = parser.parse_args()
        validate_user_options(parser, options)

        globals()[options.action](options.type)

    except OptionError as opt_error:
        logger.error(opt_error)
        exit(2)
    except IOError as io:
        logger.error(io)
        exit(3)



