#!/usr/bin/env python3
#
# This file is part of Checkbox.
#
# Copyright 2011-2016 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import argparse
import shlex
import sys

from collections import OrderedDict
from subprocess import check_output, CalledProcessError

from checkbox_support.parsers.udevadm import UdevadmParser

categories = ("ACCELEROMETER", "AUDIO", "BLUETOOTH", "CAPTURE", "CARDREADER",
              "CDROM", "DISK", "KEYBOARD", "INFINIBAND", "MMAL", "MOUSE",
              "NETWORK", "OTHER", "PARTITION", "TOUCHPAD", "TOUCHSCREEN",
              "USB", "VIDEO", "WATCHDOG", "WIRELESS", "WWAN")

attributes = ("path", "name", "bus", "category", "driver", "product_id",
              "vendor_id", "subproduct_id", "subvendor_id", "product",
              "vendor", "interface", "mac", "product_slug", "vendor_slug",
              "symlink_uuid")


class UdevResultDump:

    def addDevice(self, device):
        for attribute in attributes:
            value = getattr(device, attribute)
            if value is not None:
                print("%s: %s" % (attribute, value))
        print()


class UdevResultLister:

    def __init__(self, categories):
        self.categories = categories
        self._data = OrderedDict()
        self._devices = []
        for c in categories:
            self._data[c] = []

    def display(self, short=False):
        if not self._devices:
            return 1
        for c, devices in self._data.items():
            if short:
                for d in devices:
                    print("{}".format(
                        d.replace('None ', '').replace(' None', '')))
            else:
                print("{} ({}):".format(c, len(devices)))
                for d in devices:
                    print(" - {}".format(d))
                print()

    def filter(self):
        if not self._devices:
            return 1
        for device in self._devices:
            for attribute in attributes:
                value = getattr(device, attribute)
                if value is not None:
                    print("%s: %s" % (attribute, value))
            print()

    def addDevice(self, device):
        c = getattr(device, "category", None)
        if c in self.categories:
            self._devices.append(device)
            p = getattr(device, "product", "Unknow product")
            v = getattr(device, "vendor", "Unknow vendor")
            vid = device.vendor_id if device.vendor_id else 0
            pid = device.product_id if device.product_id else 0
            if not p:
                p = getattr(device, "interface", "Unknow product")
            self._data[c].append(
                "{} {} [{:04x}:{:04x}]".format(v, p, vid, pid))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--command", action='store', type=str,
                        default="udevadm info --export-db",
                        help="""Command to execute to get udevadm information.
                              Only change it if you know what you're doing.""")
    parser.add_argument("-d", "--lsblkcommand", action='store', type=str,
                        default="lsblk -i -n -P -o KNAME,TYPE,MOUNTPOINT",
                        help="""Command to execute to get lsblk information.
                              Only change it if you know what you're doing.""")
    parser.add_argument('-l', '--list', nargs='+', choices=categories,
                        metavar=("CATEGORY"), default=(),
                        help="""List devices found under the requested
                        categories.
                        Acceptable categories to list are:
                        {}""".format(', '.join(categories)))
    parser.add_argument('-f', '--filter', nargs='+', choices=categories,
                        metavar=("CATEGORY"), default=(),
                        help="""Filter devices found under the requested
                        categories.
                        Acceptable categories to list are:
                        {}""".format(', '.join(categories)))
    parser.add_argument('-s', '--short', action='store_true')
    args = parser.parse_args()
    try:
        output = check_output(shlex.split(args.command))
        lsblk = check_output(shlex.split(args.lsblkcommand))
    except CalledProcessError as exc:
        raise SystemExit(exc)
    # Set the error policy to 'ignore' in order to let tests depending on this
    # resource to properly match udev properties
    output = output.decode("UTF-8", errors='ignore')
    lsblk = lsblk.decode("UTF-8", errors='ignore')
    list_partitions = False
    if 'PARTITION' in args.list or 'PARTITION' in args.filter:
        list_partitions = True
    udev = UdevadmParser(output, lsblk=lsblk, list_partitions=list_partitions)
    if args.list:
        result = UdevResultLister(args.list)
        udev.run(result)
        return result.display(args.short)
    elif args.filter:
        result = UdevResultLister(args.filter)
        udev.run(result)
        return result.filter()
    else:
        result = UdevResultDump()
        udev.run(result)


if __name__ == "__main__":
    sys.exit(main())
