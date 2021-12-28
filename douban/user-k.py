from user import UserBasedCF 

rating_file = '/Users/imchengliang/Downloads/movie recommendation system/douban/ml-latest-small/ratings.csv'
Mat=[]
N_range=[5,10,15,20]
for N in N_range:
    M=[]
    for i in range(5):
        userCF = UserBasedCF(10, N)
        userCF.get_dataset(rating_file) #获取并划分数据集
        userCF.calc_user_sim() #计算用户相似度矩阵
        m=userCF.evaluate() #评估
        M.append(m) #记录每个数据集上的指标向量
    Mat.append([sum([h[2] for h in M])/5,sum([h[1] for h in M])/5,sum([h[0] for h in M])/5])#求均值

#性能曲线
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display

lab=["precision","recall","coverage"]
p=pd.DataFrame(Mat,columns=lab)
display(p) 
num = np.array(Mat)
num=num.T
#plt.rcParams['font.sans-serif'] = ['SimHei']#可以plt绘图过程中中文无法显示的问题
plt.figure(figsize=(10, 5), dpi=80)
#lab=["precision","recall","coverage"]
x_label=N_range
for row in range(len(num)):
    markes = ['-o', '-s', '-^']
    plt.plot(x_label, num[row], markes[row], label =lab[row])
plt.legend()#显示图例，如果注释，即使设置了图例仍然不显示
plt.show()#显示图片，如果注释，即使设置了图片仍然不显示