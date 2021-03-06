## Build/Integration Server

### Local Build:

```
$ cd environments/boxes/constantinopla/
$ vagrant { up, provision, destroy }
```
> map your built nodes on your /etc/hosts

### Digital Ocean:
##### Build

```
$ cd environments/boxes/constantinopla/
$ ansible-playbook build.digital_ocean.yml --ask-vault-pass -i hosts.digital_ocean
```
> map your built nodes on your /etc/hosts

#### Bootstrap/Provision

```
$ cd environments/boxes/constantinopla/
$ ansible-playbook provisioning/bootstrap/bootstrap.digital_ocean.yml --ask-vault-pass -i hosts.digital_ocean
$ ansible-playbook provisioning/blueprints/constantinopla.yml --ask-vault-pass -i hosts.digital_ocean
```

#### Control

```
$ cd environments/boxes/constantinopla/
$ export DO_TOKEN=<< YOR DIGITAL OCEAN API TOKEN >>
$ python ../../toolkit/digitalocean_cli.py -n constantinopla.info.yml -a start
$ python ../../toolkit/digitalocean_cli.py -n constantinopla.info.yml -a stop
$ python ../../toolkit/digitalocean_cli.py -n constantinopla.info.yml -a delete
```
> **constantinopla.info.yml** is generated by the **build.digital_ocean.yml** playbook
