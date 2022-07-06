import argparse
import logging.config
import os
import shutil
import sys

from yee.Constants import APP_VERSION
from yee.register.config_register import get_server_url, init_log, init_config
from yee.upgrade import Upgrade


def parser_args():
    parser = argparse.ArgumentParser(description='豆瓣电影自动下载器')
    parser.add_argument('-w', '--workdir', required=True, type=str, help='程序运行的工作目录（配置文件、种子临时下载目录）')
    args = parser.parse_args()
    return args


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
if __name__ == '__main__':
    args = parser_args()
    base_path = os.path.abspath('.')
    workdir = args.workdir
    if not os.path.exists(workdir):
        logging.info('请提供正确的配置，工作目录不存在：%s' % workdir)
        sys.exit()
    Upgrade.update_filepath(workdir)

    dbpath = os.path.join(workdir, "db")
    if not os.path.exists(dbpath):
        os.makedirs(dbpath)
    os.environ['WORKDIR'] = workdir
    os.environ['SERVER_URL'] = get_server_url()
    if not os.path.exists(workdir + os.sep + 'logs'):
        os.mkdir(workdir + os.sep + 'logs')
    shutil.copytree(os.path.join(base_path, 'conf', 'rule'), os.path.join(workdir, 'conf', 'rule'), dirs_exist_ok=True)
    shutil.copytree(os.path.join(base_path, 'conf', 'words'), os.path.join(workdir, 'conf', 'words'),
                    dirs_exist_ok=True)
    shutil.copytree(os.path.join(base_path, 'sites'), workdir + os.sep + 'sites', dirs_exist_ok=True)
    os.environ['WORKDIR'] = workdir
    init_log(workdir)
    init_config(base_path, workdir)
    import yee.app as app

    logging.info(f'当前版本: {APP_VERSION}')

    app.start()
