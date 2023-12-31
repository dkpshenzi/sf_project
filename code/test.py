import requests
from uuid import uuid4
import time
import os
import Astar
import Distribution
import PathTrack
import CBS
import judge
import MapCreate

# SERVER_URL  = os.environ.get("sf-judge-server") or "http://127.0.0.1:5555"
USERNAME = "算法挑战赛-AI平台"
# SUBMISSION_ID = str(uuid4())

# api设置
GAMELOAD = 'create_submission'
MAPSTART = 'start'
AGVCONTROL = 'step'
GAMEEND = 'finish_submission'

# 判题器
JUDGE = judge.Judge()

# 类的设置
class AGV:
    def __init__(self,agvid,payload,cap,position):
        self.id = agvid # id
        self.payload = payload # 负载
        self.cap = cap    # 容积
        self.position = position
        self.target = None
        self.path = []
    def update(self,payload,cap,position):
        self.payload = payload
        self.cap = cap
        self.position = position

def command(api,value={}):
    data = JUDGE.output(api,value)
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
    map_detail = map_state["maps"]   # 地图位置信息  # x,y,type,id
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
        new_cargos.append(cargo)
        cargo_id = cargo['id']
        cargo_target = cargo['target']
        # cargo_weight = cargo['weight']
        if 'x' not in cargo.keys():
            cargo['x'] = None    
            cargo['y'] = None
            cargo_position = (cargo['x'],cargo['y'])
            print(f"货物编号：{cargo_id}，目标：{cargo_target}，重量：1，位置：{cargo_position}")
    
    for shelf in shelves:
        shelf_id = shelf['id']
        shelf_cap = None
        shelf_payload = shelf['payload']
        shelf_position = (shelf['x'],shelf['y'])
        print(f"货架编号：{shelf_id}，cap：{shelf_cap}，负载：{shelf_payload}，位置：{shelf_position}")
    
    print()
    
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
        mapdata = command(MAPSTART)
        # 不仅仅得到地图的数据，第一次读取地图数据还会得到机器人的类列表
        map_attr,agvs,cargos,shelves,walls = sort_map_data(mapdata,True)    # 这里是第一次读取地图的数据
        
        # 得到长和宽
        rows = map_attr['height']
        cols = map_attr['width']
        
        # 初始化地图
        map_grid = MapCreate.MapCreate(rows,cols,shelves,walls)
        
        # 处理地图数据
        # 包括规划路线
        # agvs: id,payload,cap,(x,y),(target1,target2)
        # 这里是传入AGV_li 列表，然后改变AGV_li列表中的AGV目标
        dis = Distribution.Distribution(cargos,shelves)
        # 更新数据，并且进行目标的寻找
        dis.update(AGV_li,cargos,shelves)
        AGV_li,is_change_path = dis.target_finding()
        
        # print(f'是否更新了目标：{is_change_path}')
        
        # 这里是通过AGV列表中的AGV类的目标进行路径规划，总共规划两条路线
        # 得到每个机器人的一个路线
        # 首先循环每个机器人的目标
        # 这里只能够先完成第一阶段的一个寻路
        cbs = CBS.CBS(AGV_li,shelves,cargos,map_grid)
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
                if c['type'] == 'DELIVERY' or c['type'] == 'PICKUP':
                    agv.target.pop(0)
                    agv.path = []
                command_li.append(c)
            
            # print(command_li)
            
            # 开始输出指令
            data = command(AGVCONTROL,command_li)
            
            # sort_map_data(data,False)
            
            # 判断是否已经完成地图
            try:
                if data["value"]["done"] or step > 100:
                    break
            except:
                print(f'数据为：{data}')
            
            # 首先进行数据的更新
            agvs,cargos,shelves = sort_map_data(data,False)
            for index,agv in enumerate(agvs):
                a = AGV_li[index]
                a.update(agv['payload'],agv['cap'],(agv['x'],agv['y']))
            
            # 完成后进行目标的重新选择
            dis.update(AGV_li,cargos,shelves)
            # print(f'cargos:{cargos}')
            # print(f'shelves:{shelves}')
            AGV_li,is_change_path = dis.target_finding()

            for agv in AGV_li:
                print(f'当前目标为：{agv.target}')
                print(f'当前路径为：',end='')
                for node in agv.path:
                    print(f'{node.position}',end='')
                print()
            
            # 如果目标发生了改变，则需要重新规划
            # 这个时候再进行一次路径规划，只进行货物到货柜的路径规划
            if is_change_path:
                cbs = CBS.CBS(AGV_li,shelves,cargos,map_grid)
                AGV_li = cbs.solve()
            
            # print(f'完成了一次规划')
            
            step += 1
    
    # 输入结束指令
    data = command(GAMEEND)