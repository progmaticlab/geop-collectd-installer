# geop-collectd-installer

## Требования к хостам для установки агента
 * ОС Ubuntu 20 LTS / Ubuntu 18 LTS / Debian 9 / Debian 10 / CentOS 7 / CentOS 8 / RHEL 7 / RHEL 8
 * Python 2 или 3
 
## Установка
**Все действия в документе производятся на управлящей машине**
1. установить git
1. установить ansible (https://docs.ansible.com/ansible/latest/installation_guide/index.html)
1. клонировать geop-collectd-installer
```
    git clone https://github.com/progmaticlab/geop-collectd-installer.git
    cd geop-collectd-installer
```
1. Отредактировать hosts.yaml
 - добавить целевые хост для установки сборщика метрик
 - выставить нужные значения окружения для каждого из них (vm_id, tenant_id, agent_server, список дисков и их типов)
1. запустить установку collectd
```
    ansible-playbook playbooks/install-collectd.yaml -i hosts.yaml
```
