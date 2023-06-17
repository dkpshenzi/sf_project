from copy import deepcopy

class MapCreate:
    def __init__(self,rows,cols,shelves,walls):
        # 一开始就直接进行一个地图的初始化，因为墙壁和货架的位置不会变
        grid = []
        for r in range(rows):
            r_li = []
            for c in range(cols):
                r_li.append(0)
            grid.append(r_li)
            
        for shelf in shelves:
            position = (shelf['x'],shelf['y'])
            grid[position[1]][position[0]] = 1
            
        for wall in walls:
            position = (wall['x'],wall['y'])
            grid[position[1]][position[0]] = 1

        self.grid = grid
    
    def create_new_grid(self,cargos,start,goal):
        new_origin_grid = deepcopy(self.grid)
        # 货物障碍物
        
        # 为判断器额外加的一个条件
        if cargos:
            for cargo in cargos:
                if cargo['x'] != None:
                    position = (cargo['x'],cargo['y'])
                    new_origin_grid[position[1]][position[0]] = 1
        
        new_origin_grid[goal[1]][goal[0]] = 2
        new_origin_grid[start[1]][start[0]] = 2
        
        return new_origin_grid
        