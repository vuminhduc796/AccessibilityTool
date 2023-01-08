import os
import shutil
import json
from os import path

current_directory = os.getcwd().replace("/apkExplore", "")
config_file_name = current_directory + "/output/config.json"


def sync_front_end_data():
    src_path = current_directory + '/output'
    dst_path = current_directory + '/frontend/src/data'
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    shutil.copytree(src_path, dst_path)


def create_config_front_end_file():
    json_initial_data = {
        "configs": []
    }
    json_object = json.dumps({}, indent=4)
    with open(config_file_name, "w") as outfile:
        outfile.write(json_object)


def get_list_of_configs():
    list_configs = []
    if path.isfile(config_file_name) is False:
        create_config_front_end_file()
    with open(config_file_name) as fp:
        data = json.load(fp)
        if "configs" in data:
            list_configs = data["configs"]
            print(list_configs)

    return list_configs


def write_config_file(list_configs):
    with open(config_file_name, 'w') as json_file:
        json.dump({
            "configs": list_configs
        }, json_file,
            indent=4,
            separators=(',', ': '))


def add_new_config(app_name, device, mode):
    new_config = {
        "config": {
            "isLoading": "yes",
            "isDone": "no",
            "appName": app_name,
            "device": device,
            "mode": mode,
            "activities": [],
            "nodes": [],
            "edges": []
        }
    }

    list_configs = get_list_of_configs()
    is_new_config = True
    for config in list_configs:
        current_config = config["config"]
        if current_config["appName"] == app_name and current_config["device"] == device and current_config[
            "mode"] == mode:
            is_new_config = False
            break
    if is_new_config:
        list_configs.append(new_config)
        write_config_file(list_configs)


def add_new_activity_to_config(app_name, device, mode, activity_name):
    list_configs = get_list_of_configs()
    for config in list_configs:
        current_config = config["config"]
        print(current_config)
        if current_config["appName"] == app_name and current_config["device"] == device and current_config[
            "mode"] == mode:
            current_config["activities"].append(activity_name)

    print(list_configs)
    write_config_file(list_configs)


def add_new_node_to_config(app_name, device, mode, node):
    add_new_config(app_name,device,mode)
    list_configs = get_list_of_configs()
    for config in list_configs:
        current_config = config["config"]
        print(current_config)
        if current_config["appName"] == app_name and current_config["device"] == device and current_config[
            "mode"] == mode:
            current_config["nodes"].append(node.nodeActivityName)

    print(list_configs)
    write_config_file(list_configs)


def add_new_edge_to_config(app_name, device, mode, edge):
    add_new_config(app_name,device,mode)
    list_configs = get_list_of_configs()
    for config in list_configs:
        current_config = config["config"]
        print(current_config)
        if current_config["appName"] == app_name and current_config["device"] == device and current_config[
            "mode"] == mode:
            current_config["edges"].append({
                "source": edge.src,
                "destination": edge.dest
            })

    print(list_configs)
    write_config_file(list_configs)
