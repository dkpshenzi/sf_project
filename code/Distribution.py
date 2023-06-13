import numpy as np

class Node:
    def __init__(self,position,index):
        self.position = position
        self.index = index

class Distribution:
    def __init__(self,agvs,cargos,shelves):
        self.agvs = agvs
        self.cargos = cargos
        self.shelves = shelves
        
    def cal_distance(p1,p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def target_finding(self):
        # 首先对两个进行实例化
        cargos = []
        for cargo in self.cargos:
            cargos.append(Node((cargo['x'],cargo['y']),cargo['target']))
        shelves = []
        for shelf in self.shelves:
            shelves.append(Node((shelf['x'],shelf['y']),shelf['id']))

        # 然后每个机器人找到自己最近的货物
        for agv in self.agvs:
            distance = float('inf')
            task = None
            for cargo in cargos:
                dis = self.cal_distance(cargo.position,agv.position)
                if dis < distance:
                    distance = dis
                    task = cargo

            # 找到最近的任务之后开始赋值
            agv.target[0] = task.position
            # 然后找到任务对应的货架
            for shelf in shelves:
                if shelf.index == task.index:
                    agv.target[1] = shelf.position
                    break
                
        return self.agvs