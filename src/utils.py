import os

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm")


def get_folder_videos(folder):
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in VIDEO_EXTENSIONS):
                files.append(os.path.join(root, filename))
    return files
