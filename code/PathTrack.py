"""
根据机器人当前的位置来输出当前回合的指令
"""

# 常量设置
P = 'PICKUP'
D = 'DELIVERY'
M = 'MOVE'

class PathTrack:
    def __init__(self,agv):
        self.agv = agv
        self.ty = self.pick_or_delivery()

    def pick_or_delivery(self):
        """判断目前是pick还是delivery的状态
        """
        if self.agv.cap == 1:
            # 有空余空间
            return P
        else:
            return D
    
    def find_node(self,path,position):
        """找到当前agv在哪个位置上，并且返回这个位置

        Args:
            path (_type_): 路径点的列表
            position (_type_): 当前机器人所在的位置

        Returns:
            _type_: 返回当前所在的路径节点
        """
        for index,node in enumerate(path):
            if node.position == position:
                if index == len(path)-2:
                    return node,True
                else:
                    return node,False
    
    def path_tracking(self):
        if self.ty == P:
            # 这时将会调用第一个路线
            path = self.agv.path[0]
        elif self.ty == D:
            path = self.agv.path[1]
            
        # 找到点，并且判断是否已经是最后一步
        node,is_last = self.find_node(self.agv.position)
        
        # 取出下一步的方向
        direction = node.next_direction
        
        if is_last:
            # 如果已经是最后一步，那么将执行对应的行为
            if self.ty == P:
                return {"type":P,"dir":direction}
            elif self.ty == D:
                return {"type":D,"dir":direction}
        else:
            return {"type":M,"dir":direction}            
            