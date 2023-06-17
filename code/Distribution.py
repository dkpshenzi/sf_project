import numpy as np

class ShelfNode:
    def __init__(self,position,index,payload):
        self.position = position
        self.index = index
        self.payload = payload
        
class CargoNode:
    def __init__(self,position,target,is_chose=False,is_finished=False):
        self.position = position
        self.target = target
        self.is_chose = is_chose
        self.is_finished = is_finished

class Distribution:
    def __init__(self,cargos,shelves):
        # 这里的agv是实例列表，cargos和shelves都是字典列表
        self.agvs = []
        self.cargos = cargos
        self.shelves = shelves
        
        # 通过列表得到一个对应任务列表
        self.task_li = self.get_task_li(self.cargos,self.shelves)
        
    def update(self,agvs,cargos,shelves):
        self.agvs = agvs
        self.cargos = cargos
        self.shelves = shelves
        
    def get_task_li(self,cargos,shelves):
        cargos_to_shelves = []
        for cargo in cargos:
            shelf_id = cargo['target']
            shelf_position = (shelves[shelf_id]['x'],shelves[shelf_id]['y'])
            cargo_position = (cargo['x'],cargo['y'])
            cargos_to_shelves.append([cargo_position,shelf_position])
        return cargos_to_shelves
        
    def cal_distance(self,p1,p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def check_is_chose(self,agvs,cargo):
        # 检查是否已经被选中
        exist_target = []
        for agv in agvs:
            if agv.target:
                exist_target.append(agv.target)
        if cargo.position in exist_target:
            return True
        else:
            return False

    def check_is_finished(self,shelves,cargo):
        # 检查是否已经在指定位置
        # 遍历当前货架中的负载，获得已经到达的货物列表
        finish_cargo = []
        for shelf in shelves:
            if shelf.payload == self.cargos_to_shelves[shelf.index]:
                finish_cargo.append(shelf.index)
        if cargo.target in finish_cargo:
            return True
        else:
            return False

    def target_finding(self):
        # 设定一个是否赋予了目标的变量
        is_give_path = False
        
        # 然后每个机器人找到自己最近的货物
        if self.task_li:
            for agv in self.agvs:
                # 过滤掉有目标的机器人
                if agv.target:
                    continue

                dis = float('inf')
                target_task = None
                for task in self.task_li:
                    cargo_position = task[0]
                    new_dis = self.cal_distance(agv.position,cargo_position)
                    if dis > new_dis:
                        dis = new_dis
                        target_task = task
                agv.target = target_task
                # 并且删掉这个
                self.task_li.remove(target_task)
                
                # 走到这一步说明没有被筛选
                is_give_path = True
                        
        return self.agvs,is_give_path