import numpy as np

# 节点类
class Node:
    def __init__(self,position):
        self.position = position
        self.next_direction
        # 起始节点到达当前节点的代价
        self.g = 0
        # 当前节点到目标节点的代价
        self.h = 0
        # 总代价
        self.f = 0
    def get_f(self):
        self.f = self.g + self.h
        
class Astar:
    def __init__(self,grid):
        # 改用网格地图
        self.gap = 1
        self.grid = grid
        
    # 启发函数
    def inspire(self,neighbor_node,goal_node):
        # 使用曼哈顿距离
        dx = abs(neighbor_node[0]-goal_node[0])
        dy = abs(neighbor_node[1]-goal_node[1])
        return dx + dy
    
    # 路径规划
    def path_planning(self,start,goal):
        # 获取网格的行数和列数
        rows = len(self.grid)
        cols = len(self.grid[0])
        
        # 定义四个方向的移动
        directions = [(self.gap,0,'RIGHT'),(0,self.gap,'UP'),(-self.gap,0,'LEFT'),(0,-self.gap,'DOWN')]
        
        # 创建起始节点和目标节点
        start_node = Node(start)
        goal_node = Node(goal)
        
        # 创建开放列表和关闭列表
        open_list = [start_node]
        closed_list = []
        
        # 循环直到找到路径或者开放列表为空
        while open_list:
            # 从开放列表中找到代价最小的点
            current_node = min(open_list,key=lambda node:node.f)
            
            # 将当前节点从开放列表中移除
            open_list.remove(current_node)
            
            # 将当前节点加入关闭列表
            closed_list.append(current_node)
            
            # 到达目标节点，构建路径并返回
            if current_node.position == goal_node.position:
                path = []
                while current_node:
                    path.append(current_node.position)
                    current_node = current_node.parent
                # 翻转路径
                return path[::-1]
            
            # 遍历方向
            for direction in directions:
                # 计算相邻节点的位置
                neighbor_position = current_node.position + direction[:2]
                
                # 忽略超出边界的点
                if(
                    neighbor_position[0] < self.gap
                    or neighbor_position[0] >= rows * self.gap
                    or neighbor_position[1] < self.gap
                    or neighbor_position[1] >= cols * self.gap
                ):
                    continue
                
                # 忽略障碍物，货架，其他机器人节点
                if self.grid[neighbor_position[0]][neighbor_position[1]] == 1:
                    continue
                
                # 创建相邻节点对象
                neighbor_node = Node()
                
                # 设置父节点的方向
        