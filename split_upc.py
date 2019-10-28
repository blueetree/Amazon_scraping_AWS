import pandas as pd
df = pd.read_csv('upc.csv', dtype=str, header=None)
df = df.assign(g=df.index//20000)
for i in df.g.unique():
    df[df.g==i][0].to_csv('upc_%d.csv' % i, index=False)