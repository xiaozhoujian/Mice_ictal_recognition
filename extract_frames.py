"""
For HMDB51 and UCF101 datasets:

Code extracts frames from video at a rate of 25fps and scaling the
larger dimension of the frame is scaled to 256 pixels.
After extraction of all frames write a "done" file to signify proper completion
of frame extraction.

Usage:
  python extract_frames.py video_dir frame_dir
  
  video_dir => path of video files
  frame_dir => path of extracted jpg frames

"""

import os
import subprocess
from tqdm import tqdm


def extract_frames(vid_dir, frame_dir, redo=False):
    class_list = sorted(os.listdir(vid_dir))

    print("Classes =", class_list)

    for ic, cls in enumerate(class_list):
        video_list = sorted(os.listdir(vid_dir + cls))
        print(ic+1, len(class_list), cls, len(video_list))
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


# def main():
#     vid_dir = './mice_2020-03-20/'
#     frame_dir = './mice_0320-1f/'
#
#     extract(vid_dir, frame_dir, redo=True)
#
#
# if __name__ == '__main__':
#     main()
