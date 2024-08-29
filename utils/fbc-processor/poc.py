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

patch_yaml_path = '/home/dchouras/RHODS/DevOps/FBC/rhoai-2.13/catalog/catalog-patch.yaml'
patch_dict = yaml.safe_load(open(patch_yaml_path))

SCHEMA = 'olm.package'
patch = patch_dict['patch'][SCHEMA]
updatedJson = jsonupdate_ng.updateJson(json.dumps(catalog_dict[SCHEMA][patch['name']]), json.dumps(patch))
print(updatedJson)




