import pandas as pd

tables = pd.read_html("https://capitalzone.in")

print(tables[0])
