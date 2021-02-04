import collectd
import re
import os
import json

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


def read_func():
    sys_arr = []
    sys_str = ''
    sys_size = 0
    sys_usage = 0
    GB = 1024**2

    sys_type = 0
    sys_name = 0

    type_map = {}
    tmp_data = {}
    tmp_data_key = 0

    ignore_fs = ["tmpfs", "devtmpfs", "devfs", "iso9660", "overlay", "aufs", "squashfs",
                "cgroup", "cgroup2", "autofs", "proc", "sysfs", "bpf", "devpts", "securityfs",
                "pstore", "efivarfs", "hugetlbfs", "mqueue", "debugfs", "tracefs", "fusectl", 
                "configfs", "binfmt_misc", "fuse.gvfsd-fuse"]

    fs_type_map = '/opt/collectd_plugins/dict/fs_type_map.json'
    fs_type_instance = '/opt/collectd_plugins/dict/fs_type_instance.json'

    if os.stat(fs_type_map).st_size > 1:
        with open(fs_type_map, 'r') as f:
            type_map = json.load(f)
    else:
        type_map = {'.*': 'sata'}

    with open('/proc/mounts', 'r') as f:
        for line in f.read().split('\n'):
            sys_arr = line.split()
            if len(sys_arr) and sys_arr[2] not in ignore_fs:
                sys_str = os.statvfs(sys_arr[1])
                sys_size = (sys_str.f_bsize * sys_str.f_blocks) / GB
                sys_usage = (sys_str.f_blocks - sys_str.f_bfree) / GB

                for key in type_map.keys():
                    if re.search(key, sys_arr[0]):
                        sys_type = type_map.get(key)
                        break

                sys_name = re.findall(r'[a-z]+', sys_arr[0])[-1]
                with open(fs_type_instance, 'r+') as d:
                    disk_names = {}
                    if d.tell() > 0:
                        disk_names = json.load(d)
                    if disk_names.get(sys_name) is None:
                        disk_names[sys_name] = 'disk' + f'{len(disk_names) + 1}'
                        json.dump(disk_names, d)
                        d.truncate(len(json.dumps(disk_names)))
                    tmp_data_key = disk_names[sys_name]
                
                if tmp_data.get(tmp_data_key) is None:
                    tmp_data[tmp_data_key] = {'type': sys_type, 'disk_size': 0, 'disk_usage': 0}

                tmp_data[tmp_data_key]['disk_size'] += sys_size
                tmp_data[tmp_data_key]['disk_usage'] += sys_usage

    for key in tmp_data.keys():
        collectd.Values(plugin = 'vm_disk',
                    type_instance = key,
                    type = f'{tmp_data[key].get("type")}_disk_usage',
                    values = [tmp_data[key].get('disk_usage')]).dispatch()

        collectd.Values(plugin = 'vm_disk',
                    type_instance = key,
                    type = f'{tmp_data[key].get("type")}_disk_size',
                    values = [tmp_data[key].get('disk_size')]).dispatch()


collectd.register_config(config_func)
collectd.register_read(read_func)


