import pandas as pd

data_1st = pd.DataFrame()

data_2nd = [{"C":1111, "M":43}, {"C":2222, "M":44}]

data_2nd = pd.DataFrame(data_2nd)

print("\ndata_2nd\n", data_2nd)

data = pd.concat([data_1st, data_2nd], ignore_index=True)

print("\ndata\n", data)