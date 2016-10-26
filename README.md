# docker-mariadb-backup
Docker image for backing up and restoring mariadb

# Quick start
## Run
### Scheduled Backup

This will backup your data each day at 3am

Docker Engine
```
docker run \
  -v ./backup:/backup \
  -e TIMEZONE="Europe/Berlin" \
  -e SCHEDULE="0 0 3 * *" \
  -e BACKUP_METHOD="mysqldump" \
  -e MYSQL_HOST=mysql \
  -e MYSQL_DATABASE=database \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=pass \
  -t db-backup \
  --detach zeenly/mariadb-backup
```

Docker Compose
```yaml
    test-backup:
        image: zeenlym/mariadb-backup
        environment:
            - TIMEZONE=Europe/Berlin
            - SCHEDULE="0 0 3 * *"
            - BACKUP_METHOD=mysqldump
            - MYSQL_HOST=mysql
            - MYSQL_DATABASE=database
            - MYSQL_USER=user
            - MYSQL_PASSWORD=pass
        volumes:
            - ./backup:/backup
```

### Manual backup

To backup manually juste exec cmd `backup`

```
docker run ... zeenly/mariadb-backup backup
```

or from running container

```
docker exec db-backup backup
```

### Restore

To restore backup juste exec cmd `restore`. You will be asking which backup to restore. Il you want the latest add `--latest` swith.

```
docker run ... -i -t zeenly/mariadb-backup restore
```

or from running container

```
docker exec -it db-backup restore
```

> Don't forget the `-it` switch

# Advance usage
## Environment variables
There is no default environment variables, you must set them.

Scheduler:
 - `SCHEDULE` : [required] cron format scheduling, for more help visit https://en.wikipedia.org/wiki/Cron
 - `TIMEZONE` : [optional] timezone

Mysql:
 - `MYSQL_HOST`     : [required] Set mysql host
 - `MYSQL_USER`     : [required] Use this mysql user
 - `MYSQL_PASSWORD` : [optional] user password
 - `MYSQL_DATABASE` : [optional] Database to backup

Backup:
 - `BACKUP_METHOD`  : [required] Choose backup method. Example `mysqldump`
 - `BACKUP_OPTS`    : [optional] Additional argument to pass to backup method

Restore:
 - `RESTORE_OPTS`   : [optional] Additional argument to pass to restore
> Restore use `BACKUP_METHOD` var too

## mdbtool
mdbtool is the main python program to backup and restore data. It support plugins so you can choose your way to backup and restore mysql dumps.

Run `mdbtool -h` for more help.

## Backup Method
Only `mysqldump` is available by default. You may want to add your own by reading Make Your Own Plugin.

### MysqlDump
This plugins use mysqldump to backup data and save backup files in `7z` format into `/backup` folder. You should mount volume for `/backup` in order to persist your data in host filesystem.

You can disable compression with `--no-compress` switch

You can pass arguments directly to mysqldump after the `+` argument
```
# Get mysqldump binary help
mdbtool backup mysqldump + --help
```

Run `mdbtool backup mysql -h` for more help on this plugin.

# Development
You are this far away because you want to develop your own backup method.

## Make Your Own Plugin
All mdbtool plugins are stored in `/usr/local/mdbtool/plugins` directory.

Each plugin should have this architecture:
 - `myplugin` : plugin directory
 - `myplugin/__init__.py` : python implementation
 - `myplugin/Backup.py` : module for handling backup
 - `myplugin/Restore.py` : module for handling restoration

Plugins may have there own files in their directory.

`Backup.py` and `Restore.py` are both entrypoint. In order for your plugin to be recognize by the plugin system you define the `main` function :
```python
def main(args):
    ''' Plugin entry point, args is specific plugin args. To get full args use sys.argv.
    pass
```

> Restore.py is optional but this projet was born in order to give both backup and restoration of mariadb database

If your plugin is correct it should appreaded with the command `mdbtool backup --list`

If you need example see mysqldump plugin

## Use your plugin
Now your plguin is created you can make your Dockerfile

```Dockerfile
FROM zeenly/mariadb-backup
MAINTAINER First LAST <first.last@email.com>

COPY myplugin /usr/local/mdbtool/plugins/myplugin
```

Then enjoy
