
from jsonupdate_ng import jsonupdate_ng
import argparse
import yaml
import json
from collections import defaultdict
class fbc_processor:
    def __init__(self, catalog_yaml_path:str, patch_yaml_path:str, single_bundle_path:str, output_file_path:str):
        self.catalog_yaml_path = catalog_yaml_path
        self.patch_yaml_path = patch_yaml_path
        self.single_bundle_path = single_bundle_path
        self.output_file_path = output_file_path
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
        if 'olm.package' in self.patch_dict:
            self.patch_olm_package()
        if 'olm.channels' in self.patch_dict:
            self.patch_olm_channels()


    def patch_olm_package(self):
        SCHEMA = 'olm.package'
        patch = self.patch_dict['patch'][SCHEMA]
        updatedJson = jsonupdate_ng.updateJson(json.dumps(self.catalog_dict[SCHEMA][patch['name']]), json.dumps(patch))


    def patch_olm_channels(self):
        pass

    def patch_olm_bundles(self):
        pass



if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--catalog-yaml-path', required=True,
    #                     help='Path of the catalog.yaml from the main branch.', dest='catalog_yaml_path')
    # parser.add_argument('--patch-yaml-path', required=True, help='Path of the catalog-patch.yaml from the release branch.', dest='patch_yaml_path')
    # parser.add_argument('--single-bundle-path', required=False, default='',
    #                     help='Path of the single-bundle generated using the opm.', dest='single_bundle_path')
    # args = parser.parse_args()
    # processor = fbc_processor(catalog_yaml_path=args.catalog_yaml_path, patch_yaml_path=args.patch_yaml_path, single_bundle_path=args.single_bundle_path)
    c = '/home/dchouras/RHODS/DevOps/FBC/main/catalog/v4.13/rhods-operator/catalog.yaml'
    p = '/home/dchouras/RHODS/DevOps/FBC/rhoai-2.13/catalog/catalog-patch.yaml'
    s = ''
    o = '/home/dchouras/RHODS/DevOps/FBC/rhoai-2.13/catalog/v4.13/rhods-operator/catalog.yaml'
    processor = fbc_processor(catalog_yaml_path=c, patch_yaml_path=p, single_bundle_path=s, output_file_path=o)
