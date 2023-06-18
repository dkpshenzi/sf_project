from main import PRINT

class PrintControl:
    def __init__(self,info=True,err=True):
        """设定初始值，各类信息的一个开关

        Args:
            is_print_information (bool): 信息类开关
        """
        self.is_print_map_information = info
        self.is_print_error = err
        
    def print(self,content,ty):
        """根据类型输出内容

        Args:
            content (_type_): 内容
            ty (_type_): 类型
        """
        if ty == PRINT.INFO:
            if self.is_print_map_information:
                print(content)
        elif ty == PRINT.ERROR:
            if self.is_print_error:
                print(content)
        