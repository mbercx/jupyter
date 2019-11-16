import os
import numpy as np

from vscworkflows.workflows.core import get_wf_parallel
from fireworks import LaunchPad
from pymatgen import Structure

from ipywidgets import interact, interactive, Select, IntSlider, Button, Output, \
    FileUpload, BoundedIntText, SelectMultiple, Text, VBox, HBox, Layout
from ipyfilechooser import FileChooser

CLUSTER_DICT = {
    "leibniz": {
        "launchpad": LaunchPad.from_dict({
            'host': 'mongodb+srv://testcluster-au9d3.gcp.mongodb.net',
            'port': 27017,
            'name': 'test_leibniz',
            'username': 'testuser',
            'password': 'testpassword',
            'ssl': True,
            'authsource': 'admin'
        }),
        "scratch_dir": "/scratch/antwerpen/202/vsc20248/",
        "cores_per_node": 28
    },
    "hopper": {
        "launchpad": LaunchPad.from_dict({
            'host': 'mongodb+srv://testcluster-au9d3.gcp.mongodb.net',
            'port': 27017,
            'name': 'test_hopper',
            'username': 'testuser',
            'password': 'testpassword',
            'ssl': True,
            'authsource': 'admin'
        }),
        "scratch_dir": "/scratch/antwerpen/202/vsc20248/",
        "cores_per_node": 20
    }
}

def selection_interface(fworker, functional, kpt_density, nbands, nodes_list):
    
    selection_dict = {}
    selection_dict["scratch_dir"] = CLUSTER_DICT[fworker]["scratch_dir"]
    selection_dict["cores_per_node"] = CLUSTER_DICT[fworker]["cores_per_node"]
    selection_dict["lpad"] = CLUSTER_DICT[fworker]["launchpad"]
    selection_dict["functional"] = (functional, {})
    selection_dict["kpt_density"] = kpt_density
    selection_dict["nbands"] = nbands
    try:
        selection_dict["nodes_list"] = [int(i) for i in nodes_list.strip(', ').split(',')]
    except ValueError:
        selection_dict["nodes_list"] = None
    
    return selection_dict

def submit_workflows(b):
    
    with output:
        
        output.clear_output()
        selection.update()
        
        try:
            for filename in fu.value.keys():
                file_str = fu.data[0].decode("utf-8")
                spl = filename.split(".")
                if len(spl) == 1:
                    file_fmt = "poscar"
                else:
                    file_fmt = spl[-1]
            
            structure = Structure.from_str(input_string=file_str, fmt=file_fmt)
        
        except UnicodeDecodeError:
            print("Issue with geometry input file.")
            return 
        except UnboundLocalError:
            print("Please select a geometry input file.")
            return
        except ValueError:
            print("Incorrect format for input file.")
            return
        
        try:
            parallelization_dir = os.path.join(
                selection.result["scratch_dir"], "parallel_" + selection.result["functional"][0],
                str(structure.composition).replace(" ", ""),  str(selection.result["nbands"])
                + "bands_" + str(selection.result["kpt_density"]) + "kpoints"
            )
            user_incar_settings.update({"NBANDS": selection.result["nbands"]})
            user_kpoints_settings = {"reciprocal_density": selection.result["kpt_density"]}
        
            for nodes in selection.result["nodes_list"]:
                selection.result["lpad"].add_wf(
                    get_wf_parallel(
                        structure=structure,
                        directory=parallelization_dir,
                        nodes=nodes,
                        nbands=selection.result["nbands"],
                        functional=selection.result["functional"],
                        user_kpoints_settings=user_kpoints_settings,
                        user_incar_settings=user_incar_settings,
                        handlers=handlers,
                        cores_per_node=selection.result["cores_per_node"]
                    )
                )
        except TypeError as t:
            print("Incorrect node list input!")
            return

selection = interactive(selection_interface, 
                        fworker=Select(
                            options=CLUSTER_DICT.keys(),
                            value='leibniz',
                            rows=len(CLUSTER_DICT.keys()),
                            description='Fworker:',
                        ),
                        functional=Select(
                            options=['pbe', 'hse06'],
                            value='pbe',
                            rows=2,
                            description='Functional:',
                        ), 
                        kpt_density=IntSlider(
                            value=300,
                            min=100,
                            max=10000,
                            step=100,
                            description='k-point density:',
                            style = {'description_width': 'initial'}
                        ),
                        nbands=BoundedIntText(
                            value=28,
                            min=1,
                            max=10000,
                            step=1,
                            description='NBANDS:'
                        ),
                        nodes_list=Text(
                            value="1, 2, 4",
                            placeholder='Nodes (comma separated)',
                            description='Node List:',
                        ))

box_layout = Layout(display='flex',
                    align_items='flex-end',
                    width='4cm',
                    position="right")

style = {'description_width': 'initial'}

fu = FileUpload()
button = Button(description="Submit Workflow")
output = Output()

display(fu)
display(HBox(selection.children[:2]))
display(HBox(selection.children[2:4]))
display(HBox(list(selection.children[4:5]) + [HBox(layout=box_layout), button]))
display(output)
button.on_click(submit_workflows)