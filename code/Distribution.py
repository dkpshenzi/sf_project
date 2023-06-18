import numpy as np

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
            shelf_id = cargo.target
            shelf_position = shelves[shelf_id].position
            cargo_position = cargo.position
            cargos_to_shelves.append([cargo_position,shelf_position])
        return cargos_to_shelves
        
    def cal_distance(self,p1,p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def target_finding(self):
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
                        
        return self.agvs