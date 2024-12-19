import os
import random

VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm')

def get_video_choices(video_folder):
    video_files=[]

    # Get all the items in the folder, sorted alphabetically
    for item in sorted(os.listdir(video_folder)):
        item_path = os.path.join(video_folder, item)
        
        # If the item is a folder, then we need to go deeper
        if os.path.isdir(item_path):
            item_videos = get_video_choices(item_path)
            video_files.append(item_videos)
            continue

        # If the item is not a video file, then we skip it
        if not item.endswith(VIDEO_EXTENSIONS):
            continue

        # If the item is a video file, then we add it to the list
        video_files.append(item_path)

    return video_files

def shuffle_videos(video_files, result_list=[]):
    def _func(lst, result_list):
        # Get a random item from the list
        random_item = random.choice(lst)

        while True:

            # If the random item is a list, then we need to go deeper
            if isinstance(random_item, list):

                # If the list is empty, remove it from the list
                if len(random_item) == 0:
                    lst.remove(random_item)
                    return
                
                # If the list is not empty, then we need to go deeper
                lst = random_item
                random_item = random.choice(lst)
                continue
            
            # If the random item is a file, then we add it to the result list and remove it from the list
            else:
                result_list.append(random_item)
                lst.remove(random_item)
                break

    # While there are still video files to get, we keep calling
    while video_files:
        _func(video_files, result_list)
    
    return result_list