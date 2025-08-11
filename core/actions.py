import ctypes
import webbrowser
from core.path_search import ask_user_choose_path, search_paths_interactive_app, open_path, search_files, search_folder
import os
# from output.speech_output import speak

def execute_action(action_type: str, action_target: str, console_comand: str) -> str:
    try:
        if action_type == "launch_app":
            return search_paths_interactive_app(action_target)
   
        elif action_type == "open_url":
            webbrowser.open(action_target)
            return action_target

        elif action_type == "search_files": 
            paths_found = search_files(action_target)
            if paths_found:
                if len(paths_found) == 1:
                    os.startfile(paths_found[0])
                    return paths_found[0]
                else:
                    chosen = ask_user_choose_path(paths_found)
                    if chosen:
                        os.startfile(chosen)
                        return chosen
                    else:
                        return "Выбор отменён."
            else:
                return "Ничего не найдено."
            
        elif action_type == "open_folder":
            paths_found = search_folder(action_target)
            if paths_found:
                if len(paths_found) == 1:
                    open_path(paths_found[0])
                    return paths_found[0]
                else:
                    chosen = ask_user_choose_path(paths_found)
                    if chosen:
                        open_path(chosen)
                        return chosen
                    else:
                        return "Выбор отменён."
            else:
                return "Ничего не найдено."
            
        elif action_type == "console":
            os.system(console_comand)
            return console_comand
            

        else:
            return "Неизвестный тип действия."

    except Exception as e:
        return "Ошибка при выполнении действия."
    
def BD_actions(action_type, action_target, console_comand):
    try:
        if action_type == "launch_app":
            ctypes.windll.shell32.ShellExecuteW(
                None, None, action_target, None, None, 1
            )
            return "Запускаю!"
        
        elif action_type == "open_url":
            webbrowser.open(action_target)
            return "Открываю!"

        elif action_type == "search_files":
            os.startfile(action_target)
            return "Открываю!"

        elif action_type == "open_folder":
            open_path(action_target)
            return "Открываю!"

        elif action_type == "console":
            os.system(console_comand)
            return "Есть!"

        else:
            return "Неизвестный тип действия."

    except Exception as e:
        return "Ошибка при выполнении действия"