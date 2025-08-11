import os
import string
import subprocess
import ctypes
# from output.speech_output import speak
from input.vad import lisen_nunder
from core.semantic_cleaner import num_cliener

def get_all_disks():
    return [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

def search_folder(target_name):
    found = []
    # speak(f"Поиск папки {target_name}")
    print(f"🔍 Поиск папки: '{target_name}'")
    for disk in get_all_disks():
        print(f"   📂 Диск {disk}...")
        for root, dirs, _ in os.walk(disk):
            for name in dirs:
                if name.lower() == target_name.lower():
                    found.append(os.path.join(root, name))
    return found

def search_files(target_name):
    found = []
    # speak(f"Поиск файла {target_name}")
    print(f"🔍 Поиск файла: '{target_name}.*'")
    for disk in get_all_disks():
        print(f"   📁 Диск {disk}...")
        for root, _, files in os.walk(disk):
            for file in files:
                name, _ = os.path.splitext(file)
                if name.lower() == target_name.lower():
                    found.append(os.path.join(root, file))
    return found

def search_applications(target_name):
    found = []
    # speak(f"Поиск приложения {target_name}")
    print(f"🔍 Поиск приложения: '{target_name}.exe'")
    for disk in get_all_disks():
        print(f"   📁 Диск {disk}...")
        for root, _, files in os.walk(disk):
            for file in files:
                if file.lower() == target_name.lower() + ".exe":
                    found.append(os.path.join(root, file))
    return found

def open_path(path):
    if os.path.isdir(path):
        subprocess.run(f'explorer "{path}"')
    elif os.path.isfile(path):
        subprocess.run(f'explorer /select,"{path}"')

def ask_user_choose_path(paths):
    # speak("Найдено несколько вариантов")
    # speak("Скажи по какому пути мне открыть файл")
    print("\n🔎 Найдено несколько вариантов:")
    for i, path in enumerate(paths, 1):
        print(f"{i}) {path}")
    while True:
        print("\n👉 Выберите номер (или 0 для отмены): ")
        choice = num_cliener(lisen_nunder())
        print(choice)
        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                return None
            if 1 <= idx <= len(paths):
                return paths[idx - 1]
        print("❌ Некорректный выбор.")
        # speak("Некорректный выбор")


def search_paths_interactive_folder(target_name: str):
    folders = search_folder(target_name)
    if not folders:
        # speak("Папка не найдена")
        print("\n❌ Папки не найдены.")
        return None

    print(f"\n✅ Найдено папок: {len(folders)}")
    if len(folders) == 1:
        open_path(folders[0])
        return folders[0]

    chosen = ask_user_choose_path(folders)
    if chosen:
        open_path(chosen)
        return chosen
    return None

def search_paths_interactive_file(target_name: str):
    files = search_files(target_name)
    if not files:
        # speak("Файл не найден")
        print("\n❌ Файлы не найдены.")
        return None

    print(f"\n✅ Найдено файлов: {len(files)}")
    if len(files) == 1:
        open_path(files[0])
        return files[0]

    chosen = ask_user_choose_path(files)
    if chosen:
        open_path(chosen)
        return chosen
    return None

def search_paths_interactive_app(target_name: str):
    apps = search_applications(target_name)
    if not apps:
        # speak("Приложение не найдено")
        print("\n❌ Приложения не найдены.")
        return "Приложение не найдено"

    def launch(path):
        try:
            print(f"[DEBUG] Что запускаем: {path}")
            ctypes.windll.shell32.ShellExecuteW(
                None, None, path, None, None, 1
            )
            return path
        except Exception as e:
            print(f"⚠️ Ошибка запуска: {e}")

    launch(apps[0])

    return apps[0]




