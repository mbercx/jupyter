import os, json
import numpy as np
from matplotlib import colors, cm
import matplotlib.pyplot as plt

from ipywidgets import interact, interactive, interactive_output, fixed, FloatSlider, Tab, \
    Select, SelectMultiple, HBox, VBox, Output, Text, Button, Layout
from ipyfilechooser import FileChooser

def interface(f):
    
    try:
        with open(f.selected_filename, "r") as file:
            timing_list = json.loads(file.read())
    except FileNotFoundError:
        return "Please select an existing file."
    
    try:
        assert isinstance(timing_list, list)
    except AssertionError:
        return "timing_list is not a List. Please check your input file."

    nodes_list = list(set([t["nodes"] for t in timing_list]))
    nodes_list.sort()

    kpar_list = list(set([t["kpar"] for t in timing_list]))
    kpar_list.sort()

    ncore_list = list(set([t["ncore"] for t in timing_list]))
    ncore_list.sort()
    
    select_layout = Layout(width='70px')

    versus = Select(options=["nodes", "kpar"], index=0,
                    layout=select_layout)
    nodes = Select(options=nodes_list, index=0,
                   layout=select_layout)
    x_axis_select = Select(options=["ncore", "npar"], index=0, 
                           layout=select_layout)
    nodes_select = SelectMultiple(options=nodes_list,
                                  value=nodes_list[:3],
                                  rows=len(nodes_list),
                                  layout=select_layout)
    kpar_select = SelectMultiple(options=kpar_list,
                                 value=kpar_list[:3],
                                 rows=len(kpar_list),
                                 layout=select_layout)
    ncore_select = SelectMultiple(options=ncore_list,
                                  value=ncore_list[:3],
                                  rows=len(ncore_list),
                                  layout=select_layout)

    widget_mappings = {
        "Timestep": {
            "descriptions": ["X-axis", ],
            "input": (versus, ),
            "output": interactive_output(
                time_plot, {"timing_list": fixed(timing_list),
                            "versus": versus}
            )
        },
        "Chessboard": {
            "descriptions": ["Nodes", "X-axis"],
            "input": (nodes, x_axis_select),
            "output": interactive_output(
                chessboard_plot, {"timing_list": fixed(timing_list),
                                  "nodes": nodes, 
                                  "x_axis": x_axis_select}
            )
        },
        "Tetris": {
            "descriptions": ["Nodes", "KPAR", "NCORE"],
            "input": [nodes_select, kpar_select, ncore_select],
            "output": interactive_output(
                tetris_plot, {"timing_list": fixed(timing_list),
                              "nodes_choices": nodes_select,
                              "kpar_choices": kpar_select,
                              "ncore_choices": ncore_select}
            )
        },
        "Optimal": {
            "descriptions": [],
            "input": (),
            "output": interactive_output(
                optimal_settings, {"timing_list": fixed(timing_list)}
            )
        },
        "NPAR line plot": {
            "descriptions": ["Nodes", ],
            "input": (nodes, ),
            "output": interactive_output(
                npar_line_plot, {"timing_list": fixed(timing_list),
                                "nodes": nodes}
            )
        }
    }

    tab = Tab()
    tab.children = [VBox((HBox([VBox((Button(description=desc, layout=select_layout), inp)) 
                                for (desc, inp) in zip(w["descriptions"], w["input"])]), w["output"])) 
                    for w in widget_mappings.values()]

    for i, title in enumerate(widget_mappings.keys()):
        tab.set_title(i, title)
    
    return tab

def time_plot(timing_list, versus):
    
    if versus == "nodes":
        time_vs_nodes(timing_list)
    elif versus == "kpar":
        time_vs_kpar(timing_list)

def time_vs_nodes(timing_list):
    
    kpar_list = list(set(
        [t["kpar"] for t in timing_list]
    ))
    kpar_list.sort()
    
    plt.rcdefaults()
    cmap = cm.viridis._resample(len(kpar_list))

    plt.rc("font", size=14)
    fig, ax = plt.subplots()

    plt.scatter(
        x=[t["nodes"] for t in timing_list], 
        y=[t["timing"] for t in timing_list],
        c=[cmap.colors[kpar_list.index(t["kpar"])] for t in timing_list]
    )

    plt.yscale("log")
    ax.set_xlabel("Number of nodes")
    ax.set_ylabel("Average time/electronic step")

    cbar = plt.colorbar()
    cbar.ax.set_yticklabels(["1", "8", "20", "42", "112", "252"]);
    cbar.ax.set_ylabel("KPAR")
    
    return plt

def time_vs_kpar(timing_list):
    
    plt.rcdefaults()
    
    node_list = list(set(
        [t["nodes"] for t in timing_list]
    ))
    node_list.sort()

    for node in node_list:

        node_timings = [timing for timing in timing_list if timing["nodes"] == node]
        kpars = [t["kpar"] for t in node_timings]
        timings = [t["timing"] for t in node_timings]

        plt.plot(kpars, timings, "o")

    plt.xscale("log")
    plt.xlabel("KPAR")
    plt.yscale("log")
    plt.ylabel("Average time / electronic step.")

    plt.legend(node_list, bbox_to_anchor=(1, 1.025), loc="upper left", title="# nodes")

def npar_line_plot(timing_list, nodes):
    
    import matplotlib.pyplot as plt
    
    nodes_timings = [timing for timing in timing_list if timing["nodes"] == nodes]
    nodes_timings = sorted(nodes_timings, key=lambda x: x["kpar"])

    npars = set()
    for n in [t["npar"] for t in nodes_timings]:
        npars.add(n)
    npars = list(npars)
    npars.sort()
    npars = npars[:9]

    cmap = cm.plasma._resample(len(npars))

    for n in npars:
        kpars = [t["kpar"] for t in nodes_timings if t["npar"] == n]
        timings = [t["timing"] for t in nodes_timings if t["npar"] == n]


        plt.plot(kpars, timings, "o-", color=cmap.colors[npars.index(n)])

    # Set axis scales
    plt.xscale("log")
    plt.xlabel("KPAR")
    plt.yscale("log")
    plt.ylabel("Average time / electronic step")
    plt.legend(npars, bbox_to_anchor=(1, 1.025), loc="upper left", title="NPAR")
    
