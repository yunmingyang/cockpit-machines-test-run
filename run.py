#!/usr/bin/python3

import os
import yaml
import secrets
import argparse
import subprocess


class ArgsError(RuntimeError):
    def __init__(self, *args, **kwargs):
        pass


class TestSuite:
    def __init__(self,
                 mode=None,
                 cases_path=None,
                 yaml_path=None,
                 res_path=None,
                 tag=None,
                 browser=None,
                 options=None):

        self.mode = mode
        self.cases_path = cases_path
        self.yaml_path = yaml_path
        self.res_path = res_path
        self.tag = tag
        self.browser = browser
        self.options = options

    def _check(self):
        self._check_mode()
        if self.mode == 'file':
            if not self.yaml_path:
                raise ArgsError('need yaml file path')
            self._parser_from_file()
        elif self.mode == 'options' and not self.options:
            raise ArgsError('options must be set')
        self._check_param()

    def _check_mode(self):
        if self.mode not in ['options', 'file']:
            raise ArgsError('unsupported mode for executor')

    def _parser_from_file(self):
        if not os.path.exists(self.yaml_path):
            raise ArgsError('yaml file does not exist')
        with open(self.yaml_path, 'r') as fp:
            self.options = yaml.load(fp, yaml.FullLoader)

    def _check_param(self):
        keys = self.options.keys()
        if 'GUEST' not in keys:
            raise ArgsError('GUEST must be set')

    def set_env(self):
        self._check()
        for key, value in self.options.items():
            os.environ[key] = value

    def run(self):
        if not os.path.exists(self.cases_path):
            raise ArgsError("cases path is not existing.")
        self.set_env()

        cmd_list = ['avocado', 'run', self.cases_path, '-t', self.tag]
        if self.res_path:
            cmd_list.append('--job-results-dir')
            cmd_list.append(self.res_path + '/'
                            + os.environ.get('BROWSER', secrets.token_hex(2)))

        run_cmd = ' '.join(cmd_list)
        subprocess.run(run_cmd, shell=True)

    def run_from_file(self):
        for b in self.browser:
            print(b)
            os.environ['BROWSER'] = b
            self.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cases_path', help="cases files path")
    parser.add_argument('yaml_path', help="yaml files path")
    parser.add_argument('-r', '--result', help="avocado results path")
    parser.add_argument('-t', '--tag', help="avocado tags", default='machines')
    parser.add_argument('-b',
                        '--browser',
                        help='the browser that test runs',
                        default=['chrome', 'firefox', 'edge'])
    args = parser.parse_args()

    TestSuite('file',
              cases_path=args.cases_path,
              yaml_path=args.yaml_path,
              res_path=args.result,
              tag=args.tag,
              browser=args.browser if args.browser == ['chrome', 'firefox', 'edge'] else args.browser.split(' ')).run_from_file()


if __name__ == '__main__':
    main()
