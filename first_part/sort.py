import os
import shutil
import concurrent.futures
import threading
from normalization import normalize

thread_count = 0


def move_file(file_path, destination_folder_path, iter_numb):
    try:
        shutil.move(file_path, destination_folder_path)
    except shutil.Error:
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        file_extension = file_extension[1:]
        normalized_file_name = (
            str(iter_numb) + normalize(file_name) + "." + file_extension
        )
        normalized_file_path_new = os.path.join(
            os.path.dirname(file_path), normalized_file_name
        )
        os.rename(file_path, normalized_file_path_new)
        shutil.move(normalized_file_path_new, destination_folder_path)


def process_folder(folder_path):
    image_extensions = ("jpeg", "png", "jpg", "svg")
    video_extensions = ("avi", "mp4", "mov", "mkv")
    document_extensions = ("doc", "docx", "txt", "pdf", "xlsx", "pptx")
    audio_extensions = ("mp3", "ogg", "wav", "amr")
    archive_extensions = ("zip", "gz", "tar")
    known_extensions = set()
    unknown_extensions = set()
    iter_numb = 0
    futures = []

    for root, dirs, files in os.walk(folder_path):
        iter_numb += 1
        if any(
            folder in root
            for folder in ["archives", "video", "audio", "documents", "images"]
        ):
            continue

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_name_splitted = file_name.split(".")
                file_extension = file_name_splitted.pop(-1)
                file_name = ""
                for name in file_name_splitted:
                    file_name += name
                normalized_file_name = normalize(file_name) + "." + file_extension
                normalized_file_path = os.path.join(root, normalized_file_name)
                os.rename(file_path, normalized_file_path)

                if file_extension in image_extensions:
                    destination_folder = "images"
                    known_extensions.add(file_extension)
                elif file_extension in video_extensions:
                    destination_folder = "video"
                    known_extensions.add(file_extension)
                elif file_extension in document_extensions:
                    destination_folder = "documents"
                    known_extensions.add(file_extension)
                elif file_extension in audio_extensions:
                    destination_folder = "audio"
                    known_extensions.add(file_extension)
                elif file_extension in archive_extensions:
                    destination_folder = "archives"
                    known_extensions.add(file_extension)
                    destination_folder = os.path.join(folder_path, destination_folder)
                    destination_folder = os.path.join(destination_folder, file_name)
                    shutil.unpack_archive(normalized_file_path, destination_folder)
                    os.remove(normalized_file_path)
                    continue
                else:
                    destination_folder = "unknown"
                    unknown_extensions.add(file_extension)

                destination_folder_path = os.path.join(folder_path, destination_folder)
                os.makedirs(destination_folder_path, exist_ok=True)

                future = executor.submit(
                    move_file, normalized_file_path, destination_folder_path, iter_numb
                )
                futures.append(future)
                global thread_count
                thread_count += 1

            concurrent.futures.wait(futures)

    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            folder_path = os.path.join(root, dir)
            if folder_path not in [
                "archives",
                "video",
                "audio",
                "documents",
                "images",
            ] and not os.listdir(folder_path):
                os.removedirs(folder_path)

    if not known_extensions:
        known_extensions = "не обнаружено."
    if not unknown_extensions:
        unknown_extensions = "не обнаружено."

    return known_extensions, unknown_extensions


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Введите путь к папке")
        sys.exit(1)

    folder_path = sys.argv[1]
    known_extensions, unknown_extensions = process_folder(folder_path)
    print(
        f"Известные расширения:{known_extensions}\nНеизвестные расширения:{unknown_extensions}"
    )

    print(f"Количество задействованных потоков: {thread_count}")
