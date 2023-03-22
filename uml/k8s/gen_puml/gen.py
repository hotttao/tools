import os
import omegaconf
from distutils import dir_util

PWD = os.path.abspath(os.path.dirname(__file__))
PUML_COMMAND = ('goplantuml -recursive -hide-connections -show-implementations -show-compositions '
                '-hide-methods -ignore "{filter}" {module} > {path}')
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
                if 'filter' == m:
                    conf_map[root] = [os.path.join(root, i) for i in c]
                else:
                    _iter_conf(sub_path, c)

        conf_map = {}
        staging_config = self.puml_config['staging']
        _iter_conf('', staging_config)
        print(conf_map)
        return conf_map

    def get_module_param(self, module):
        f = self.conf_staging[module]
        puml_filter = ','.join(
            [os.path.join(self.staging_code_path, i) for i in f])
        puml_module = os.path.join(self.staging_code_path, module)
        puml_path = os.path.join(self.staging_puml_path, module)
        puml_dir = os.path.dirname(puml_path)
        if not os.path.exists(puml_dir):
            dir_util.mkpath(puml_dir)
        param = dict(filter=puml_filter, module=puml_module,
                     path=f'{puml_path}.puml')
        return param

    def gen_puml_command(self):
        collect = []
        conf_puml = self.conf_staging
        for d in conf_puml.keys():
            p = self.get_module_param(d)
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
        with open(path_shell, 'w') as bf:
            for i in commands + combine:
                bf.write(i)
                bf.write('\n')


def main():
    puml_obj = GenPuml()
    puml_obj.gen_shell()


if __name__ == '__main__':
    main()
