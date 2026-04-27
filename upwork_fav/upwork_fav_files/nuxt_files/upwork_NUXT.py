# ===== CLEAN VERSION (CI SAFE) =====

import json
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Increase recursion limit for deeply nested structures
sys.setrecursionlimit(2000)

def dereference(item, data_list, memo):
    if isinstance(item, int) and 0 <= item < len(data_list):
        item = data_list[item]

    if isinstance(item, (dict, list)):
        if id(item) in memo:
            return memo[id(item)]

        if isinstance(item, dict):
            new_obj = {}
            memo[id(item)] = new_obj
            for key, value in item.items():
                new_obj[key] = dereference(value, data_list, memo)
            return new_obj

        elif isinstance(item, list):
            new_obj = []
            memo[id(item)] = new_obj
            for element in item:
                new_obj.append(dereference(element, data_list, memo))
            return new_obj

    return item


def map_data(raw_data):
    try:
        if not isinstance(raw_data, list) or len(raw_data) < 2:
            raise ValueError("Invalid input data")

        return dereference(raw_data[1], raw_data, {})

    except Exception as e:
        print(f"❌ Mapping error: {e}")
        return None


def NUXT_function(driver):
    try:
        wait = WebDriverWait(driver, 15)
        script_tag = wait.until(
            EC.presence_of_element_located((By.ID, '__NUXT_DATA__'))
        )
        json_string = script_tag.get_attribute('innerHTML')
        data = json.loads(json_string)

        return map_data(data)

    except Exception as e:
        print(f"❌ NUXT error: {e}")
        return None