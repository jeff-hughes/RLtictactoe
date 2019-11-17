# %%
import pandas as pd
from plotnine import ggplot, aes, geom_line

file = 'tally_20191117_104202.csv'
data = pd.read_csv(file)

# %%
data2 = data.melt(id_vars=['game'],
                  value_vars=['cum_X', 'cum_O', 'cum_T'],
                  var_name='player',
                  value_name='wins')

data2['perc'] = data2.wins / data2.game

# %%
(ggplot(data2, aes(x='game', y='perc', color='player'))
    + geom_line())
