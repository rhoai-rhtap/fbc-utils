import yaml
import json
from collections import defaultdict
from jsonupdate_ng import jsonupdate_ng

yaml_path = '/home/dchouras/RHODS/DevOps/FBC/main/catalog/v4.13/rhods-operator/catalog.yaml'
objs = yaml.safe_load_all(open(yaml_path))
print(type(objs))
catalog_dict = defaultdict(dict)
for obj in objs:
    # print(obj)
    catalog_dict[obj['schema']][obj['name']] = obj

# print(json.dumps(catalog_dict, indent=4))

patch_yaml_path = '/home/dchouras/RHODS/DevOps/FBC/rhoai-2.13/catalog/catalog-patch.yaml'
patch_dict = yaml.safe_load(open(patch_yaml_path))

SCHEMA = 'olm.package'
patch = patch_dict['patch'][SCHEMA]
catalog_dict[SCHEMA][patch['name']] = jsonupdate_ng.updateJson(catalog_dict[SCHEMA][patch['name']], patch)
def str_presenter(dumper, data):
    if data.count('\n') > 0:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


docs = [doc for schema, schema_dict in catalog_dict.items() for name, doc in schema_dict.items()]
yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
yaml.safe_dump_all(docs, open('output.yaml', 'w'))




