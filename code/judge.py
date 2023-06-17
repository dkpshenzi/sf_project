import json
import judge_draw
import time

GAMELOAD = 'create_submission'
MAPSTART = 'start'
AGVCONTROL = 'step'
GAMEEND = 'finish_submission'

DIRECTION = {"RIGHT":(1,0),"LEFT":(-1,0),"UP":(0,-1),"DOWN":(0,1)}

class Judge:
    def __init__(self):
        self.map_path = r'D:\Code\sf\sf_project\data\l3.json'
        # 读取文件
        with open(self.map_path,'r',encoding='utf-8') as f:
            self.all_data = json.load(f)
            
        # 首先实例化画图
        row = self.all_data['map_attr']['height']
        col = self.all_data['map_attr']['width']
        self.j_draw = judge_draw.JudgeDraw(row,col)
        
        # 初始化做图
        self.draw()
    
    def draw(self):
        value = self.all_data['map_state']
        agvs = value['agvs']
        shelves = value['shelves']
        cargos = value['cargos']

        walls = []
        maps = value['maps']
        for position in maps:
            if position['type'] == 'wall':
                walls.append(position)
                
            if position['type'] == 'agv':
                index = position['id']
                agvs[index]['x'] = position['x']
                agvs[index]['y'] = position['y']
                
            if position['type'] == 'shelf':
                index = position['id']
                shelves[index]['x'] = position['x']
                shelves[index]['y'] = position['y']
                
            if position['type'] == 'cargo':
                index = position['id']
                cargos[index]['x'] = position['x']
                cargos[index]['y'] = position['y']
                
        self.j_draw.draw_point(agvs,shelves,cargos,walls)
    
    def gameload(self):
        # 初始化地图数据
        # 给出地图id
        data = {'value':{'maps':[
            'g4'
        ]}}
        return data
    
    def mapstart(self):
        data = {'value':self.all_data}
        return data
    
    def find_obs(self,agv_id):
        state = self.all_data['map_state']
        agvs = state['agvs']
        cargos = state['cargos']
        shelves = state['shelves']
        
        obs = []
        for i,agv in enumerate(agvs):
            if i != agv_id:
                obs.append((agv['x'],agv['y']))
        for cargo in cargos:
            obs.append((cargo['x'],cargo['y']))
        for shelf in shelves:
            obs.append((shelf['x'],shelf['y']))
        
        return obs        
    
    def add_position(self,p1,p2):
        return (p1[0]+p2[0],p1[1]+p2[1])
    
    def step(self,value):
        # 循环里面的指令
        # 然后每个为对应索引的机器人所做的事情
        for index_agv,command in enumerate(value):
            c_ty = command['type']
            
            if c_ty == 'STAY':
                # 那就什么都不需要动
                continue
            elif c_ty == 'MOVE':
                # 这里涉及到是否能够移动
                # 于是需要找到附近所有的障碍物部分
                obs = self.find_obs(index_agv)

                # 计算当前移动后的一个位置
                direction = command['dir']
                direction = DIRECTION[direction]
                
                # 当前机器人所在位置
                agv = self.all_data['map_state']['agvs'][index_agv]
                agv_position = (agv['x'],agv['y'])
                
                
                # 判断下一步是否在障碍物上，并且不能出界
                next_position = self.add_position(agv_position,direction)
                attr = self.all_data['map_attr']
                rows = attr['height']
                cols = attr['width']
                if (
                    next_position in obs
                    or next_position[0] < 0
                    or next_position[0] >= cols
                    or next_position[1] < 0
                    or next_position[1] >= rows
                ):
                    # 如果在的话那就跳过
                    continue
                else:
                    # 这个时候就需要变化机器人的坐标
                    # 注意需要变化两个地方的数据
                    x = next_position[0]
                    y = next_position[1]
                    self.all_data['map_state']['agvs'][index_agv]['x'] = x
                    self.all_data['map_state']['agvs'][index_agv]['y'] = y
                    
                    ps = self.all_data['map_state']['maps']
                    for index_p,p in enumerate(ps):
                        if p['type'] == 'agv' and p['id'] == index_agv:
                            self.all_data['map_state']['maps'][index_p]['x'] = x
                            self.all_data['map_state']['maps'][index_p]['y'] = y
                            break
            elif c_ty == 'PICKUP':
                # 计算当前移动后的一个位置
                direction = command['dir']
                direction = DIRECTION[direction]
                
                # 当前机器人所在位置
                agv = self.all_data['map_state']['agvs'][index_agv]
                agv_position = (agv['x'],agv['y'])
                
                # 方向位置
                next_position = self.add_position(agv_position,direction)
                
                #取出所有的货物坐标
                cargos = self.all_data['map_state']['cargos']
                cargo_ps = []
                for cargo in cargos:
                    position = (cargo['x'],cargo['y'])
                    cargo_ps.append(position)
                
                # 判断货物是否在当前机器人下一步上
                if next_position in cargo_ps:
                    for c_index,cargo_p in enumerate(cargo_ps):
                        if cargo_p == next_position:
                            print('成功拿起来')
                            print(c_index)
                            # 修改当前货物位置
                            self.all_data['map_state']['cargos'][c_index]['x'] = None
                            self.all_data['map_state']['cargos'][c_index]['y'] = None
                            
                            ps = self.all_data['map_state']['maps']
                            for index_p,p in enumerate(ps):
                                if p['type']== 'cargo' and p['id'] == c_index:
                                    del self.all_data['map_state']['maps'][index_p]
                            
                            # 然后修改机器人当前状态
                            self.all_data['map_state']['agvs'][index_agv]['payload'] = c_index
            elif c_ty == 'DELIVERY':
                # 首先判断机器人手上是否拿着东西
                payload = self.all_data['map_state']['agvs'][index_agv]
                if payload == None:
                    # 手上没拿着东西就不谈放下
                    pass
                else:
                    # 计算当前移动后的一个位置
                    direction = command['dir']
                    direction = DIRECTION[direction]
                    
                    # 当前机器人所在位置
                    agv = self.all_data['map_state']['agvs'][index_agv]
                    agv_position = (agv['x'],agv['y'])
                    
                    # 方向位置
                    next_position = self.add_position(agv_position,direction)

                    #取出所有的货柜坐标
                    shelves = self.all_data['map_state']['shelves']
                    shelf_ps = []
                    for shelf in shelves:
                        position = (shelf['x'],shelf['y'])
                        shelf_ps.append(position)
                    
                    # 判断货柜是否在当前机器人下一步上
                    # 并且需要编号相同
                    if next_position in shelf_ps:
                        # 当前机器人手上的货物目标
                        cargo_target = self.all_data['map_state']['agvs'][index_agv]['payload']
                        for shelf_index,shelf in enumerate(shelves):
                            position = (shelf['x'],shelf['y'])
                            if next_position == position and cargo_target == shelf['id']:
                                # 如果在下一个的位置，并且还是对应的货架
                                # 首先修改shelves的负载
                                self.all_data['map_state']['shelves'][shelf_index]['payload'] = cargo_target
                                # 然后修改机器人手上的情况
                                self.all_data['map_state']['agvs'][index_agv]['payload'] = None
                                break
                            

        # 最后输出数据
        # 需要判断所有的货物是否都在货架上了
        is_complete = True
        shelves = self.all_data['map_state']['shelves']
        for shelf in shelves:
            if shelf['payload'] == None:
                is_complete = False
                break

        self.all_data['done'] = is_complete
        data = {'value':self.all_data}
        
        # 调用画图
        self.draw()
        return data
        
    def gameend(self):
        print('程序结束')
        return self.all_data
        
    def output(self,api,value=None):
        if api == GAMELOAD:
            return self.gameload()
        elif api == MAPSTART:
            return self.mapstart()
        elif api == AGVCONTROL:
            return self.step(value)
        elif api == GAMEEND:
            return self.gameend()
        