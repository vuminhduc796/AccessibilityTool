import yaml
with open('./config/config.yml', 'r') as config:
    config_content = yaml.safe_load(config)