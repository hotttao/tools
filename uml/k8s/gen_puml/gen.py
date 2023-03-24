import os
import re
import subprocess
import omegaconf
from distutils import dir_util, file_util

PWD = os.path.abspath(os.path.dirname(__file__))
TEMP_MODULE = os.path.join(PWD, 'tmp')
PUML_COMMAND = ('goplantuml -recursive -hide-connections -show-implementations -show-compositions '
                '{options}  -ignore "{filter}" {module} > {path}')
PUML_COMBINE_COMMAND = ('goplantuml -hide-connections -show-implementations '
                        '-hide-methods -ignore "{filter}" {module} > {path}')
DEFINE_COMMAND = ('goplantuml {options}  -ignore "{filter}" {module} > {path}')


def run_command(command):
    cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    out, err = cmd.communicate()
    if cmd.returncode != 0:
        print(f'run {command} stdout: {out}')
        print(f'run {command} stderr: {err}')
    return cmd.returncode


class GoCodeHandler:
    def __init__(self):
        self.pattern_package = re.compile(r'package\s+([a-zA-Z0-9]+)')

    def rpl_pkg_dir(self, dir, package_replace):
        for root, dirs, files in os.walk(dir):
            for f in files:
                p = os.path.join(root, f)
                self.replace_package(p, package_replace)

    def replace_package(self, path, package_replace):
        """替换 pakcage 名称

        Returns:
            _type_: _description_
        """
        with open(path, 'r') as bf:
            content = bf.read()
        new_content = self.pattern_package.sub(
            f'package {package_replace}', content)
        with open(path, 'w') as cf:
            cf.write(new_content)


