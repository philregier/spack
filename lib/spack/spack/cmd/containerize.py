# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import os
import os.path

import llnl.util.tty

import spack.container
import spack.container.images
import spack.monitor

description = ("creates recipes to build images for different"
               " container runtimes")
section = "container"
level = "long"


def setup_parser(subparser):
    monitor_group = spack.monitor.get_monitor_group(subparser)  # noqa
    subparser.add_argument(
        '--list-os', action='store_true', default=False,
        help='list all the OS that can be used in the bootstrap phase and exit'
    )
    subparser.add_argument(
        '--os', type=str, dest='os', default=None,
        help='OS to use in the bootstrap phase'
    )

    subparser.add_argument(
        '--last-stage',
        choices=('bootstrap', 'build', 'final'),
        default='final',
        help='last stage in the container recipe'
    )


def containerize(parser, args):
    if args.list_os:
        possible_os = spack.container.images.all_bootstrap_os()
        msg = 'The following operating systems can be used to bootstrap Spack:'
        msg += '\n{0}'.format(' '.join(possible_os))
        llnl.util.tty.msg(msg)
        return

    config_dir = args.env_dir or os.getcwd()
    config_file = os.path.abspath(os.path.join(config_dir, 'spack.yaml'))
    if not os.path.exists(config_file):
        msg = 'file not found: {0}'
        raise ValueError(msg.format(config_file))

    config = spack.container.validate(config_file)

    if args.os:
        config['spack']['container']['images']['os'] = args.os

    # If we have a monitor request, add monitor metadata to config
    if args.use_monitor:
        config['spack']['monitor'] = {
            "host": args.monitor_host,
            "keep_going": args.monitor_keep_going,
            "prefix": args.monitor_prefix,
            "tags": args.monitor_tags
        }
    recipe = spack.container.recipe(config, last_phase=args.last_stage)
    print(recipe)
