import collectd
import re
import os
import json
import math

def config_func(config):
    path_set = False
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]
        if key == 'path':
            global PATH
            PATH = val
            path_set = True
        else:
            collectd.info('vm_disk plugin: Unknown config key "%s"' % key)
    if path_set:
        collectd.info('vm_disk plugin: Using overridden path %s' % PATH)
    else:
        collectd.info('vm_disk plugin: Using default path %s' % PATH)


def truncate(number, digits):
    stepper = float(10.0 ** digits)
    return float(math.trunc(stepper * number) / stepper)

def json_load(path, none_str):
    if os.stat(path).st_size > 1:
        with open(path, 'r') as f:
            return json.load(f)
    return none_str

def read_func():
    MB = float(1024**2)
    ignore_fs = ["tmpfs", "devtmpfs", "devfs", "iso9660", "overlay", "aufs", "squashfs",
                "cgroup", "cgroup2", "autofs", "proc", "sysfs", "bpf", "devpts", "securityfs",
                "pstore", "efivarfs", "hugetlbfs", "mqueue", "debugfs", "tracefs", "fusectl",
                "configfs", "binfmt_misc", "fuse.gvfsd-fuse", "fuse.lxcfs", "nsfs"]

    disk_type_map_path = '/opt/collectd_plugins/dict/disk_type_map.json'
    disk_type_instance_path = '/opt/collectd_plugins/dict/disk_type_instance.json'

    fs_data_array = []      # for ex. ['/dev/sda2', '/', 'ext4', ...]
    fs_data_struct = {}     # for ex. os.statvfs('/')
    fs_size = 0             # for ex. sda2 size
    fs_usage = 0            # for ex. sda2 usage
    disk_name = ''          # sda, sdb etc.
    disk_type = ''          # ssd | hdd | sata
    disk_names = {}         # {sda: disk1, sdb: disk2, xdb: disk3 ...}
    cur_disk_num = ''       # disk1 | disk2 | disk3 ...
    disks_data = {}         # {disk1: {sda_data}, disk2: {sdb_data}..}


    disk_type_map = json_load(disk_type_map_path, {'.*': 'sata'})
    disk_type_instance = json_load(disk_type_instance_path, {})

    with open('/proc/mounts', 'r') as f:
        disks_data = {}
        for line in f.read().split('\n'):
            fs_data_array = line.split()

            if not len(fs_data_array) or fs_data_array[2] in ignore_fs:
                continue

            fs_data_struct = os.statvfs(fs_data_array[1])
            fs_size = float(fs_data_struct.f_bsize * fs_data_struct.f_blocks) / MB
            fs_usage = float(fs_data_struct.f_bsize) * float(fs_data_struct.f_blocks - fs_data_struct.f_bfree) / MB

            disk_name = re.findall(r'[a-z]+', fs_data_array[0])[-1]

            for key in disk_type_map.keys():
                if re.search(key, disk_name):
                    disk_type = disk_type_map.get(key)
                    break

            cur_disk_num = disk_type_instance.get(disk_name)

            # accumulate different fs data
            if cur_disk_num is not None:
                if disks_data.get(cur_disk_num) is None:
                    disks_data[cur_disk_num] = {'type': disk_type, 'disk_size': 0, 'disk_usage': 0}

                disks_data[cur_disk_num]['disk_size'] += fs_size
                disks_data[cur_disk_num]['disk_usage'] += fs_usage

    for disk in disks_data.keys():
        cur_disk_data = disks_data[disk]
        # vm disk fs size
        collectd.Values(plugin = 'vm_disk',
                    type_instance = disk,
                    type = 'disk_size_' + cur_disk_data.get('type'),
                    values = [truncate(cur_disk_data.get('disk_size'), 6)]).dispatch()
        # vm disk fs usage
        collectd.Values(plugin = 'vm_disk',
                    type_instance = disk,
                    type = 'disk_usage_' + cur_disk_data.get('type'),
                    values = [truncate(cur_disk_data.get('disk_usage'), 6)]).dispatch()


collectd.register_config(config_func)
collectd.register_read(read_func)