def chessboard_plot(timing_list, nodes, x_axis="npar"):
    
    plt.rcdefaults()
    
    node_timings = [t for t in timing_list if t["nodes"] == nodes]

    node_kpar_list = list(set([t["kpar"] for t in node_timings]))
    node_kpar_list.sort()
    node_x_list = list(set([t[x_axis] for t in node_timings]))
    node_x_list.sort()

    timestep = np.zeros([len(node_kpar_list), len(node_x_list)])

    for timing in node_timings:
        timestep[node_kpar_list.index(timing["kpar"])][node_x_list.index(timing[x_axis])] = timing["timing"]

    norm = colors.Normalize(vmin=np.min([t["timing"] for t in node_timings]),
                            vmax=np.max(timestep))
    timestep[timestep == 0.0] = None

    fig, ax = plt.subplots(figsize=(len(node_x_list), len(node_kpar_list)))
    ax.imshow(timestep, cmap=cm.RdYlGn_r, origin="lower", norm=norm)

    for i in range(len(node_kpar_list)):
        for j in range(len(node_x_list)):
            if not np.isnan(timestep[i, j]):
                text = ax.text(j, i, round(timestep[i, j], 1),
                               ha="center", va="center", color="k")

    ax.set_xticks(range(len(node_x_list)))
    ax.set_xticklabels([str(n) for n in node_x_list])
    ax.set_xlabel(x_axis)
    ax.set_yticks(range(len(node_kpar_list)))
    ax.set_yticklabels([str(k) for k in node_kpar_list])
    ax.set_ylabel("KPAR")

    plt.title(str(nodes) + " nodes")
    
def tetris_plot(timing_list, nodes_choices, kpar_choices, 
                ncore_choices):
    
    fontsize = 18
    plt.rcParams["axes.linewidth"] = 2
    plt.rcParams["font.size"] = 14
    plt.rc('axes', labelsize=fontsize)
    plt.rc('xtick', labelsize=fontsize)
    plt.rc('ytick', labelsize=fontsize)

    fig, ax = plt.subplots(1, len(nodes_choices), 
                           figsize=(len(nodes_choices) * len(ncore_choices), len(kpar_choices)))
    plt.subplots_adjust(wspace=0, bottom=0.0)

    for i, n in enumerate(nodes_choices):

        n_timings = [t for t in timing_list if t["nodes"] == n 
                     and t["kpar"] in kpar_choices and t["ncore"] in ncore_choices]

        timestep = np.zeros([len(kpar_choices), len(ncore_choices)])

        for t in n_timings:
            timestep[kpar_choices.index(t["kpar"])][ncore_choices.index(t["ncore"])] = t["timing"]
        
        try:
            norm = colors.Normalize(vmin=np.min([t["timing"] for t in n_timings]),
                                    vmax=np.max(timestep))
        except ValueError:
            print("Chosen combination of Nodes/KPAR/NCORE results in empty plot for " + str(n) + " nodes.")
            return None

        timestep[timestep == 0.0] = np.nan
        im = ax[i].imshow(timestep, cmap=cm.RdYlGn_r, origin="lower", norm=norm)

        for x in range(len(kpar_choices)):
            for y in range(len(ncore_choices)):
                if not np.isnan(timestep[x, y]):
                    t = ax[i].text(y, x, round(timestep[x, y], 1),
                               ha="center", va="center", color="k")

        ax[i].set_title(str(n) + " NODES", fontsize=20)
        ax[i].set_xticks(range(len(ncore_choices)))
        ax[i].set_xticklabels([str(c) for c in ncore_choices])
        ax[i].set_xlabel("NCORE")
        if i > 0:
            #ax[i].tick_params(left="off", right="off")
            ax[i].yaxis.set_major_locator(plt.NullLocator())

    ax[0].set_yticks(range(len(kpar_choices)))
    ax[0].set_yticklabels([str(k) for k in kpar_choices])
    ax[0].set_ylabel("KPAR")
    
def optimal_settings(timing_list):
    
    nodes_list = list(set(
        [t["nodes"] for t in timing_list]
    ))
    nodes_list.sort()
    
    best_setting_list = []

    for nodes in nodes_list:

        best_time = 1e10

        for t in [timing for timing in timing_list if timing["nodes"] == nodes]:
            if t["timing"] < best_time:
                best_setting = t
                best_time = t["timing"]
        best_setting_list.append(best_setting)
        
    speedup = []
    efficiency = []

    for d in best_setting_list:
        speedup.append(
            best_setting_list[0]["timing"] / d["timing"]
        )
        efficiency.append(
            best_setting_list[0]["timing"] / d["timing"] / d["nodes"]
        )
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx() 

    ax1.plot(
        [t["nodes"] for t in best_setting_list],
        [t["timing"] for t in best_setting_list],
        "o-", color="b"
    )
    ax2.plot(
        [t["nodes"] for t in best_setting_list],
        efficiency,
        "o-", color="r"
    )
    ax2.plot(
        [t["nodes"] for t in best_setting_list],
        [1]*len(best_setting_list),
        "-", color="k"
    )
    ax1.set_xlabel("# nodes")
    ax1.set_ylabel("Average time / electronic step", color="b")
    ax2.set_ylabel("Efficiency", color="r")