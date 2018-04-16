import re
from collections import deque
from datetime import datetime
from time import time

import plotly.graph_objs as go
import plotly.offline as ofly

super_re = re.compile('^{date}  (?:{variants})$'.format(
    date=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*',  # date: group 1
    variants='|'.join([
        r'(?:Room:.*; HP: (\d+); dmg: (\d+); gold: (\d+);(?: dice: (\d+))?)',  # hp, dmg, gold, dice: groups (2,3,4,5)
        r'(Retrying last message\.\.\.)',  # retry: group 6
        r'(Low health, starting battle!|Too long in room, starting battle!)',  # battle: group 7
        r'(Very low health\. Pause bot!)',  # stop: group 8
        r'(Exception occurred!)',  # crash: group 9
        r'(Unknown room:.*)'  # unknown: group 10
    ])
), re.M)


class Plotter(object):
    @staticmethod
    def deque_to_list(q):
        l = [None] * len(q)
        idx = 0
        for i in q:
            l[idx] = i
            idx += 1
        return l

    def load_data(self, log_path):
        load_begin = time()

        self.data_hp, self.data_hp_x = deque(), deque()
        self.data_dmg, self.data_dmg_x = deque(), deque()
        self.data_gold, self.data_gold_x = deque(), deque()
        self.data_dice, self.data_dice_x = deque(), deque()

        self.lags, self.lags_x = deque(), deque()

        self.battles = deque()
        self.stops = deque()
        self.crashes = deque()
        self.unknown = deque()

        inf = float('inf')
        nan = float('NaN')

        current_lags = 0
        old_hp, old_dmg, old_gold, old_lags, old_dice = nan, nan, nan, nan, nan
        self.min_hp, self.min_gold, self.min_dmg = inf, inf, inf
        self.max_hp, self.max_gold, self.max_dmg, self.max_lags = -inf, -inf, -inf, -inf

        self.colored_n = 0
        self.data_n = 0
        self.load_time = datetime.now()
        with open(log_path, 'r') as f:
            for match in super_re.finditer(f.read()):
                date, hp, dmg, gold, dice, retry, battle, stop, crash, unknown = match.groups()
                if hp is not None:  # or dmg or gold
                    hp, dmg, gold = [int(i) for i in [hp, dmg, gold]]
                    if gold != old_gold:
                        self.data_gold.append(gold)
                        self.data_gold_x.append(date)
                        old_gold = gold
                        self.min_gold = min(self.min_gold, gold)
                        self.max_gold = max(self.max_gold, gold)

                    if dmg != old_dmg:
                        self.data_dmg.append(dmg)
                        self.data_dmg_x.append(date)
                        old_dmg = dmg
                        self.min_dmg = min(self.min_dmg, dmg)
                        self.max_dmg = max(self.max_dmg, dmg)

                    if hp != old_hp:
                        self.data_hp.append(hp)
                        self.data_hp_x.append(date)
                        old_hp = hp
                        self.min_hp = min(self.min_hp, hp)
                        self.max_hp = max(self.max_hp, hp)

                    if dice is not None:
                        dice = int(dice)
                        if dice != old_dice:
                            self.data_dice.append(dice)
                            self.data_dice_x.append(date)
                            old_dice = dice

                    current_lags = 0
                    self.data_n += 1
                elif retry is not None:
                    current_lags += 1
                    self.colored_n += 1
                elif battle is not None:
                    self.battles.append(date)
                elif stop is not None:
                    self.stops.append(date)
                elif crash is not None:
                    self.crashes.append(date)
                elif unknown is not None:
                    self.crashes.append(date)
                if current_lags != old_lags:
                    self.lags.append(current_lags)
                    self.lags_x.append(date)
                    old_lags = current_lags
                    self.max_lags = max(self.max_lags, current_lags)
        print('Load: ' + str(time() - load_begin))

    @staticmethod
    def _plotly_vertical(xs, bottom, top, yref, color=None, width=1):
        ln = {'width': width}
        if color:
            ln['color'] = color
        for x in xs:
            yield {
                'type': 'line',
                'xref': 'x',
                'yref': yref,
                'x0': x,
                'y0': bottom,
                'x1': x,
                'y1': top,
                'line': ln,
            }

    def plot_plotly(self):
        max_lags = self.max_lags + 30
        min_lags = 1
        max_hp = self.max_hp + 30
        min_hp = self.min_hp - 30
        min_gold = self.min_gold
        max_gold = self.max_gold

        print('min)gold: ' + str(min_gold))

        # {6x + 5y = 1; x/y = 1/0.3} (distance = 30% of size)
        size = 2 / 15  # x
        distance = 1 / 25  # y

        xaxis = dict(
            domain=[0, 1],
            anchor='x'
        )

        layout = go.Layout(
            autosize=True,
            height=1000,

            xaxis2=xaxis,
            yaxis2=dict(
                autorange=True,
                anchor='y2', domain=[1 * size + 1 * distance, (1 + 1) * size + 1 * distance]  # Hp
            ),

            xaxis3=xaxis,
            yaxis3=dict(
                autorange=True,
                anchor='y3', domain=[2 * size + 2 * distance, (2 + 1) * size + 2 * distance],  # Retries
                type='log'
            ),

            xaxis4=xaxis,
            yaxis4=dict(
                autorange=True,
                anchor='y4', domain=[3 * size + 3 * distance, (3 + 1) * size + 3 * distance]  # Gold
            ),

            xaxis5=xaxis,
            yaxis5=dict(
                autorange=True,
                anchor='y5', domain=[4 * size + 4 * distance, (4 + 1) * size + 4 * distance]  # Damage
            ),

            xaxis6=xaxis,
            yaxis6=dict(
                autorange=True,
                anchor='y6', domain=[5 * size + 5 * distance, (5 + 1) * size + 5 * distance]  # Dice
            ),

            shapes=(
                    list(self._plotly_vertical(self.stops, min_lags, max_lags, 'y3')) +  # Stops
                    list(self._plotly_vertical(self.battles, min_hp, max_hp, 'y2')) +  # Battles
                    list(self._plotly_vertical(self.unknown, self.min_gold, self.max_gold, 'y4')) +  # Unknown
                    list(self._plotly_vertical(self.crashes, self.min_dmg, self.max_dmg, 'y5'))  # Crashes
            )
        )

        pie_trace = go.Pie(labels=['OK', 'Retry'], values=[self.data_n, self.colored_n],
                           hoverinfo='label+percent', textinfo='value',
                           domain={
                               'x': [0, 1],
                               'y': [0 * size + 0 * distance, (0 + 1) * size + 0 * distance]
                           })

        damage_trace = go.Scattergl(x=self.deque_to_list(self.data_dmg_x), y=self.deque_to_list(self.data_dmg),
                                    xaxis='x', yaxis='y5',
                                    name='Урон',
                                    mode='lines+markers', connectgaps=True)
        dice_trace = go.Scattergl(x=self.deque_to_list(self.data_dice_x), y=self.deque_to_list(self.data_dice),
                                  xaxis='x', yaxis='y6',
                                  name='Бросок кубика',
                                  mode='lines+markers', connectgaps=True)
        gold_trace = go.Scattergl(x=self.deque_to_list(self.data_gold_x), y=self.deque_to_list(self.data_gold),
                                  xaxis='x', yaxis='y4',
                                  name='Золото',
                                  mode='lines+markers', connectgaps=True)
        lags_trace = go.Scattergl(x=self.deque_to_list(self.lags_x), y=self.deque_to_list(self.lags),
                                  xaxis='x', yaxis='y3',
                                  name='Повторы',
                                  mode='lines', connectgaps=True)
        hp_trace = go.Scattergl(x=self.deque_to_list(self.data_hp_x), y=self.deque_to_list(self.data_hp),
                                xaxis='x', yaxis='y2',
                                name='Здоровье',
                                mode='lines+markers', connectgaps=True)

        self.fig = go.Figure(data=[pie_trace, damage_trace, dice_trace, gold_trace, lags_trace, hp_trace],
                             layout=layout)

    def to_div(self):
        return ofly.plot(self.fig, output_type='div', validate=False, include_plotlyjs=False, show_link=False,
                         link_text="")
