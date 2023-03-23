import os
import omegaconf
from distutils import dir_util, file_util

PWD = os.path.abspath(os.path.dirname(__file__))
TEMP_MODULE = os.path.join(PWD, 'tmp')
PUML_COMMAND = ('goplantuml -recursive -hide-connections -show-implementations -show-compositions '
                '{options}  -ignore "{filter}" {module} > {path}')
PUML_COMBINE_COMMAND = ('goplantuml -hide-connections -show-implementations '
                        '-hide-methods -ignore "{filter}" {module} > {path}')


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
        print(conf_map)
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

    def gen_puml_command(self):
        collect = []
        conf_puml = self.conf_staging
        for d in conf_puml.keys():
            p = self.get_module_param(d)
            c = PUML_COMMAND.format(**p)
            collect.append(c)
        return collect

    def gen_define_command(self):
        collect = []
        define = self.puml_config['define']
        collect = []
        for i, ms in define.items():
            temp_module = os.path.join(TEMP_MODULE, i)
            if os.path.exists(temp_module):
                dir_util.remove_tree(temp_module)
            if not os.path.exists(temp_module):
                dir_util.mkpath(temp_module)
            for f in ms:
                t = os.path.join(self.staging_code_path, f)
                d = os.path.join(temp_module, os.path.basename(t))
                file_util.copy_file(src=t, dst=d)
            path = os.path.join(TEMP_MODULE, f'{i}.puml')
            p = {
                'filter': '',
                'module': ' '.join([temp_module]),
                'path': path,
                'options': ''
            }
            c = PUML_COMMAND.format(**p)
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
            collect.append(PUML_COMBINE_COMMAND.format(**p))
        return collect

    def gen_shell(self):
        path_shell = os.path.join(PWD, 'gen1.sh')
        commands = self.gen_puml_command()
        combine = self.gen_combine_command()
        define = self.gen_define_command()
        with open(path_shell, 'w') as bf:
            for i in commands + combine + define:
                bf.write(i)
                bf.write('\n')


def main():
    puml_obj = GenPuml()
    puml_obj.gen_shell()


if __name__ == '__main__':
    main()
