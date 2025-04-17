import os
import shutil
import subprocess


def extract_frames(video_path, frames_path):
    print(f"Extracting frames from {video_path}")

    outer_path = video_path.split("/")[0: -2]
    stdout_path = os.path.join("/", *outer_path, "output.log")

    ffmpeg_command = ['ffmpeg', '-i', os.path.join(video_path, video_path), f"{frames_path}/%05d.png"]
    with open(stdout_path, "a") as f:
        subprocess.run(ffmpeg_command, stdout=f, stderr=subprocess.STDOUT)

def create_folder_structure(folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print('Created folder:', folder)

def setup_structure(save_path, source_path):
    frames_path = os.path.join(save_path, "camera_frames")
    all_frames_path = os.path.join(save_path, "inputs")
    results_path = os.path.join(save_path, "results")
    cameras_path = os.path.join(save_path, "cameras")

    all_folders = [frames_path, all_frames_path, results_path, cameras_path]
    create_folder_structure(all_folders)

    # copy video folder
    video_path = os.path.join(save_path, "videos")
    video_num = len(os.listdir(source_path))
    shutil.copytree(source_path, video_path)
    print(f"Copying {video_num} videos from {source_path} to {video_path}")

    # extract frames
    for video in os.listdir(video_path):
        video_name, video_ext = os.path.splitext(video)
        new_path = os.path.join(frames_path, video_name)
        os.makedirs(new_path)
        extract_frames(os.path.join(video_path, video), new_path)


    frame_folders = sorted(os.listdir(frames_path))
    folder_paths = [os.path.join(frames_path, folder) for folder in frame_folders]
    folder_files = [sorted(os.listdir(folder)) for folder in folder_paths]

    num_frames = len(folder_files[0])
    num_folders = len(folder_files)

    for frame_counter in range(num_frames):
        frame_counter_folder = os.path.join(all_frames_path, str(frame_counter))
        os.mkdir(frame_counter_folder)

        for i in range(num_folders):
            src_path = os.path.join(folder_paths[i], folder_files[i][frame_counter])
            dest_path = os.path.join(frame_counter_folder, f"{i}.png")
            shutil.copyfile(src_path, dest_path)
