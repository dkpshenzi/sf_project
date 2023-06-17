from Astar import Node
"""
根据机器人当前的位置来输出当前回合的指令
"""

# 常量设置
P = 'PICKUP'
D = 'DELIVERY'
M = 'MOVE'
S = 'STAY'

class PathTrack:
    def __init__(self,agv):
        self.agv = agv
        self.ty = self.pick_or_delivery()

    def pick_or_delivery(self):
        """判断目前是pick还是delivery的状态
        """
        if self.agv.payload == None:
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
                
        return None,None
    
    def path_tracking(self):
        # 调用当前的路线
        path = self.agv.path 
            
        if path != []:
            '''for node in path:
                print(f'节点：{node.position}，方向：{node.next_direction}')'''
                
            # 找到点，并且判断是否已经是最后一步
            node,is_last = self.find_node(path,self.agv.position)
            
            # 取出下一步的方向
            try:
                direction = node.next_direction
            except:
                return {"type":S}
            
            if is_last:
                # 如果已经是最后一步，那么将执行对应的行为
                if self.ty == P:
                    return {"type":P,"dir":direction}
                else:
                    return {"type":D,"dir":direction}
            else:
                if direction == 'STAY':
                    return {"type":S}
                else:
                    return {"type":M,"dir":direction}
        else:
            return {"type":S}            
            