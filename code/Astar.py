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
    
def print_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    path[::-1]
    if len(path) >= 4:
        for p in path:
            print(p.position,end='')
    print()
    
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
        # 添加一个原地的方向，让其能够停留在原地
        self.directions = {'STAY':(0,0),'RIGHT':(self.gap,0),'UP':(0,self.gap),'LEFT':(-self.gap,0),'DOWN':(0,-self.gap)}
        
    def inspire(self,neighbor_node,goal_node):
        """启发函数

        Args:
            neighbor_node (_type_): 邻居节点
            goal_node (_type_): 目标节点

        Returns:
            _type_: 返回h代价
        """
        # 使用曼哈顿距离
        dx = abs(neighbor_node.position[0]-goal_node.position[0])
        dy = abs(neighbor_node.position[1]-goal_node.position[1])
        return dx + dy
    
    def get_direction(self,current_node,parent_node):
        """获得父节点如何到子节点

        Args:
            current_node (_type_): 当前节点
            parent_node (_type_): 父节点

        Returns:
            _type_: 返回方向
        """
        direction = (current_node.position[0] - parent_node.position[0],current_node.position[1] - parent_node.position[1])
        for key,value in self.directions.items():
            if direction == value:
                return key
    
    def path_planning(self,start,goal,restrict=None):
        """路径规划

        Args:
            start (_type_): 起始坐标
            goal (_type_): 终点坐标
            restrict : 约束 (position,tick)

        Returns:
            _type_: 返回的是路径节点的列表
        """
        # 获取网格的行数和列数
        rows = len(self.grid)
        cols = len(self.grid[0])
        
        # print_grid(self.grid,'传输进来的地图')
        
        # print(f'行数y:{rows}')
        # print(f'列数x:{cols}')
        # print(f'起点坐标{start}')
        # print(f'终点坐标{goal}')
        
        # 创建起始节点和目标节点
        start_node = Node(start)
        goal_node = Node(goal)
        
        # 创建开放列表和关闭列表
        open_list = [start_node]
        # closed_list = []
        
        # print(f'目标节点坐标{goal_node.position}')
        
        # 循环直到找到路径或者开放列表为空
        while open_list:
            # 从开放列表中找到代价最小的点
            current_node = min(open_list,key=lambda node:node.f)
            
            # 输出当前点的路径
            print_path(current_node)
            
            # 将当前节点从开放列表中移除
            open_list.remove(current_node)
            
            # 将当前节点加入关闭列表
            # closed_list.append(current_node)
            
            # print(f'当前节点坐标{current_node.position}')
            
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
                # print('返回正确路径')
                return path[::-1]
            
            # print('进行了一次开放列表查询')
            
            # 遍历方向
            for direction in self.directions.values():
                # 计算相邻节点的位置
                neighbor_position = (current_node.position[0] + direction[0],current_node.position[1] + direction[1])
                
                # 忽略超出边界的点
                if(
                    neighbor_position[0] < 0
                    or neighbor_position[0] >= cols
                    or neighbor_position[1] < 0
                    or neighbor_position[1] >= rows
                ):
                    # print(f'忽略了{neighbor_position}')
                    continue
                
                # 忽略障碍物，货架，其他机器人节点
                if self.grid[neighbor_position[1]][neighbor_position[0]] == 1:
                    # print(f'忽略障碍物节点{neighbor_position}')
                    continue
                
                # 创建相邻节点对象
                neighbor_node = Node(neighbor_position,current_node)
                
                # 忽略已经在关闭列表中的点
                # 但是允许与自己坐标相同的点
                '''if neighbor_node.position in list(map(lambda node:node.position,closed_list)) and neighbor_node.position != current_node.position:
                    # print(f'忽略了在关闭列表中的节点{neighbor_position}')
                    continue'''
                
                # print(f'邻居节点坐标{neighbor_position}')
                
                # 计算从起始节点到相邻节点的实际代价
                # 因为走直线，所以只会加1  
                neighbor_node.g = current_node.g + 1
                
                # 这里开始判断约束条件
                # 如果这个点是刚好在这个时间，并且是这个点则跳过
                is_continue = False
                if restrict:
                    for res in restrict:
                        if neighbor_node.g == res['tick'] and neighbor_node.position == res['position'].position:
                            is_continue = True
                            break
                if is_continue:
                    continue
                
                # 计算相邻节点到目标节点的估计代价，用曼哈顿距离
                # neighbor_node.h = self.inspire(neighbor_node,goal_node)
                neighbor_node.h = 0
                
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
        
def print_grid(grid,context):
    newg = grid[-1::-1]
    print(context)
    for g in newg:
        print(g)
    
def create_grids(rows,cols,start,goal,agvs,shelves,cargos,walls):
    
    # 0的地方代表的是空白，起点跟终点需要同时设为2
    # 初始化地图
    grid = []
    for r in range(rows):
        r_li = []
        for c in range(cols):
            r_li.append(0)
        grid.append(r_li)
    # print_grid(grid,'初始地图')
        
    # 机器人障碍物
    for agv in agvs:
        position = agv.position
        grid[position[1]][position[0]] = 0
    # 将自己本身的设置为2
    grid[start[1]][start[0]] = 2
    # print_grid(grid,'加入了机器人后的地图')
    
    # 货架障碍物
    for shelf in shelves:
        position = (shelf['x'],shelf['y'])
        grid[position[1]][position[0]] = 1
    # print_grid(grid,'加入了货架后的地图')
    
    # 货物障碍物
    # 为判断器额外加的一个条件
    if cargos:
        for cargo in cargos:
            if cargo['x'] != None:
                position = (cargo['x'],cargo['y'])
                grid[position[1]][position[0]] = 1
    # print_grid(grid,'加入了货物后的地图')
        
    # 障碍物
    if walls:
        for wall in walls:
            position = (wall['x'],wall['y'])
            grid[position[1]][position[0]] = 1
        
    # 设置终点为0
    grid[goal[1]][goal[0]] = 2
    # print_grid(grid,'加入了障碍物后的地图')
    
    # 以上便把整个地图的格式给设置好了
    return grid