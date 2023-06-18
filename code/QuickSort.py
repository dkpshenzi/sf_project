def quicksort(num):
    if len(num) <= 1:
        return num
    
    key = num[0]
    llist,rlist,mlist = [],[],[key]
    for i in range(1,len(num)):
        if num[i].get_value() > key.get_value():
            rlist.append(num[i])
        elif num[i].get_value() < key.get_value():
            llist.append(num[i])
        else:
            mlist.append(num[i])
        
    return quicksort(llist) + mlist + quicksort(rlist)