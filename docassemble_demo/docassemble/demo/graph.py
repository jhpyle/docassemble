__all__ = ['make_pie']

import matplotlib.pyplot as plt


def make_pie(data, the_file):
    the_file.initialize(filename='graph.svg')
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    labels = list(data.keys())
    fracs = list(data.values())

    ax.pie(fracs, labels=labels, autopct='%1.1f%%')
    with open(the_file.path(), 'wb') as f:
        plt.savefig(f, format="svg")
    the_file.commit()
    the_file.retrieve()
