import Astar
from copy import deepcopy

class Node:
    def __init__(self,constraints,solution,cost):
        self.constraints = constraints
        self.solution = solution
        self.cost = cost

class CBS:
    def __init__(self,agvs,shelves,cargos,map_grid):
        # 传入智能体，这个智能体是每个机器人的列表
        # 包含每个智能体的当前坐标和目标坐标
        self.agvs = agvs
        self.shelves = shelves
        self.cargos = cargos
        self.map_grid = map_grid
        
    def find_path(self,restrict=None):     
        # 寻找路径取的是机器人的暂时目标
        paths = []
        for index,agv in enumerate(self.agvs):
            if agv.temp_target == []:
                paths.append([])
                continue
            
            if restrict:
                new_restrict = []
                for res in restrict:
                    if res['id'] == index:
                        new_restrict.append(res)
            # 机器人当前的目标
            target = agv.temp_target[0]
            
            # 首先地图栅格化
            grid = self.map_grid.create_new_grid(self.cargos,agv.position,target)
            # 实例化Astar
            a = Astar.Astar(grid)
            # 进行路径规划
            if restrict and new_restrict:
                path = a.path_planning(agv.position,target,new_restrict)
            else:
                path = a.path_planning(agv.position,target)

            paths.append(path)
        return paths
    
    def cal_value(self,paths,restricts):
        # 这里是仅仅加上所有线路的长度
        value = sum(len(path) for path in paths)
        # 代价2：加上当前的限制数
        value += len(restricts) * 5
        return value
    
    def find_conflict(self,paths):
        '''for i,path in enumerate(paths):
            print(f'第{i}条路：{[node.position for node in path]}')
            time.sleep(0.1)'''
        
        # 找到冲突，并且返回第一个冲突
        # 带有发生冲突的两个机器人，以及发生冲突的时间点
        for i_index,i in enumerate(paths[:-1]):
            for j_index,j in enumerate(paths[i_index+1:]):
                # 这里得到了两条路径
                # 首先判断哪个列表长
                # print(f'第一条路径：{i}')
                # print(f'第二条路径：{j}')
                position_result = None
                cross_result = None
                previous_id = None
                future_result = None
                
                # 检查位置冲突
                if len(i) > len(j):
                    loop_li = j
                else:
                    loop_li = i
                    
                # 寻找当前路段的冲突
                for index,node in enumerate(loop_li[:-1]):
                    # 对撞 
                    if j[index].position == i[index+1].position and j[index+1].position == i[index].position:
                        cross_result = index + 1
                        # 同时需要判断，是谁造成了等待后才进行的重新冲突判断
                        if index >= 1 and j[index].position == j[index-1].position:
                            previous_id = i_index 
                        elif i[index].position == i[index-1].position:
                            previous_id = i_index + j_index + 1
                        break
                    
                    # 重叠
                    if j[index].position == i[index].position:
                        position_result = index
                        break
                    
                    # 进入和出去同一个格子
                    if j[index].position == i[index+1].position:
                        # j正在出去,i正在进来，所以让i再等会
                        future_result = [i_index,index+1]
                        break
                    if i[index].position == j[index+1].position:
                        future_result = [i_index+j_index+1,index+1]
                        break

                # 判断是否有相同时间点内，坐标相同的元素
                result = None
                if position_result:
                    result = position_result
                    if len(i) > len(j):
                        position = i[result]
                    else:
                        position = j[result]
                    return [{'a1':i_index,'a2':j_index+i_index+1,'t':result,'position':position}]
                    
                if future_result:
                    a1 =  future_result[0]
                    if a1 == i_index:
                        # 代表是i的
                        position = i[future_result[1]]
                    else:
                        # 代表是j的要堵塞
                        position = j[future_result[1]]
                    r = {'a1':a1,'a2':None,'t':future_result[1],'position':position}
                    return [r]
                
                if cross_result:
                    result = cross_result
                    p1 = i[result-1]
                    p2 = i[result]
                    if previous_id != None:
                        r1 = {'a1':previous_id,'a2':None,'t':result,'position':p1}
                        r2 = {'a1':previous_id,'a2':None,'t':result,'position':p2}
                        r3 = {'a1':previous_id,'a2':None,'t':result+1,'position':p1}
                    else:
                        r1 = {'a1':i_index,'a2':j_index+i_index+1,'t':result,'position':p1}
                        r2 = {'a1':i_index,'a2':j_index+i_index+1,'t':result,'position':p2}
                        r3 = {'a1':i_index,'a2':j_index+i_index+1,'t':result+1,'position':p1}
                    return [r1,r2,r3]
        return []
        
    def solve(self):
        # 首先更新机器人的暂时坐标
        for agv in self.agvs:
            agv.temp_target = agv.target
        
        # 首先进行一次代价最小的路径搜索，即是不考虑任何的碰撞和冲突
        min_paths = self.find_path()
        # print(f'当前的路径解决方案：{min_paths}')
        
        min_value = self.cal_value(min_paths,[])
        # print(f'当前的最小代价{min_value}')
        
        # 定义一个根节点
        root = Node([],min_paths,min_value)
        
        # 定义一个开放列表
        open_list = [root]
        closed_list = []
        
        while open_list:
            # 从开放列表中找到代价最小的一个
            current_node = min(open_list,key=lambda node:node.cost)
            
            '''print(f'当前约束条件为：')
            for c in current_node.constraints:
                c_id = c['id']
                c_tick = c['tick']
                c_position = c['position'].position
                print(f'id:{c_id} tick:{c_tick} position:{c_position}')
            for index,path in enumerate(current_node.solution):
                print(f'第{index}路线为：')
                for node in path:
                    print(node.position,end='')
                print()'''
            
            # 将当前节点从开放列表中移除
            open_list.remove(current_node)

            # 将当前节点加入关闭列表
            closed_list.append(current_node)

            # 判断其中是否存在冲突
            result = self.find_conflict(current_node.solution)
            
            # 如果没有冲突的话，则给每个机器人修改其当前路径
            # 属于是剪枝，但并不是最优选
            if not result:
                for index,path in enumerate(current_node.solution):
                    self.agvs[index].path = path
                return self.agvs
            else:
                # 如果存在冲突的话，则需要进行节点的分支
                # result=[a1,a2,t]
                a1 = result[0]['a1']
                a2 = result[0]['a2']
                if a2:
                    a1_restricts = []
                    a2_restricts = []
                    for re in result:
                        a1_restricts.append({'id':a1,'tick':re['t'],'position':re['position']})
                        a2_restricts.append({'id':a2,'tick':re['t'],'position':re['position']})     
                    restricts = [a1_restricts,a2_restricts]
                else:
                    a1_restricts = []
                    for re in result:
                        a1_restricts.append({'id':a1,'tick':re['t'],'position':re['position']})
                    restricts = [a1_restricts]
                
                # print(f'当前约束：{restricts}')
                
                for restrict in restricts:
                    # 新的约束
                    current_restrict = deepcopy(current_node.constraints)
                    # 这里遍历旧的约束
                    new_restrict = current_restrict + restrict
                    
                    # 如果有约束则优先简化约束
                    sample = []
                    end_restrict = []
                    for r in new_restrict:
                        r_id = r['id']
                        r_tick = r['tick']
                        r_position = r['position']
                        r_r_position = r_position.position
                        sam = [r_id,r_tick,r_r_position]
                        if sam not in sample:
                            sample.append(sam)
                            end_restrict.append(r)
                    
                    # 首先对该约束进行重新的一个路径规划计算
                    re_path = self.find_path(end_restrict)
                    
                    # 计算该条路径的一个价值
                    cost = self.cal_value(re_path,new_restrict)
                    
                    # 创建该约束下的节点
                    child_node = Node(end_restrict,re_path,cost)
                    
                    # 忽略已经在关闭列表中的节点
                    if child_node.solution in list(map(lambda node:node.solution,closed_list)):
                        continue
                    # 如果该节点已经存在于开放列表中，且当前的路径代价更大，则忽略
                    if any(
                        child_node.solution == node.solution and child_node.cost >= node.cost  
                        for node in open_list
                    ):
                        continue
                    
                    # 将该子节点加入开放列表中
                    open_list.append(child_node)
        # 如果没有找到任何方法的话，则返回空列表
        return self.agvs