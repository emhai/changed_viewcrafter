import os
import shutil
import subprocess

import cv2


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


def create_video(input_folder):

    name = os.path.basename(input_folder)
    outer_folder = os.path.dirname(input_folder)
    video_name = f"{name}.mp4"
    video_path = os.path.join(outer_folder, video_name)

    images = sorted(os.listdir(input_folder), key=lambda x: int(os.path.splitext(x)[0]))
    frame = cv2.imread(os.path.join(input_folder, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # You can also try 'avc1'
    fps = 30  # Adjust frame rate as needed
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    # Write images to video
    for image in images:
        img_path = os.path.join(input_folder, image)
        frame = cv2.imread(img_path)
        video.write(frame)

    # Release resources
    video.release()
    cv2.destroyAllWindows()

def extract_renders(results_folder):
    # extract frames
    for folder in os.listdir(results_folder):
        if not os.path.isdir(os.path.join(results_folder, folder)):
            continue


        video_path = os.path.join(results_folder, folder, "render.mp4")
        new_path = os.path.join(results_folder, folder, "render_frames")
        os.makedirs(new_path)
        extract_frames(video_path, new_path)


def separate_cameras(results_folder, cameras_folder):
    frame_types = ["diffusion_frames", "render_frames"]
    for frame_number in os.listdir(results_folder):
        if not os.path.isdir(os.path.join(results_folder, frame_number)):
            continue


        for frame_type in frame_types:
            frame_folder = os.path.join(results_folder, frame_number, frame_type)
            for camera in os.listdir(frame_folder):
                file_name = os.path.join(frame_folder, camera)
                name, ext = os.path.splitext(camera)

                name_folder = os.path.join(cameras_folder, frame_type, f"{name}")
                print(name_folder, "--", file_name)
                if not os.path.exists(name_folder):
                    os.makedirs(name_folder)

                shutil.copyfile(file_name, f"{name_folder}/{frame_number}.png")

    for frame_type in frame_types:
        camera_files = [f for f in os.listdir(os.path.join(cameras_folder, frame_type))]
        for file in camera_files:
            create_video(os.path.join(cameras_folder, frame_type, file))
#
# def main():
#     results_folder = "/media/emmahaidacher/Volume/RESULTS/espresso_renders/results"
#     cameras_folder = "/media/emmahaidacher/Volume/RESULTS/espresso_renders/cameras"
#     separate_cameras(results_folder, cameras_folder)
#
# if __name__ == "__main__":
#     main()