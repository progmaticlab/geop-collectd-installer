import collectd

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
    for i in range (512):
        collectd.Values(plugin='ballast',
                        type='count',
                        type_instance='ballast', 
                        values=[255]).dispatch()


collectd.register_config(config_func)
collectd.register_read(read_func)

