import requests
from uuid import uuid4
import time
import os
import Astar
#nothing
SERVER_URL  = os.environ.get("sf-judge-server") or "http://127.0.0.1:5555"
USERNAME = "算法挑战赛-AI平台"
SUBMISSION_ID = str(uuid4())

# 事例指令
ACTIONS_SEQ = [
    [{"type":"PICKUP","dir":"RIGHT"},{"type":"PICKUP","dir":"LEFT"}],
    [{"type":"MOVE","dir":"RIGHT"},{"type":"MOVE","dir":"LEFT"}],
    [{"type":"MOVE","dir":"RIGHT"},{"type":"MOVE","dir":"LEFT"}],
    [{"type":"MOVE","dir":"RIGHT"},{"type":"STAY"}],
    [{"type":"MOVE","dir":"UP"},{"type":"STAY"}],
    [{"type":"STAY"},{"type":"MOVE","dir":"LEFT"}],
    [{"type":"STAY"},{"type":"MOVE","dir":"LEFT"}],
    [{"type":"MOVE","dir":"DOWN"},{"type":"MOVE","dir":"LEFT"}],
    [{"type":"MOVE","dir":"RIGHT"},{"type":"MOVE","dir":"LEFT"}],
    [{"type":"MOVE","dir":"RIGHT"},{"type":"DELIVERY","dir":"LEFT"}],
    [{"type":"MOVE","dir":"RIGHT"},{"type":"STAY"}],
    [{"type":"DELIVERY","dir":"RIGHT"},{"type":"STAY"}]
]

# api设置
GAMELOAD = 'create_submission'
MAPSTART = 'start'
AGVCONTROL = 'step'
GAMEEND = 'finish_submission'

def command(api,value={}):
    resp = requests.post(f"{SERVER_URL}/{api}",json=value)
    assert (resp.status_code == 200)
    data = resp.json()
    # print (data)
    return data

# 处理并提取地图数据，再进行输出
def sort_map_data(mapdata):
    """用于整理地图数据，输出到控制台
    arr:
        mapdata: 传入的地图字典数据
        
    return:
        map_attr: 地图元数据，宽，高，最大步数，单词决策最大时间
        agvs: 机器人字典列表：id,payload,cap,position
        cargos: 货物字典列表：id,target,weight,position
        shelves: 货架字典列表：id,cap,payload,position
        wall: 墙壁字典列表：x,y
    """
    # 处理并提取地图数据，再进行输出
    value = mapdata["value"]
    map_attr = value["map_attr"]    # 地图元信息 # 宽，高，最大步数，单次决策最大时间
    
    map_state = value["map_state"]  # 地图状态
    agvs = map_state["agvs"]    # 机器人状态    # id,payload负载,cap
    cargos = map_state["cargos"]    # 货物状态  # id,target目的地货架,weight
    shelves = map_state["shelves"]  # 货架状态  # id,cap,payload
    map_detail = map_state["map"]   # 地图位置信息  # x,y,type,id
    # type: agvs shelf wall cargo
    walls = []   # 添加一个障碍物的列表
    
    width = map_attr['width']
    height = map_attr['height']        
    print(f'地图宽为{width}，高为{height}')
    
    # 先给所有物品的条目上坐标
    for position in map_detail:
        ty = position['type']
        if ty == 'agv':
            agvs[position['id']]['x'] = position['x']
            agvs[position['id']]['y'] = position['y']
        elif ty == 'cargo':
            cargos[position['id']]['x'] = position['x']
            cargos[position['id']]['y'] = position['y']
        elif ty == 'shelf':
            shelves[position['id']]['x'] = position['x']
            shelves[position['id']]['y'] = position['y']
        elif ty == 'wall':
            wall = {"x":position['x'],'y':position['y']}
            walls.append(wall)
    
    # 然后再逐个提取信息
    for agv in agvs:
        agv_id = agv['id']
        agv_payload = agv['payload']
        agv_cap = agv['cap']
        agv_position = (agv['x'],agv['y'])
        print(f'机器人编号：{agv_id}，负载：{agv_payload}，cap：{agv_cap}，位置：{agv_position}')
    
    for cargo in cargos:
        cargo_id = cargo['id']
        cargo_target = cargo['target']
        cargo_weight = cargo['weight']
        cargo_position = (cargo['x'],cargo['y'])
        print(f"货物编号：{cargo_id}，目标：{cargo_target}，重量：{cargo_weight}，位置：{cargo_position}")
    
    for shelf in shelves:
        shelf_id = shelf['id']
        shelf_cap = shelf['cap']
        shelf_payload = shelf['payload']
        shelf_position = (shelf['x'],shelf['y'])
        print(f"货架编号：{shelf_id}，cap：{shelf_cap}，负载：{shelf_payload}，位置：{shelf_position}")
        
    return map_attr,agvs,cargos,shelves,walls
        
if __name__ == "__main__":
    # 通过对网站发送post命令来获取信息
    # 初始化接受地图数据
    # 获得地图id列表,maps:[]
    data = command(GAMELOAD)

    # 每个地图展开
    for map_id in data['value']['maps']:
        # 指定一个地图然后开始比赛
        # 获得地图数据
        # 这个是刚刚开始的数据
        mapdata = command(MAPSTART,{"map_id":map_id})
        map_attr,agvs,cargos,shelves,walls = sort_map_data(mapdata)
        
        # 处理地图数据
        # 包括规划路线
        
        
        # 输入指令部分
        # 输入指令，每个指令输入完成后都会有一个新的回应，同时指令可以同时下达给四个机器人
        # 同时这里也需要判断什么时候完成
        for actions in ACTIONS_SEQ:
            try:
                print('actions:', actions)
                # 输入指令部分
                data = command(AGVCONTROL,{"map_id": map_id,"actions": actions})
                if data["value"]["done"]:
                    print ('done:', data["value"]["done"])
                    break
            except AssertionError:
                print("assert error occur")
                break
    
    # 输入结束指令
    data = command(GAMEEND)