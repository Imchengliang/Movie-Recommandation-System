import random
import math
from operator import itemgetter

class UserBasedCF():
    # 初始化相关参数
    def __init__(self,K,N):
        # 找到与目标用户兴趣相似的K个用户，为其推荐10部电影
        self.n_sim_user = K
        self.n_rec_movie =N

        # 将数据集划分为训练集和测试集
        self.trainSet = {}  #格式{user1:{movie1:ratings},{user2...},....}
        self.testSet = {}

        # 用户相似度矩阵
        self.user_sim_matrix = {}
        self.movie_count = 0

        #print('Similar user number = %d' % self.n_sim_user)
        #print('Recommneded movie number = %d' % self.n_rec_movie)


    # 读文件得到“用户-电影”数据
    def get_dataset(self, filename, pivot=0.75):
        trainSet_len = 0
        testSet_len = 0
        for line in self.load_file(filename):
            user, movie, rating, timestamp = line.split(',')
            if random.random() < pivot:      #按照3:1划分训练集和测试集
                self.trainSet.setdefault(user, {}) #setdefault,自动创建key，若已存在，则不改变原value
                self.trainSet[user][movie] = float(rating) 
                trainSet_len += 1
            else:
                self.testSet.setdefault(user, {})
                self.testSet[user][movie] = float(rating)
                testSet_len += 1
        #print('Split trainingSet and testSet success!')
        #print('TrainSet = %s' % trainSet_len)
        #print('TestSet = %s' % testSet_len)
        #return self.trainSet ,self.testSet
    

    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if i == 0:  # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load %s success!' % filename)


    # 计算用户之间的相似度
    def calc_user_sim(self):
        # 构建“电影-用户”倒排表
        # key = movieID, value = list of userIDs who have seen this movie
        #print('Building movie-user table ...')
        movie_user = {}
        for user, movies in self.trainSet.items():
            for movie in movies:
                if movie not in movie_user:
                    movie_user[movie] = set()
                movie_user[movie].add(user)
        #print('Build movie-user table success!')

        self.movie_count = len(movie_user)
        #print('Total movie number = %d' % self.movie_count)

        #print('Build user co-rated movies matrix ...')
        for movie, users in movie_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1
        #print('Build user co-rated movies matrix success!')

        # 计算相似性
        #print('Calculating user similarity matrix ...')
        for u, related_users in self.user_sim_matrix.items():
            for v, count in related_users.items():
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))
        #print('Calculate user similarity matrix success!')


    # 针对目标用户U，找到其最相似的K个用户，产生N个推荐
    def recommend(self, user):
        K = self.n_sim_user
        N = self.n_rec_movie
        rank = {}
        watched_movies = self.trainSet[user]

        # v=similar user, wuv=similar factor
        for v, wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0:K]:
            #用user中的第2个item即相似度值，作为key进行排序
            #for movie,rvi in self.trainSet[v].items(): #查看相似用户v的所有感兴趣电影，若目标用户已经看过，则跳过
            for movie in self.trainSet[v]:
                if movie in watched_movies:
                    continue
                rank.setdefault(movie, 0)#若没看过，将该电影添加到推荐电影列表，
                #rank[movie] += wuv*rvi   #目标用户对该电影的感兴趣值=相似度*感兴趣度，遍历所有相似用户求和
                rank[movie] += wuv   #这里只是预测用户是否会对电影打分，与分数高低无关，所以rvi设为1，只用相似度wuv计算
        return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]  #返回感兴趣值的topN


    # 产生推荐并通过准确率、召回率和覆盖率进行评估
    def evaluate(self):
        print("Evaluation start ...")
        N = self.n_rec_movie
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_movies = set()

        for i, user, in enumerate(self.trainSet):
            test_movies = self.testSet.get(user, {})
            rec_movies = self.recommend(user)
            for movie, w in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
            rec_count += N
            test_count += len(test_movies)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        #print('precisioin=%.4f\trecall=%.4f\tcoverage=%.4f' % (precision, recall, coverage))
        return [precision, recall, coverage]