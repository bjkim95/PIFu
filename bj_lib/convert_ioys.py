from pathlib import Path
import argparse
from shutil import copyfile
import pdb

action_kr_to_eng = {'도전적동작':'challenging', '기본동작_대화':'talking', '기본동작_뛰기': 'jumping', '기본동작_박수':'clap', '기본동작_인사':'hello', '기본동작_걷기':'walking', 
                    '응용동작_스포츠':'sports', '응용동작_커머스':'commerce', '응용동작_화상회의':'meeting', '응용동작_재활운동':'rehab', '응용동작_국민체조':'kukmin', '응용동작_홈트레이닝':'hometraining', 
                    '응용동작_국민건강체조':'kunkang', '응용동작_코로나예방수칙':'covid'}
subaction_kr_to_eng = {'복싱':'boxing', '두 팔 교차':'armcross', '마주보고 서서':'standing', '제자리': 'inplace', '한발로 제자리':'oneleg', '마주보며 앞으로':'front', '마주보며 위아래로': 'updown',
                       '고개': 'bow', '악수': 'handshake', '경례':'salute', '손인사':'hi', '주먹인사':'fist', '하이파이브':'hifive', '나란히 걷기': 'straight', '골프': 'golf', '볼링':'bowling', '축구': 'soccer', '탁구':'pingpong', '배드민턴': 'badminton',
                       '물건 주고받기':'handover', '메모':'memo', '발표':'presenting', '질문 (손 들기)': 'question', '양손 번갈아 위아래 흔들기':'armalter', '양손 공 주고받기':'twohandpass', '손 위로 좌우 흔들기' :'waving', '한 손 공 주고받기': 'onehandpass',
                       '노젓기':'rowing', '가슴젖히기':'chestup', '목휘둘리기':'rotateneck', '무릎굽혀 펴기':'bendknee1', '팔들어 숨쉬기':'breathing', '몸통 옆으로 틀기': 'twistbody', '몸 옆으로 굽히기':'bendbody', 
                       '팔 앞뒤로 들어 옆으로 내리기(숨쉬기)':'breathing', '팔 흔들며 무릅 굽혀 펴고들기':'bendknee2',
                       '팔 들어 흔들어 앞뒤로 휘둘리기': 'rotatearm', '런지':'lunge', '스쿼트':'squat', '기펴기':'unfold', '날개펴기':'wing', '금강막기':'kumkang', '꼬아서기':'twist', '앞뒷굽이':'frontback', '주먹지르기':'fist', '가볍게 뛰기':'hop', '몸틀어 손날치기':'knifehand', 
                       '어깨 돌리기':'shoulder', '소매기침':'cough', '손바닥 기침':'palmcough', '간격 두고 줄서기':'lineup'}  # 53 poses

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='/home/byungjunkim/storage1/datasets/ioys/Training')
    parser.add_argument('-o', '--output', type=str, default='/home/byungjunkim/storage1/datasets/ioys_pifu_raw')
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    for action in input_dir.iterdir():
        if action.is_dir():
            for subaction in action.iterdir():
                for sample_obj in subaction.glob('*.obj'):
                    sample_tex = subaction / (sample_obj.stem + '.jpg')
                    sample_mtl = subaction / (sample_obj.stem + '.mtl')
                    if (not sample_tex.exists()) or (not sample_mtl.exists()): # if something is missing
                        continue
                    action_name = action_kr_to_eng[action.stem[14:]]
                    subaction_name = subaction_kr_to_eng[subaction.stem]
                    sample_index = sample_obj.stem[-5:-2]
                    sample_name = '_'.join([sample_index, action_name, subaction_name])
                    obj_dir = output_dir / (sample_name + '_OBJ')
                    tex_dir = obj_dir / 'tex'
                    obj_dir.mkdir(exist_ok=True)
                    tex_dir.mkdir(exist_ok=True)

                    copied_obj_name = sample_name + '_100k.obj'
                    copied_tex_name = sample_name + '_dif_2k.jpg'
                    copied_mtl_name = sample_name + '.mtl'
                    copied_obj_path = obj_dir / copied_obj_name
                    copied_tex_path = tex_dir / copied_tex_name
                    copied_mtl_path = obj_dir / copied_mtl_name
                    if not copied_obj_path.exists():
                        copyfile(str(sample_obj), str(copied_obj_path))
                    if not copied_tex_path.exists():
                        copyfile(str(sample_tex), str(copied_tex_path))
                    if not copied_mtl_path.exists():
                        copyfile(str(sample_mtl), str(copied_mtl_path))

                    # edit obj file and mtl fime due to file name change
                    with open(copied_obj_path, 'r') as obj:
                        obj_data = obj.readlines()
                        obj_data[11] = f'mtllib ./{copied_mtl_name}\n'
                        new_obj_contents = ''.join(obj_data)
                    with open(copied_obj_path, 'w') as new_obj:
                        new_obj.write(new_obj_contents)

                    with open(copied_mtl_path, 'r') as mtl:
                        mtl_data = mtl.readlines()
                        mtl_data[12] = f'tex/map_Kd {copied_tex_name}\n'
                        new_mtl_contents = ''.join(mtl_data)
                    with open(copied_mtl_path, 'w') as new_mtl:
                        new_mtl.write(new_mtl_contents)
