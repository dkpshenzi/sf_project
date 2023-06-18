import requests
from uuid import uuid4
import os
import Distribution
import PathTrack
import CBS
import MapCreate
from PrintControl import PrintControl

SERVER_URL  = os.environ.get("sf-judge-server") or "http://127.0.0.1:5555"
USERNAME = "算法挑战赛-AI平台"
SUBMISSION_ID = str(uuid4())

# api设置
GAMELOAD = 'create_submission'
MAPSTART = 'start'
AGVCONTROL = 'step'
GAMEEND = 'finish_submission'

# 常量的设置
class PRINT:
    MAPINFO = 'map_information'     # 信息数据
    LOG = 'log'                     # 日志
    ERROR = 'error'                 # 错误

# 类的设置
class AGV:
    def __init__(self,agvid):
        self.id = agvid
        self.payload = None
        self.position = ()
        self.target = []
        self.path = []
    def update(self,payload):
        """更新数据

        Args:
            payload (_type_): 负载
            position (_type_): 坐标
        """
        self.payload = payload

class CARGO:
    def __init__(self,target):
        self.position = ()
        self.target = target
        
class SHELF:
    def __init__(self,index):
        self.position = ()
        self.index = index
        self.payload = None
    def update(self,payload):
        """更新数据

        Args:
            payload (_type_): 负载值
        """
        self.payload = payload
        
class WALL:
    def __init__(self,position):
        self.position = position

class MAP:
    def __init__(self):
        self.rows = None
        self.cols = None
        self.agvs = []
        self.cargos = []
        self.shelves = []
        self.walls = []
        
        self.map_grid = None    # 地图创建实例
        self.dis = None         # 地图创建实例  
    def set_arr(self,width,height):
        """设置行数和列数

        Args:
            rows (_type_): _description_
            cols (_type_): _description_
        """
        self.rows = height  # 行对应高
        self.cols = width   # 列对应宽
    def set_instance(self,walls,agvs,cargos,shelves):
        self.walls = walls
        self.agvs = agvs
        self.cargos = cargos
        self.shelves = shelves
    def get_map_grid(self):
        self.map_grid = MapCreate.MapCreate(self.rows,self.cols,self.shelves,self.walls)
    def get_dis(self):
        self.dis = Distribution.Distribution(self.cargos,self.shelves)
    def find_target(self):
        self.dis.update(self.agvs,self.cargos,self.shelves)
        self.agvs = self.dis.target_finding()
    
def command(api,value={}):
    resp = requests.post(f"{SERVER_URL}/{api}",json=value)
    assert (resp.status_code == 200)
    data = resp.json()
    return data

# 处理并提取地图数据，再进行输出
def sort_map_data(map_instance,mapdata,is_first):
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
    # 将全部处理过的数据制作成实例的列表

    value = mapdata["value"]
    map_state = value["map_state"]  # 地图状态
    map_attr = value["map_attr"]    # 地图元信息
    agvs = map_state["agvs"]    # 机器人状态    # id,payload负载,cap
    cargos = map_state["cargos"]    # 货物状态  # id,target目的地货架,weight
    shelves = map_state["shelves"]  # 货架状态  # id,cap,payload
    map_detail = map_state["map"]   # 地图位置信息  # x,y,type,id
    
    if is_first:
        # 地图自带的信息
        width = map_attr['width']
        height = map_attr['height']        
        pc.print(f'地图宽为{width}，高为{height}')
        
        # 障碍物
        walls = []
        for position in map_detail:
            ty == position['type']
            if ty == 'wall':
                x = position['x']
                y = position['y']
                wall = WALL((x,y))
                walls.append(wall)
                
        # 机器人实例化
        agv_li = []
        for agv in agvs:
            agv_id = agv['id']
            new_agv = AGV(agv_id)
            agv_li.append(new_agv)
            
        # 货物实例化
        cargos_li = []
        for cargo in cargos:
            cargo_target = cargo['target']
            new_cargo = CARGO(cargo_target)
            cargos_li.append(new_cargo)
        
        # 货柜实例化
        shelves_li = []
        for shelf in shelves:
            shelf_id = shelf['id']
            new_shelf = SHELF(shelf_id)
            shelves_li.append(new_shelf)
        
        map_instance.set_arr(width,height)  # 设置地图宽和高信息
        map_instance.set_instance(walls,agv_li,cargos_li,shelves_li)       # 设置地图的实例
    
    # 先给所有物品的条目上坐标
    for position in map_detail:
        ty = position['type']
        if ty == 'agv':
            index = position['id']
            map_instance.agvs[index].position = (position['x'],position['y'] )
        elif ty == 'cargo':
            index = position['id']
            map_instance.cargos[index].position = (position['x'],position['y'] )
        elif ty == 'shelf':
            index = position['id']
            map_instance.shelves[index].position = (position['x'],position['y'] )
    
    # 然后再逐个提取信息
    for agv in agvs:
        index = agv['id']
        agv_payload = agv['payload']
        map_instance.agvs[index].update(agv_payload)
    
    for shelf in shelves:
        index = shelf['id']
        shelf_payload = shelf['payload']
        map_instance.shelves[index].update(shelf_payload)
        
    return map_instance
        
if __name__ == "__main__":
    # 获得地图id列表,maps:[]
    data = command(GAMELOAD)
    
    # 实例化打印控制器
    pc = PrintControl()

    # 每个地图展开
    for map_id in data['value']['maps']:
        pc.print(f'当前地图为：{map_id}',PRINT.MAPINFO)
        
        # 实例化当前地图
        MA = MAP()
        
        # 指定一个地图然后开始比赛
        mapdata = command(MAPSTART,{"map_id":map_id})
        
        # 第一次读取地图数据
        MA = sort_map_data(MA,mapdata,True)    
        
        # 初始化地图
        MA.get_map_grid()
        
        # 规划目标
        MA.get_dis()
        # 分配目标
        MA.find_target()

        # 找路径
        cbs = CBS.CBS(MA.agvs,MA.map_grid)
        MA.agvs = cbs.solve()
            
        # 初始化步数
        step = 0
            
        while True:
            # 指令列表
            command_li = []
            
            # 一张地图内，指令的输出
            for agv in MA.agvs:
                pathTrack = PathTrack.PathTrack(agv)
                c = pathTrack.path_tracking()
                if c['type'] == 'DELIVERY':
                    agv.target = []
                    agv.path = []
                command_li.append(c)
            
            # 开始输出指令
            data = command(AGVCONTROL,{"map_id": map_id,"actions": command_li})
            
            # 判断是否已经完成地图
            try:
                if data["value"]["done"] or step > 30:
                    break
            except:
                pc.print(f'数据为：{data}',PRINT.ERROR)
            
            # 首先进行数据的更新
            MA = sort_map_data(MA,mapdata,False) 
            
            # 完成后进行目标的重新选择
            MA.find_target()
            
            # 需要重新规划
            cbs = CBS.CBS(MA.agvs,MA.map_grid)
            MA.agvs = cbs.solve()

            step += 1
    
    # 输入结束指令
    data = command(GAMEEND)