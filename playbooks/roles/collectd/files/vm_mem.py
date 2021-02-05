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
            collectd.info('vm_mem plugin: Unknown config key "%s"' % key)
    if path_set:
        collectd.info('vm_mem plugin: Using overridden path %s' % PATH)
    else:
        collectd.info('vm_mem plugin: Using default path %s' % PATH)


def read_func():
    mem_size = 0 
    mem_usage = 0 
    mem_free = 0 
    
    # TODO: mem_shortage (may be balloon + swap-out)

    with open('/proc/meminfo', 'r') as f:
        for line in f.read().split('\n'):
            if re.search(r'^MemTotal:  *', line):
                mem_size = int(line.replace('MemTotal:', '').replace('kB', '').strip())
            if re.search(r'^MemFree: *', line):
                mem_free = int(line.replace('MemFree:', '').replace('kB', '').strip())

    mem_usage = mem_size - mem_free

    # vm memory size
    collectd.Values(plugin='vm_mem',
                    type='vm_mem_size',
                    type_instance='memory_0',
                    values=[mem_size]).dispatch()
    # overal memory usage
    collectd.Values(plugin='vm_mem',
                    type='vm_mem_usage',
                    type_instance='memory_0',
                    values=[mem_usage]).dispatch()


collectd.register_config(config_func)
collectd.register_read(read_func)


