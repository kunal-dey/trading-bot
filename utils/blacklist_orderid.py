import json

BLACKLISTED_IDS:dict[str,list] ={
    "ids":[]
}

def get_blacklisted_order_id():
    global BLACKLISTED_IDS
    with open("temp/blacklist_ids.json") as file:
        try:
            BLACKLISTED_IDS = json.load(file)
        except:
            pass
    return BLACKLISTED_IDS

def add_blacklisted_order_id(order_id:str):
    global BLACKLISTED_IDS
    BLACKLISTED_IDS["ids"].append(order_id)
    with open("temp/blacklist_ids.json", 'w') as file:
        data = json.dumps(BLACKLISTED_IDS)
        file.write(data)