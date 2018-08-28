import random

fi = open('kmeans_data.txt','w')
scale = 5
sigma = 5
dim = 3
prec = 5 # decimal precision
target_size = 256 * 1024 * 1024 # 256MB: two hdfs blocks by default
n_entries = target_size / ((len(str(scale)) + 2 + prec) * dim)

acc_size = 0

while True:
  tmps = ""
  for j in range(dim):
    coin = random.random()
    m = 0
    if coin < 0.5:
      m = -scale
    else:
      m = scale
    tmps = tmps + ("%."+ str(prec) + "f ") % random.gauss(m, sigma)
  acc_size = acc_size + len(tmps)
  if acc_size > target_size:
    break
  fi.write(tmps[:-1] + '\n')

fi.close()
