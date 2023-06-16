import requests
from uuid import uuid4
import time
import os
import Astar
import Distribution
import PathTrack
import CBS

SERVER_URL  = os.environ.get("sf-judge-server") or "http://127.0.0.1:5555"
USERNAME = "算法挑战赛-AI平台"
SUBMISSION_ID = str(uuid4())

# 事例指令
'''ACTIONS_SEQ = [
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
]'''

# api设置
GAMELOAD = 'create_submission'
MAPSTART = 'start'
AGVCONTROL = 'step'
GAMEEND = 'finish_submission'

# 类的设置
class AGV:
    def __init__(self,agvid,payload,cap,position):
        self.id = agvid # id
        self.payload = payload # 负载
        self.cap = cap    # 容积
        self.position = position
        self.target = []
        self.path = []
    def update(self,payload,cap,position):
        self.payload = payload
        self.cap = cap
        self.position = position

def command(api,value={}):
    resp = requests.post(f"{SERVER_URL}/{api}",json=value)
    # assert (resp.status_code == 200)
    data = resp.json()
    # print (data)
    return data

# 处理并提取地图数据，再进行输出
def sort_map_data(mapdata,is_first):
    """用于整理地图数据，输出到控制台
    arr:
        mapdata: 传入的地图字典数据
        is_first: 是否是第一次读取地图数据
        
    return:
        map_attr: 地图元数据，宽，高，最大步数，单词决策最大时间
        agvs: 机器人字典列表：id,payload,cap,position
        cargos: 货物字典列表：id,target,weight,position
        shelves: 货架字典列表：id,cap,payload,position
        wall: 墙壁字典列表：x,y
    """
    # 处理并提取地图数据，再进行输出
    value = mapdata["value"]
    if is_first:
        map_attr = value["map_attr"]    # 地图元信息 # 宽，高，最大步数，单次决策最大时间
        width = map_attr['width']
        height = map_attr['height']        
        print(f'地图宽为{width}，高为{height}')
    
    map_state = value["map_state"]  # 地图状态
    agvs = map_state["agvs"]    # 机器人状态    # id,payload负载,cap
    cargos = map_state["cargos"]    # 货物状态  # id,target目的地货架,weight
    shelves = map_state["shelves"]  # 货架状态  # id,cap,payload
    map_detail = map_state["map"]   # 地图位置信息  # x,y,type,id
    # type: agvs shelf wall cargo
    walls = []   # 添加一个障碍物的列表
    
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
        if is_first:
            new_agv = AGV(agv_id,agv_payload,agv_cap,agv_position)
            AGV_li.append(new_agv)
        print(f'机器人编号：{agv_id}，负载：{agv_payload}，cap：{agv_cap}，位置：{agv_position}')
    
    new_cargos = []
    for cargo in cargos:
        # 先判断是否存在坐标，若无坐标则去除
        if 'x' in cargo.keys():
            new_cargos.append(cargo)
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
    
    for wall in walls:
        x = wall['x']
        y = wall['y']
        position = (x,y)
        # print(f'障碍物：{position}')
    
    if is_first:
        return map_attr,agvs,new_cargos,shelves,walls
    else:
        # print(cargos)
        return agvs,new_cargos,shelves
        
if __name__ == "__main__":
    # 通过对网站发送post命令来获取信息
    # 初始化接受地图数据
    # 获得地图id列表,maps:[]
    data = command(GAMELOAD)

    # 每个地图展开
    for map_id in data['value']['maps']:
        print(f'当前地图为：{map_id}')
        
        # 每张地图开始初始化机器人列表
        AGV_li = []
        
        # 指定一个地图然后开始比赛
        # 获得地图数据
        # 这个是刚刚开始的数据
        mapdata = command(MAPSTART,{"map_id":map_id})
        # 不仅仅得到地图的数据，第一次读取地图数据还会得到机器人的类列表
        map_attr,agvs,cargos,shelves,walls = sort_map_data(mapdata,True)    # 这里是第一次读取地图的数据
        
        # 得到长和宽
        rows = map_attr['height']
        cols = map_attr['width']
        
        # 处理地图数据
        # 包括规划路线
        # agvs: id,payload,cap,(x,y),(target1,target2)
        # 这里是传入AGV_li 列表，然后改变AGV_li列表中的AGV目标
        dis = Distribution.Distribution(AGV_li,cargos,shelves)
        AGV_li = dis.target_finding()
        
        # 这里是通过AGV列表中的AGV类的目标进行路径规划，总共规划两条路线
        # 得到每个机器人的一个路线
        # 首先循环每个机器人的目标
        # 这里只能够先完成第一阶段的一个寻路
        cbs = CBS.CBS(rows,cols,AGV_li,shelves,cargos,walls)
        AGV_li = cbs.solve()
            
        # 初始化步数
        step = 0
            
        while True:
            # 指令列表
            command_li = []
            
            # 一张地图内，指令的输出
            # 首先输出指令，然后获取是否抵达目的地
            for agv in AGV_li:
                pathTrack = PathTrack.PathTrack(agv)
                c = pathTrack.path_tracking()
                command_li.append(c)
            
            print(command_li)
            
            # 开始输出指令
            data = command(AGVCONTROL,{"map_id": map_id,"actions": command_li})
            
            # sort_map_data(data,False)
            
            # 判断是否已经完成地图
            if data["value"]["done"] or step > 20:
                break
            
            # 首先进行数据的更新
            agvs,cargos,shelves = sort_map_data(data,False)
            for index,agv in enumerate(agvs):
                a = AGV_li[index]
                a.update(agv['payload'],agv['cap'],(agv['x'],agv['y']))
            
            # 这个时候再进行一次路径规划，只进行货物到货柜的路径规划
            cbs = CBS.CBS(rows,cols,AGV_li,shelves,cargos,walls)
            AGV_li = cbs.solve()
            
            print(f'完成了一次规划')
            # raise NameError()
            
            step += 1
    
    # 输入结束指令
    data = command(GAMEEND)