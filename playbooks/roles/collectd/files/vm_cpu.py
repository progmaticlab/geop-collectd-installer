import collectd
import re
import time
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
            collectd.info('vm_cpu plugin: Unknown config key "%s"' % key)
    if path_set:
        collectd.info('vm_cpu plugin: Using overridden path %s' % PATH)
    else:
        collectd.info('vm_cpu plugin: Using default path %s' % PATH)

def truncate(number, digits):
    stepper = float(10.0 ** digits)
    return float(math.trunc(stepper * number) / stepper)

def read_func():
    count = 0
    cpu_usage = 0
    cpu_steal = 0
    cpu_array_1 = []
    cpu_array_2 = []
    total = 0
    with open('/proc/stat', 'r') as f:
        for line in f.read().split('\n'):
            if re.search(r'^cpu  *', line):
                cpu_array_1 = list(map(int, line.replace('cpu','').split()))
                break

    time.sleep(1)

    with open('/proc/stat', 'r') as f:
        for line in f.read().split('\n'):
            if re.search(r'^cpu[0-9][0-9]*', line):
                count += 1
            if re.search(r'^cpu  *', line):
                cpu_array_2 = list(map(int, line.replace('cpu','').split()))

    total = float(sum(cpu_array_2) - sum(cpu_array_1))
    cpu_usage = float(total - cpu_array_2[3] + cpu_array_1[3]) / total
    cpu_steal = float(cpu_array_2[7] - cpu_array_1[7]) / total

    # cpu core count
    collectd.Values(plugin='vm_cpu',
                    type='cpu_num',
                    type_instance='cpu_0',
                    values=[count]).dispatch()
    # overal cpu steal
    collectd.Values(plugin='vm_cpu',
                    type='cpu_shortage',
                    type_instance='cpu_0',
                    values=[truncate(cpu_steal*100, 2)]).dispatch()
    # overal cpu usage
    collectd.Values(plugin='vm_cpu',
                    type='cpu_usage',
                    type_instance='cpu_0',
                    values=[truncate(cpu_usage*100, 2)]).dispatch()


collectd.register_config(config_func)
collectd.register_read(read_func)

