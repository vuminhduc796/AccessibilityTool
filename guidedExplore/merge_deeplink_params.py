import json
import os

class ParamGenerator:
    intent_paras = {}
    params_types = ['getStringExtra', 'getExtras', 'getIntExtra', 'getBooleanExtra', 'getDoubleExtra', 'getLongExtra', 'getData']
    params_default_values = ['string', 'extras_string', 1, True, 1.1, 2, 'getData']
    params_adb_command = ['--es', '--es', '--ei', '--ez', '--ef', '--el', '--es']
    replace_char_list = [' ']

    def __init__(self, para_json):
        with open(para_json, 'r', encoding='utf8') as f:
            self.intent_paras = json.loads(f.read())

    def get_paras_by_pkg_activity(self, activity, assign_value=True):
        activities = self.intent_paras
        if activities is None:
            return None
        else:
            activity_paras = activities.get(activity, None)
            if activity_paras is None:
                return None
            else:
                return activity_paras

    def assign_default_value2params(self, params):
        results = []
        for i in params:
            key = i[0]
            if key == '' or key == ' ':
                continue
            key = str(key).replace(' ', '\\ ')
            value_type = i[1]
            value = 'other'
            cmd = '--es extra_key other'
            if value_type in self.params_types:
                index = self.params_types.index(value_type)
                value = self.params_default_values[index]
                cmd = self.params_adb_command[index]
                results.append(' '.join([cmd, key, str(value)]))
            else:
                results.append(cmd)

        return results

    def merge_deeplinks_params(self, deeplink_json,
                               merged_path=r'data/deeplinks_params.json'):
        params = 'params'
        if os.stat(deeplink_json).st_size != 0:
            with open(deeplink_json, 'r', encoding='utf8') as f:

                activities = json.loads(f.read())
                for activity in activities.keys():
                    params_list = self.get_paras_by_pkg_activity(activity)

                    if params_list is not None:
                        param_dict = {}
                        for param in params_list:

                            key = param[0]
                            type = param[1]
                            if type == "getExtras":
                                if "extra_keys" in param_dict.keys():
                                    param_dict["extra_keys"] = [key]
                                else:
                                    param_dict.get("extra_keys").append(key)
                            elif type == "getStringExtra":
                                param_dict = mapKey(param_dict, "extra_string", "string", key)
                            elif type == "getBooleanExtra":
                                param_dict = mapKey(param_dict, "extra_boolean", "true", key)
                            elif type == "getIntArrayExtra":
                                param_dict = mapKey(param_dict, "extra_array_int", [1,2,3], key)
                            elif type == "getLongArrayExtra":
                                param_dict = mapKey(param_dict, "extra_array_long", [1,2,3], key)
                            elif type == "getFloatArrayExtra":
                                param_dict = mapKey(param_dict, "extra_array_float", [1,2,3], key)
                            elif type == "getComponent":
                                param_dict = mapKey(param_dict, "extra_component", "component", key)
                            elif type == "getExtraUri":
                                param_dict = mapKey(param_dict, "extra_uri", "component", key)
                            elif type == "getIntExtra":
                                param_dict = mapKey(param_dict, "extra_int", 1, key)
                            elif type == "getFloatExtra":
                                param_dict = mapKey(param_dict, "extra_float", 1, key)
                            elif type == "getLongExtra":
                                param_dict = mapKey(param_dict, "extra_long", 1, key)
                        print("Dsd")
                        print(param_dict)
                        for key, value in param_dict.items():
                            for component in activities[activity]:
                                component[key] = value
                        #activities.get(activity).get(params).extend(params_list)
            with open(merged_path, 'w', encoding='utf8') as save:
                json.dump(activities, save, indent=4)

def mapKey(param_dict, type, hardCodedValue, key):
    if type not in param_dict.keys():
        param_dict[type] = [{key: hardCodedValue}]
    else:
        param_dict.get(type).append({key: hardCodedValue})
    return param_dict

if __name__ == '__main__':
    pass
    # current_directory = os.path.join(os.getcwd(), "guidedExplore/data")
    # merged_path = os.path.join( current_directory, app_name, 'deeplinks_params.json')
    # deeplinks_path = os.path.join( current_directory, app_name, 'deeplinks.json')
    # params_path = r'data/intent_para.json'
    # params = ParamGenerator(params_path)
    # deeplinks_json = r'data/deeplinks.json'
    # params.merge_deeplinks_params(deeplinks_json)