class PumlCodeHandler:
    def __init__(self):
        self.pattern_package = re.compile(r'package\s+([a-zA-Z0-9]+)')
        # self.packages = []

    def prepare(self, dir):
        packages = []
        for root, dirs, files in os.walk(dir):
            for f in files:
                p = os.path.join(root, f)
                package_name = self.extract_package(p)
                packages.append(package_name)
        return packages

    def extract_package(self, path):
        with open(path, 'r') as bf:
            content = bf.read()
        package_name = self.pattern_package.search(content).groups()[0]
        return package_name

    def handler_puml(self, path_puml, packages, pkg_rpl):
        """替换 puml 中的 package 名称

        Args:
            path_puml (_type_): _description_
            packages (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        if not packages:
            return
        with open(path_puml, 'r') as bf:
            content = bf.read()
        for i in packages:
            b1 = f'namespace {i}'
            r1 = f'namespace {pkg_rpl}'
            b2 = f'{i}.'
            r2 = f'{pkg_rpl}.'
            content = content.replace(b1, r1).replace(b2, r2)
        with open(path_puml, 'w') as cf:
            cf.write(content)


class GenPuml:
    def __init__(self) -> None:
        self.code_root = '/home/tao/code/github/'
        self.puml_config = omegaconf.OmegaConf.load(
            os.path.join(PWD, 'puml.yaml'))
        self.staging_code_path = os.path.join(
            self.code_root, 'kubernetes/staging/src/k8s.io')
        self.staging_puml_path = os.path.join(
            self.code_root, 'tools/uml/k8s/staging')
        self.conf_staging = self.get_staging_puml_conf()

        self.puml_handler = PumlCodeHandler()
        self.puml_handler_info = {}

    def get_staging_puml_conf(self):
        def _iter_conf(root, sub_conf):
            for m, c in sub_conf.items():
                sub_path = os.path.join(root, m)
                if m in ['filter', 'options']:
                    if root not in conf_map:
                        conf_map[root] = {}
                    if m == 'filter':
                        conf_map[root][m] = [os.path.join(root, i) for i in c]
                    if m == 'options':
                        conf_map[root][m] = c
                else:
                    _iter_conf(sub_path, c)

        conf_map = {}
        staging_config = self.puml_config['staging']
        _iter_conf('', staging_config)
        # print(conf_map)
        return conf_map

    def get_module_param(self, module):
        f = self.conf_staging[module].get('filter', [])
        o = self.conf_staging[module].get('options', '')
        puml_filter = ','.join(
            [os.path.join(self.staging_code_path, i) for i in f])
        puml_module = os.path.join(self.staging_code_path, module)
        puml_path = os.path.join(self.staging_puml_path, module)
        puml_dir = os.path.dirname(puml_path)
        if not os.path.exists(puml_dir):
            dir_util.mkpath(puml_dir)
        param = dict(filter=puml_filter, module=puml_module,
                     path=f'{puml_path}.puml', options=' '.join(o))
        return param

    def gen_pkg_command(self):
        """直接生成 pkg 下 package 的 puml

        Returns:
            _type_: _description_
        """
        collect = []
        conf_puml = self.conf_staging
        for d in conf_puml.keys():
            p = self.get_module_param(d)
            c = PUML_COMMAND.format(**p)
            collect.append(c)
            self.puml_handler_info[d] = {
                'path': p['path'],
                'packages': [],
                'command': c
            }
        return collect

    def gen_define_command(self):
        collect = []
        define = self.puml_config['define']
        collect = []
        # go_code_handler = GoCodeHandler()

        for i, ms in define.items():
            temp_module = os.path.join(TEMP_MODULE, i)
            if os.path.exists(temp_module):
                dir_util.remove_tree(temp_module)
            if not os.path.exists(temp_module):
                dir_util.mkpath(temp_module)
            for f in ms['includes']:
                t = os.path.join(self.staging_code_path, f)
                d = os.path.join(temp_module, os.path.basename(t))
                file_util.copy_file(src=t, dst=d)
            # go_code_handler.rpl_pkg_dir(temp_module, i)
            packages = self.puml_handler.prepare(temp_module)
            path = os.path.join(TEMP_MODULE, f'{i}.puml')
            p = {
                'filter': '',
                'module': ' '.join([temp_module]),
                'path': path,
                'options': ' '.join(ms.get('options', []))
            }
            c = DEFINE_COMMAND.format(**p)
            self.puml_handler_info[i] = {
                'path': path,
                'packages': packages,
                'command': c
            }
            collect.append(c)
        return collect

    def gen_combine_command(self):
        combine = self.puml_config['combine']
        collect = []
        for i, ms in combine.items():
            module_params = [self.get_module_param(m) for m in ms]
            path = os.path.join(os.path.dirname(
                module_params[0]['path']), f'{i}.puml')
            p = {
                'filter': ','.join([m['filter'] for m in module_params]),
                'module': ' '.join([m['module'] for m in module_params]),
                'path': path
            }
            c = PUML_COMBINE_COMMAND.format(**p)
            self.puml_handler_info[i] = {
                'path': p['path'],
                'packages': [],
                'command': c,
            }
            collect.append(c)
        return collect

    def gen_shell(self):
        path_shell = os.path.join(PWD, 'gen1.sh')
        commands = self.gen_pkg_command()
        combine = self.gen_combine_command()
        define = self.gen_define_command()
        with open(path_shell, 'w') as bf:
            for i in commands + combine + define:
                bf.write(i)
                bf.write('\n')

    def run_gen_puml(self):
        self.gen_pkg_command()
        self.gen_combine_command()
        self.gen_define_command()
        path_shell = os.path.join(PWD, 'gen1.sh')
        f = open(path_shell, 'w')
        for name, puml_info in self.puml_handler_info.items():
            command = puml_info['command']
            f.write(f'{command}\n')
            return_code = run_command(command)
            if return_code != 0:
                raise ValueError(command)
            self.puml_handler.handler_puml(
                puml_info['path'], puml_info['packages'], name)
        f.close()


def main():
    puml_obj = GenPuml()
    puml_obj.run_gen_puml()


if __name__ == '__main__':
    main()
