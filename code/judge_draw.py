import numpy as np
import matplotlib.pyplot as plt

class JudgeDraw:
    def __init__(self,row,col):
        # 画图
        plt.ion()
        
        self.row = row
        self.col = col
        # 先定好左下和右上打基础
        # plt.scatter(-0.5,-0.5,color='white')
        # plt.scatter(row+0.5,col+0.5,color='white')
    
    def get_pos_li(self,pos):
        position = []
        for p in pos:
            position.append((p['x'],p['y']))
        return np.array(position)
    
    def draw_point(self,agvs,shelves,cargos,walls):
        plt.clf()
        
        # 弄好坐标
        plt.xlim((-1,self.col+1))
        plt.ylim((-1,self.row+1))
        plt.xticks(np.arange(-1,self.col+1))
        plt.yticks(np.arange(-1,self.row+1))
        
        # 绘制网格线
        plt.grid(True)
        plt.axis('scaled')
        
        # 首先获得各种坐标列表
        agvs_p = self.get_pos_li(agvs)
        shelves_p = self.get_pos_li(shelves)
        cargos_p = self.get_pos_li(cargos)
        walls_p = self.get_pos_li(walls)
        
        AC = 'blue'
        SC = 'red'
        CC = 'green'
        WC = 'black'
        
        for agv in agvs_p:
            x = agv[0]
            y = agv[1]
            plt.scatter(x,y,color=AC,marker='s',label='AGVs')
            
        for shelf in shelves_p:
            x = shelf[0]
            y = shelf[1]
            plt.scatter(x,y,color=SC,marker='s',label='Shelves')
        
        for cargo in cargos_p:
            x = cargo[0]
            y = cargo[1]
            plt.scatter(x,y,color=CC,marker='s',label='Cargos')
        
        for wall in walls_p:
            x = wall[0]
            y = wall[1]
            plt.scatter(x,y,color=WC,marker='s',label='Walls')
        
        plt.pause(2)
        