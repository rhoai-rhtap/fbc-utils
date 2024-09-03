
from jsonupdate_ng import jsonupdate_ng
import argparse
import yaml
import json
from collections import defaultdict
class fbc_processor:
    def __init__(self, catalog_yaml_path:str, patch_yaml_path:str, single_bundle_path:str, output_catalog_path:str):
        self.catalog_yaml_path = catalog_yaml_path
        self.patch_yaml_path = patch_yaml_path
        self.single_bundle_path = single_bundle_path
        self.output_catalog_path = output_catalog_path
        self.catalog_dict:defaultdict = self.parse_catalog_yaml()
        self.patch_dict = self.parse_patch_yaml()

    def parse_catalog_yaml(self):
        objs = yaml.safe_load_all(open(self.catalog_yaml_path))
        print(type(objs))
        catalog_dict = defaultdict(dict)
        for obj in objs:
            catalog_dict[obj['schema']][obj['name']] = obj
        return catalog_dict

    def parse_patch_yaml(self):
        return yaml.safe_load(open(self.patch_yaml_path))
    def patch_catalog_yaml(self):
        if 'olm.package' in self.patch_dict['patch']:
            self.patch_olm_package()
        if 'olm.channels' in self.patch_dict['patch']:
            self.patch_olm_channels()

        self.write_output_catalog()

    def write_output_catalog(self):
        docs = [doc for schema, schema_val in self.catalog_dict.items() for name, doc in schema_val.items()]
        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
        yaml.safe_dump_all(docs, open(self.output_catalog_path, 'w'))


    def patch_olm_package(self):
        SCHEMA = 'olm.package'
        patch = self.patch_dict['patch'][SCHEMA]
        self.catalog_dict[SCHEMA][patch['name']] = jsonupdate_ng.updateJson(self.catalog_dict[SCHEMA][patch['name']], patch)


    def patch_olm_channels(self):
        SCHEMA = 'olm.channel'
        PATCH_SCHEMA = 'olm.channels'
        for channel in self.patch_dict['patch'][PATCH_SCHEMA]:
            if channel['name'] in self.catalog_dict[SCHEMA]:
                self.catalog_dict[SCHEMA][channel['name']] = jsonupdate_ng.updateJson(self.catalog_dict[SCHEMA][channel['name']], channel, meta={'listPatchScheme': {'$.entries': 'name'}})
            else:
                self.catalog_dict[SCHEMA][channel['name']] = channel

    def patch_olm_bundles(self):
        pass

def str_presenter(dumper, data):
    if data.count('\n') > 0:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--catalog-yaml-path', required=True,
    #                     help='Path of the catalog.yaml from the main branch.', dest='catalog_yaml_path')
    # parser.add_argument('--patch-yaml-path', required=True, help='Path of the catalog-patch.yaml from the release branch.', dest='patch_yaml_path')
    # parser.add_argument('--single-bundle-path', required=True,
    #                     help='Path of the single-bundle generated using the opm.', dest='single_bundle_path')
    # parser.add_argument('--output-catalog-path', required=True,
    #                     help='Path of the single-bundle generated using the opm.', dest='output_catalog_path')
    # args = parser.parse_args()
    # processor = fbc_processor(catalog_yaml_path=args.catalog_yaml_path, patch_yaml_path=args.patch_yaml_path, single_bundle_path=args.single_bundle_path, output_catalog_path=args.output_catalog_path)
    c = '/home/dchouras/RHODS/DevOps/FBC/main/catalog/v4.13/rhods-operator/catalog.yaml'
    p = '/home/dchouras/RHODS/DevOps/FBC/rhoai-2.13/catalog/catalog-patch.yaml'
    s = ''
    o = 'output.yaml'
    processor = fbc_processor(catalog_yaml_path=c, patch_yaml_path=p, single_bundle_path=s, output_catalog_path=o)
    processor.patch_catalog_yaml()
