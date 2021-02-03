import collectd
import re

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


def read_func():
    # count
    count = 0 
    cpu_usage = 0
    cpu_steal = 0
    cpu_array = []
    with open('/proc/stat', 'r') as f:
        for line in f.read().split('\n'):
            if re.search(r'^cpu[0-9][0-9]*', line):
                count += 1
            if re.search(r'^cpu  *', line):
                cpu_array = list(map(int, line.replace("cpu","").split()))
                total = sum(cpu_array)
                cpu_usage = (total - cpu_array[3]) / total
                cpu_steal = cpu_array[7] / total

    
    # cpu core count 
    collectd.Values(plugin='vm_cpu',
                    type="vm_cpu_num",
                    values=[count]).dispatch()
    # overal cpu steal
    collectd.Values(plugin='vm_cpu',
                    type="vm_cpu_shortage",
                    values=[cpu_steal]).dispatch()
    # overal cpu usage
    collectd.Values(plugin='vm_cpu',
                    type="vm_cpu_usage",
                    values=[cpu_usage]).dispatch()


collectd.register_config(config_func)
collectd.register_read(read_func)

