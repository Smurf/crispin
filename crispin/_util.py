import logging
import sys

logger = logging.getLogger(__name__)
default_level = logging.WARNING
logger.level = default_level

def set_log_level(logging_level):
    # For some reason setting the level in basicConfig fails?
    logging.getLogger(__name__).level = logging_level

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stdout)],
    )

def dict_to_dot(d, parent_key=''):
    """
    This function takes a dict and converts it into a dot notation like jinja2 uses.
    This function **ONLY** returns keys, no values.
    """
    items = []
    sep = '.'
    for k, v in d.items():
        # Current key we're iterating through
        if parent_key:
            c_key = f"{parent_key}{sep}{k}"
        else:
            c_key = k
        # Recurse if current value is a dict
        if isinstance(v, dict):
            items.append(c_key)
            items.extend(dict_to_dot(v, c_key))
        else:
            items.append(c_key)
    return items

def dot_to_dict(d_list, parent={}):
    res = parent

    for item in d_list:
        keys = item.split('.')
        c_res = res

        # For each dot we decend down creating a new dict each time
        # c_res is pointer to current dict, this builds the nested dicts
        # by moving the c_res pointer for each dot in the string
        for sub_key in keys[:-1]: # Ensure that the last value is not treated as a dict by trimming with :-1
            if sub_key not in c_res:
                c_res[sub_key] = {}
            c_res = c_res[sub_key] # Move down the dict structure for the next iteration

        # keys[-1] == the final value after the last ., set this to empty
        # BUT only if the key does not already exist in our current dict!
        if keys[-1] not in c_res and isinstance(c_res, dict):
            c_res[keys[-1]] = ""
    return res
