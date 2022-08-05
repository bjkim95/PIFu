import argparse
from pathlib import Path
import random

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='/home/shunsuke/Downloads/rp_dennis_posed_004_OBJ')
    parser.add_argument('-r', '--test_ratio',  type=int, default=0.1, help='ratio of test set')
    args = parser.parse_args()

    data_dir = Path(args.input)
    render_dir = data_dir / 'RENDER'
    data = list(sorted(render_dir.iterdir()))
    num_test = int(len(data) * args.test_ratio)

    testset = random.sample(data, num_test)
    testset_names = [path.stem for path in testset]

    output_path = data_dir / 'val.txt'
    with open(output_path, 'w') as f:
        f.write('\n'.join(testset_names))
