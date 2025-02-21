import os
import numpy as np
import imageio
import logging
import glob

logger = logging.getLogger(__package__)

########################################################################################################################
# camera coordinate system: x-->right, y-->down, z-->scene (opencv/colmap convention)
# poses is camera-to-world
########################################################################################################################


def find_files(dir, exts):
    if os.path.isdir(dir):
        # types should be ['*.png', '*.jpg']
        files_grabbed = []
        for ext in exts:
            files_grabbed.extend(glob.glob(os.path.join(dir, ext)))
        if len(files_grabbed) > 0:
            files_grabbed = sorted(files_grabbed)
        return files_grabbed
    else:
        return []

def parse_txt(filename):
    assert os.path.isfile(filename)
    nums = open(filename).read().split()
    return np.array([float(x) for x in nums]).reshape([4, 4]).astype(np.float32)

def load_data_split(basedir, scene, split, skip=1, try_load_min_depth=True, only_img_files=False):


    if basedir[-1] == '/':          # remove trailing '/'
        basedir = basedir[:-1]

    split_dir = f'{basedir}/{scene}/{split}'

    if only_img_files:
        img_files = find_files(f'{split_dir}/rgb', exts=['*.png', '*.jpg'])
        return img_files

    # camera parameters files
    intrinsics_files = find_files(f'{split_dir}/intrinsics', exts=['*.txt'])
    pose_files = find_files(f'{split_dir}/pose', exts=['*.txt'])
    logger.info(f'{split} intrinsics_files: {len(intrinsics_files)}')
    logger.info(f'{split} pose_files: {len(pose_files)}')

    intrinsics_files = intrinsics_files[::skip]
    pose_files = pose_files[::skip]
    cam_cnt = len(pose_files)

    # img files
    img_files = find_files(f'{split_dir}/rgb', exts=['*.png', '*.jpg'])
    if len(img_files) > 0:
        logger.info(f'{split} img_files: {len(img_files)}')
        img_files = img_files[::skip]
        assert(len(img_files) == cam_cnt)
    else:
        img_files = [None, ] * cam_cnt

    # mask files
    mask_files = find_files(f'{split_dir}/mask',
                            exts=['*.png', '*.jpg'])
    if len(mask_files) > 0:
        logger.info(f'{split} mask_files: {len(mask_files)}')
        mask_files = mask_files[::skip]
        assert(len(mask_files) == cam_cnt)
    else:
        mask_files = [None, ] * cam_cnt

    # min depth files
    mindepth_files = find_files(
        f'{split_dir}/min_depth', exts=['*.png', '*.jpg'])
    if try_load_min_depth and len(mindepth_files) > 0:
        logger.info(f'{split} mindepth_files: {len(mindepth_files)}')
        mindepth_files = mindepth_files[::skip]
        assert(len(mindepth_files) == cam_cnt)
    else:
        mindepth_files = [None, ] * cam_cnt

    # assume all images have the same size as training image
    train_imgfile = find_files(
        f'{basedir}/{scene}/train/rgb', exts=['*.png', '*.jpg'])[0]
    train_im = imageio.imread(train_imgfile)
    H, W = train_im.shape[:2]

    try:
        max_depth = float(open(f'{split_dir}/max_depth.txt').readline().strip())
    except:
        max_depth = None

    return [H, W], intrinsics_files, pose_files, img_files, mask_files, mindepth_files, max_depth

    # create ray samplers
    # ray_samplers = []
    # for i in range(cam_cnt):
    #     intrinsics = parse_txt(intrinsics_files[i])
    #     pose = parse_txt(pose_files[i])
    #     # read max depth
    #     try:
    #         max_depth = float(
    #             open(f'{split_dir}/max_depth.txt').readline().strip())
    #     except:
    #         max_depth = None

    #     ray_samplers.append(RaySamplerSingleImage(H=H, W=W, intrinsics=intrinsics, c2w=pose,
    #                                               img_path=img_files[i],
    #                                               resolution_level=2,
    #                                               mask_path=mask_files[i],
    #                                               min_depth_path=mindepth_files[i],
    #                                               max_depth=max_depth))
    # logger.info(f'Split {split}, # views: {cam_cnt}')

    # return ray_samplers
