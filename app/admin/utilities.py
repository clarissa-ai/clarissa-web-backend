from psutil import (
    cpu_percent,
    virtual_memory,
    disk_usage,
)


def get_system_stats():
    ret = {}
    ret['cpu_percent'] = cpu_percent()
    ret['mem_percent'] = virtual_memory().percent
    ret['disk_percent'] = disk_usage('/').percent
    return ret
