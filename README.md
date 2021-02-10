# geop-collectd-installer
## нужно иметь джампхост, с которого будут запускаться ansible playbooks.
.. возможные ОС для хостов, на которые будут установлены collectd и telegraf:
    Ubuntu 20 LTS / Ubuntu 18 LTS / Debian 9 / Debian 10 / CentOS 7 / CentOS 8

## установить git

## установить ansible

### клонировать geop-collectd-installer
    git clone https://github.com/progmaticlab/geop-collectd-installer.git

### запустить установку collectd
    cd geop-collectd-installer
    # выставить переменную telegraf_server [IP] в hosts.yaml
    # и указать все хосты, куда надо установить collectd
    ansible-playbook playbooks/install-collectd.yaml -i hosts.yaml

