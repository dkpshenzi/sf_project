import numpy as np

# 节点类
class Node:
    def __init__(self,position,parent=None):
        """节点类的初始函数

        Args:
            position (_type_): 坐标
            parent (_type_, optional): 父节点，方便回溯. Defaults to None.
        """
        self.position = position
        # 父节点
        self.parent = parent
        # 起始节点到达当前节点的代价
        self.g = 0
        # 当前节点到目标节点的代价
        self.h = 0
        # 总代价
        self.f = 0
        # 向子节点的方向
        self.next_direction = None
        # 是否是枢纽
        self.is_hub = False
    def get_f(self):
        """计算总代价
        """
        self.f = self.g + self.h
    def change_into_hub(self):
        self.is_hub = True
    
class Astar:
    def __init__(self,grid):
        """Astar算法的初始函数

        Args:
            grid (list): 对地图栅格化的地图表示
            
        Attri:
            gap : 网格地图的间隔
            grid : 网格地图
        """
        # 改用网格地图
        self.gap = 1
        self.grid = grid
        # 定义四个方向
        self.directions = {'RIGHT':(self.gap,0),'UP':(0,self.gap),'LEFT':(-self.gap,0),'DOWN':(0,-self.gap)}
        
    def inspire(self,neighbor_node,goal_node):
        """启发函数

        Args:
            neighbor_node (_type_): 邻居节点
            goal_node (_type_): 目标节点

        Returns:
            _type_: 返回h代价
        """
        # 使用曼哈顿距离
        dx = abs(neighbor_node[0]-goal_node[0])
        dy = abs(neighbor_node[1]-goal_node[1])
        return dx + dy
    
    def get_direction(self,current_node,parent_node):
        """获得父节点如何到子节点

        Args:
            current_node (_type_): 当前节点
            parent_node (_type_): 父节点

        Returns:
            _type_: 返回方向
        """
        direction = current_node.position - parent_node.position
        for key,value in self.directions.items():
            if direction == value:
                return key
    
    def path_planning(self,start,goal):
        """路径规划

        Args:
            start (_type_): 起始坐标
            goal (_type_): 终点坐标

        Returns:
            _type_: 返回的是路径节点的列表
        """
        # 获取网格的行数和列数
        rows = len(self.grid)
        cols = len(self.grid[0])
        
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
                    path.append(current_node)
                    # 如果父节点存在的话，就设置父节点的下一个方向
                    if current_node.parent:
                        next_direction = self.get_direction(current_node,current_node.parent)
                        current_node.parent.next_direction = next_direction
                    current_node = current_node.parent
                # 翻转路径
                return path[::-1]
            
            # 遍历方向
            for direction in self.directions.values():
                # 计算相邻节点的位置
                neighbor_position = current_node.position + direction
                
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
                neighbor_node = Node(neighbor_position,current_node)
                
                # 忽略已经在关闭列表中的点
                if neighbor_node.position in list(map(lambda node:node.position,closed_list)):
                    continue
                
                # 计算从起始节点到相邻节点的实际代价
                # 因为走直线，所以只会加1
                neighbor_node.g = current_node.g + 1
                
                # 计算相邻节点到目标节点的估计代价，用曼哈顿距离
                neighbor_node.h = self.inspire(neighbor_node,goal_node)
                
                # 计算相邻节点的总代价
                neighbor_node.get_f()
                
                # 如果相邻节点已经在开放列表中，且新的路径代价更大，则忽略
                if any(
                    neighbor_node.position == node.position and neighbor_node.g >= node.g  
                    for node in open_list
                ):
                    continue
                
                # 将相邻节点加入开放列表
                open_list.append(neighbor_node)
        # 没有找到路径，则返回空列表
        return []
        
def create_grids(rows,cols,start,goal,agvs,shelves,cargos,walls):
    
    # 0的地方代表的是空白，起点跟终点需要同时设为2
    # 初始化地图
    grid = []
    for r in range(rows):
        r_li = []
        for c in range(cols):
            r_li.append(0)
        grid.append(r_li)
        
    # 机器人障碍物
    for agv in agvs:
        position = agv.position
        grid[position[0]][position[1]] = 1
    # 将自己本身的设置为2
    grid[start[0]][start[1]] = 2
    
    # 货架障碍物
    for shelf in shelves:
        position = (shelf['x'],shelf['y'])
        grid[position[0]][position[1]] = 1
    
    # 货物障碍物
    for cargo in cargos:
        position = (cargo['x'],cargo['y'])
        grid[position[0]][position[1]] = 1
        
    # 障碍物
    for wall in walls:
        position = (wall['x'],wall['y'])
        grid[position[0]][position[1]] = 1
        
    # 设置终点为0
    grid[goal[0]][goal[1]] = 2
    
    # 以上便把整个地图的格式给设置好了
    return grid