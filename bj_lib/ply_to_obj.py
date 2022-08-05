from pathlib import Path
import os
import trimesh
import pymeshlab
import xatlas
import argparse
from tqdm import tqdm
import ipdb

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    args = parser.parse_args()

    input_dir = Path(args.input)
    for subject in tqdm(sorted(input_dir.iterdir())):
        ms = pymeshlab.MeshSet()
        subject_name = subject.stem[:-4]
        ply_file = str(subject / (subject_name + '_100k.ply'))
        obj_from_ply = str(subject / (subject_name + '.obj'))
        obj_with_uv = str(subject / (subject_name + '_with_uv.obj'))
        obj_final = str(subject / (subject_name + '_100k.obj'))
        tex_dir = subject / 'tex'
        tex_dir.mkdir(exist_ok=True)
        textname = './' + subject_name + '_dif_2k.png'
        if Path(obj_final).exists() and Path(textname).exists():
            continue

        # export ply to obj for meshlab processing
        mesh = trimesh.load_mesh(ply_file)
        mesh.export(obj_from_ply)

        # make uv coordinates
        print('uv unwrap')
        if not Path(obj_with_uv).exists():
            vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)
            xatlas.export(obj_with_uv, mesh.vertices[vmapping], indices, uvs)

        # load temp obj file to meshlab and map vertex color to texture
        print('map vertex color to texture')
        ms.load_new_mesh(obj_with_uv)
        ms.load_new_mesh(obj_from_ply) 
        ms.transfer_attributes_to_texture_per_vertex(sourcemesh=1, targetmesh=0, textw=2048, texth=2048, textname=textname)
        ms.set_current_mesh(0)
        ms.save_current_mesh(obj_final)

        # remove temp files
        os.remove(obj_from_ply)
        os.remove(obj_with_uv)

        # add extension to the final obj file
        shutil.move(obj_final, obj_final)
