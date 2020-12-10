from make_list import make_train_test

import os
import subprocess
from tqdm import tqdm
import multiprocessing
from functools import partial


def extract_frames(vid_dir, frame_dir, redo=False):
    class_list = sorted(os.listdir(vid_dir))

    print("Classes =", class_list)

    for ic, cls in enumerate(class_list):
        video_list = sorted(os.listdir(vid_dir + cls))
        print(ic + 1, len(class_list), cls, len(video_list))
        for video in tqdm(video_list):
            out_dir = os.path.join(frame_dir, cls, video[:-4])

            # Checking if frames already extracted
            if os.path.isfile(os.path.join(out_dir, 'done')) and not redo:
                continue
            try:
                os.system('mkdir -p "%s"' % out_dir)
                # check if horizontal or vertical scaling factor
                # This command used to get the width and height pixel. Output will be: width=xxx\nheight=xxx\n
                command = 'ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 "%s"' % \
                          (os.path.join(vid_dir, cls, video))
                o = subprocess.check_output(command, shell=True).decode('utf-8')
                lines = o.splitlines()
                width = int(lines[0].split('=')[1])
                height = int(lines[1].split('=')[1])
                resize_str = '-1:256' if width > height else '256:-1'

                # extract frames to out_dir
                os.system('ffmpeg -i "%s" -r 10 -q:v 2 -vf "scale=%s" "%s"  > /dev/null 2>&1' %
                          (os.path.join(vid_dir, cls, video), resize_str, os.path.join(out_dir, '%05d.jpg')))
                nframes = len([fname for fname in os.listdir(out_dir) if fname.endswith('.jpg') and len(fname) == 9])
                if nframes == 0:
                    raise Exception
                os.system('touch "%s"' % (os.path.join(out_dir, 'done')))
            except:
                print("ERROR", cls, video)


def mul_resize(source_dir, output_dir, video):
    if not video.endswith('mp4'):
        return False
    video_path = os.path.join(source_dir, video)
    # This command used to get the width and height pixel. Output will be: width=xxx\nheight=xxx\n
    command = 'ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1 "%s"' % video_path
    out = subprocess.check_output(command, shell=True).decode('utf-8')
    lines = out.splitlines()
    width = int(lines[0].split('=')[1])
    height = int(lines[1].split('=')[1])
    resize_str = '-1:256' if width > height else '256:-1'

    command = 'ffmpeg -hide_banner -loglevel panic -y -i {} -pix_fmt yuv444p -filter:v scale={} -c:a copy {} > /dev/null 2>&1'.format(
        video_path, resize_str, os.path.join(output_dir, video)
    )
    os.system(command)


def resize_videos(source_dir, output_dir):
    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    func = partial(mul_resize, source_dir, output_dir)
    pool = multiprocessing.Pool(8)
    pool.map(func, os.listdir(source_dir))
    pool.close()
    pool.join()
    # recursively resize the sub directory
    dir_list = [name for name in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, name))]
    if dir_list:
        for directory in dir_list:
            resize_videos(os.path.join(source_dir, directory), os.path.join(output_dir, directory))
    # for video in os.listdir(source_dir):


def main():
    # source_case_path = '/data/jojen/dataset_5/pre/pre_case'
    # resized_case_path = '/data/jojen/dataset_5/resized/pre_case'
    source_case_path = '/data/jojen/dataset6/source'
    resized_case_path = '/data/jojen/dataset6/resized'
    resize_videos(source_case_path, resized_case_path)

    # source_control_path = '/data/jojen/model_validation/pre/extract_control'
    # resized_control_path = '/data/jojen/model_validation/resized/extract_control'
    # resize_videos(source_control_path, resized_control_path)

    # train_txt = '/data/jojen/model_validation/train_validation.txt'
    # test_case_txt = '/data/jojen/model_validation/val_case.txt'
    # test_ctl_txt = '/data/jojen/model_validation/val_control.txt'
    # make_train_test(resized_case_path, resized_control_path, train_txt, test_case_txt, test_ctl_txt, train_ratio=1)


if __name__ == '__main__':
    main()
