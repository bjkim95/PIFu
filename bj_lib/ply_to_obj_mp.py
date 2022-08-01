from pathlib import Path
import os
import trimesh
import pymeshlab
import xatlas
import argparse
from tqdm import tqdm
import multiprocessing as mp
import parmap
import ipdb
import time

num_cores = mp.cpu_count()

def ply_to_obj(subject):
    start = time.time()
    ms = pymeshlab.MeshSet()
    subject_name = subject.stem[:-4]
    ply_file = str(subject / (subject_name + '_100k.ply'))
    obj_from_ply = str(subject / (subject_name + '.obj'))
    obj_with_uv = str(subject / (subject_name + '_with_uv.obj'))
    obj_final = str(subject / (subject_name + '_100k.obj'))
    tex_dir = subject / 'tex'
    tex_dir.mkdir(exist_ok=True)
    textname = str(tex_dir / (subject_name + '_dif_2k.png'))
    if Path(obj_final).exists() and Path(textname).exists():
        print(f'{subject_name} is already processed!')
        return
    # export ply to obj for meshlab processing
    mesh = trimesh.load_mesh(ply_file)
    mesh.export(obj_from_ply)

    # make uv coordinates
    print(f'uv unwrap {subject_name}')
    if not Path(obj_with_uv).exists():
        vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)
        xatlas.export(obj_with_uv, mesh.vertices[vmapping], indices, uvs)

    # load temp obj file to meshlab and map vertex color to texture
    print(f'map vertex color to texture {subject_name}')
    ms.load_new_mesh(obj_with_uv)
    ms.load_new_mesh(obj_from_ply) 
    ms.transfer_attributes_to_texture_per_vertex(sourcemesh=1, targetmesh=0, textw=2048, texth=2048, textname=textname)
    ms.set_current_mesh(0)
    ms.save_current_mesh(obj_final)

    # remove temp files
    os.remove(obj_from_ply)
    os.remove(obj_with_uv)

    print(f'processing {subject_name} took {time.time() - start}')

    return subject_name

def get_result(result):
    global results
    results.append(result)
    print(f'{len(results)} scans are processed')

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    args = parser.parse_args()
    
    input_dir = Path(args.input)

    ''' >>>apply_async version
    results = [] 
    pool = mp.Pool(num_cores)
    for subject in sorted(input_dir.iterdir()):
        pool.apply_async(ply_to_obj, args=(subject,), callback=get_result)
    pool.close()
    pool.join()
    <<<'''

    parmap.map(ply_to_obj, sorted(input_dir.iterdir()), pm_pbar=True, pm_processes=num_cores)
