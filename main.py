import os
import subprocess
import sys
import shutil


def show_menu():
    print("\n=== iNaturalist Tree Generator ===")
    print("1. Собрать данные наблюдений")
    print("2. Сгенерировать визуализацию")
    print("3. Полный цикл (сбор + генерация)")
    print("4. Очистить папку photos")
    print("5. Выход")
    return input("Выберите действие: ")


def run_script(script_name):
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"\n✅ {script_name} выполнен успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при выполнении {script_name}: {e}")
        return False


def clear_photos_folder():
    folder = 'input/photos'
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Не удалось удалить {file_path}. Причина: {e}')
        print("\n🗑️  Папка photos успешно очищена!")
    else:
        print("\n⚠️  Папка photos не существует!")


def main():
    while True:
        choice = show_menu()

        if choice == '1':
            run_script("data_collection.py")

        elif choice == '2':
            if not os.path.exists("input/nodes.pkl"):
                print("\n⚠️  Файл данных не найден! Сначала выполните сбор данных.")
                continue
            run_script("drawio_generator.py")

        elif choice == '3':
            if run_script("data_collection.py"):
                run_script("drawio_generator.py")

        elif choice == '4':
            clear_photos_folder()

        elif choice == '5':
            print("\nДо свидания!")
            break

        else:
            print("\n⚠️  Неверный ввод! Попробуйте снова.")


if __name__ == "__main__":
    main()
