# main.py
import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()


def show_menu():
    print("\n=== iNaturalist Tree Generator ===")
    print("1. Собрать данные наблюдений")
    print("2. Сгенерировать визуализацию")
    print("3. Полный цикл (сбор + генерация)")
    print("4. Выход")
    return input("Выберите действие: ")


def run_script(script_name):
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"\n✅ {script_name} выполнен успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении {script_name}: {e}")
        return False


def main():
    while True:
        choice = show_menu()

        if choice == '1':
            run_script("data_collection.py")

        elif choice == '2':
            if not os.path.exists(os.getenv("pkl_file_name", "nodes.pkl")):
                print("\n⚠ Файл данных не найден! Сначала выполните сбор данных.")
                continue
            run_script("drawio_generator.py")

        elif choice == '3':
            if run_script("data_collection.py"):
                run_script("drawio_generator.py")

        elif choice == '4':
            print("\nДо свидания!")
            break

        else:
            print("\n⚠ Неверный ввод! Попробуйте снова.")


if __name__ == "__main__":
    main()
