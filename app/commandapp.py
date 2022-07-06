import argparse
import logging
import os.path
import sys

from yee.commandactions import CommandActions
from yee.register.config_register import words_config, base_config, get_server_url, init_log, init_config


def parser_args():
    parser = argparse.ArgumentParser(description='影音助理')
    parser.add_argument('-w', '--workdir', required=True, type=str, help='程序运行的工作目录（配置文件、种子临时下载目录）')
    parser.add_argument('-a', '--action', required=True, type=str, default='moviesmanager',
                        help='需要运行的操作：moviesmanager（影视管理）')
    parser.add_argument('--source-type', required=False, type=str, help='待处理的源目录影视类型movie 电影 tv 剧集（moviesmanager操作时需要）')
    parser.add_argument('--source-dir', required=False, type=str, help='待处理的源目录（moviesmanager操作时需要）')
    parser.add_argument('--target-dir', required=False, type=str, help='处理后的目标目录（moviesmanager操作时需要）')
    parser.add_argument('--file-mode', required=False, type=str, default='link',
                        help='文件处理模式，link、copy（moviesmanager操作时需要，分别为硬链接和复制模式，默认为link）')
    parser.add_argument('--use-country-folder', required=False, action="store_true",
                        help='是否把电影目录保存在国家名文件夹中国呢，True/False（moviesmanager操作时需要）')
    parser.add_argument('--name-ignore-words', required=False, type=str, help='电影名中的无效词设置，多个用英文逗号隔开,')
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
    workdir = args.workdir
    os.environ['WORKDIR'] = workdir
    os.environ['SERVER_URL'] = get_server_url()
    init_log(workdir)
    init_config(os.path.abspath('.'), workdir)
    tmdb_config = base_config.movie_metadata.get('tmdb')
    if tmdb_config is None:
        sys.exit()
    if args.action == 'moviesmanager':
        if args.source_type is None or args.source_type.strip() == '':
            logging.error('源目录影视类型设置为空')
            sys.exit()
        if args.source_dir is None or args.source_dir.strip() == '':
            logging.error('待处理的源目录为空')
            sys.exit()
        if args.target_dir is None or args.target_dir.strip() == '':
            logging.error('处理后的目标目录为空')
            sys.exit()
        if not os.path.exists(args.source_dir):
            logging.error('无法访问源目录：%s，请检查是否做了挂载同时确保有权限访问。' % args.source_dir)
            sys.exit()
        if not os.path.exists(args.target_dir):
            logging.error('无法访问目标路径：%s，请检查是否做了挂载同时确保有权限访问。' % args.target_dir)
            sys.exit()
        if args.name_ignore_words is not None and len(args.name_ignore_words) > 0:
            warr = args.name_ignore_words.split(',')
            for s in warr:
                if s == '':
                    continue
                words_config.ignore_words.append(s)
        CommandActions.movies_manager(tmdb_config['api_key'],base_config.movie_metadata.get('proxies'), args.file_mode, args.use_country_folder,
                                      args.source_type,
                                      args.source_dir, args.target_dir)
