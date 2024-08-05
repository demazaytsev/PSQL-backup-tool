import os
from json import JSONDecodeError, load
import psycopg2


class PSQLBackupTool():
    
    '''
    Cоздание резервных копий объектов БД.
    Поддерживается только работа с СУБД PostgreSQL.
    '''

    class Error(Exception):

        '''Общее исключение для ошибок, возникающих в PSQLBackupTool'''

    def __init__(self) -> None:
        '''
        Побочные действия:
            Установка занчения свойства current_dir_path - 
        '''
        self.current_dir_path: str = os.path.dirname(os.path.realpath(__file__))      


    def create_backup(self) -> None:
        '''
        При вызове метода выполняются следующие действия:
            1. Из файла settings.json извлекаются пользовательские настройки.
            2. Из файла query.sql извлекается SQL запрос, возвращающий таблицу с тремя столбцами:

            первый столбец - описание структуры подкаталогов,
            второй столбец - имя файла,
            третий столбец - содержимое файла.

            3. SQL запрос выполняется для БД, описанной в settings.json.
            4. В соответствии со значениями каждой из строк результирующей таблицы формируется структура каталогов,
            содержащая указанный файл с соответствующим содержимым.
        '''
        SETTINGS_FILE_NAME: str = 'settings.json'
        QUERY_FILE_NAME: str = 'query.sql'

        path_settings: str = os.path.join(self.current_dir_path, SETTINGS_FILE_NAME)
        path_query: str = os.path.join(self.current_dir_path, QUERY_FILE_NAME)
        try:
            with (open(path_settings, 'r', encoding='utf-8') as settings_file, 
                open(path_query, 'r', encoding='utf-8') as query_file):
                # Извлечение словаря с настройками подключения
                settings: dict[str, str | bool | dict[str, str]] = load(settings_file)
                # Извлечение SQL запроса
                query: str = query_file.read()
        except FileNotFoundError as missing_file:
            missing_file_name: str = os.path.basename(missing_file.filename)
            raise self.Error(f'В папке проекта не найден файл "{missing_file_name}"')
        except JSONDecodeError:
            raise self.Error(f'Ошибка чтения "{SETTINGS_FILE_NAME}". Пожалуйста, убедитесь, что в файле "{SETTINGS_FILE_NAME}" содержится действительный JSON-объект')
        try:
            # Настройки для подключения к БД
            connection_settings: dict[str, str] = {key: str(value) for key, value in settings['connection'].items()}
            # Дефолтный каталог, в который помещаются все остальные
            storage_path: str = os.path.normpath(str(settings['storage']))
            real_storage_path: str = os.path.join(self.current_dir_path, storage_path)
            # Нужно ли перезаписывать файл, если по данному пути он уже существует
            overwriting: bool = bool(settings['overwriting'])
            open_mode: str = 'w' if overwriting else 'x'
        except KeyError as key_error:
            raise self.Error(f'Ошибка чтения "{SETTINGS_FILE_NAME}". JSON-объект должен содержать поле "{key_error.args[0]}"')

        print('Подключение к базе данных')

        # Попытка подключения к БД
        try:
            connection: psycopg2.extensions.connection = psycopg2.connect(**connection_settings)
        except (UnicodeDecodeError, psycopg2.Error):
            raise self.Error(f'Вероятно, произошла ошибка подключения к базе данных. Пожалуйста, убедитесь, что в файле {SETTINGS_FILE_NAME} содержатся корректные данные')

        # Выполнение запроса к БД
        try:
            with connection.cursor() as crsr:
                crsr.execute(query)
                result_description: tuple[psycopg2.extensions.Column, ...] = crsr.description
                number_of_columns: int = len(result_description)
                if number_of_columns != 3:
                    raise self.Error(f'Результирующая таблица должна состоять из трех столбцов. Данный запрос возвращает таблицу из {number_of_columns} {self.correct_declension("столбец", number_of_columns)}')
                number_of_rows: int = crsr.rowcount
                if number_of_rows <= 0:
                    raise self.Error('Результирующая таблица не содержит значений')
                for folder_path, file_name, text in crsr:
                    try:
                        folder_path: str = os.path.normpath(str(folder_path))
                        file_name: str = os.path.normpath(str(file_name))
                        text: str = str(text)
                        real_folder_path: str = os.path.join(real_storage_path, folder_path)
                        file_path: str = os.path.join(real_folder_path, file_name)
                        short_file_path: str = os.path.join(storage_path, folder_path, file_name)
                        os.makedirs(real_folder_path, exist_ok=True)
                        with open(file_path, open_mode, encoding='utf-8') as new_file:
                            new_file.write(text)
                        print(f'Файл {short_file_path} успешно создан')
                    except (FileNotFoundError, NotADirectoryError):
                        raise self.Error('Указан некорректный путь к папке. Файлы не были созданы')
                    except FileExistsError:
                        raise self.Error(f'Файл {short_file_path} уже существует. Перезапись по умолчанию отключена')
        except psycopg2.Error:
            raise self.Error('Ошибка обращения к базе данных')
        finally:
                connection.close()
                print('Отключение от базы данных выполнено')

    def correct_declension(
        self,
        word: str,
        number: int
    ) -> str:
        '''
        Нахождение грамматически верной формы существительного 
        в родительном падеже единственного / множественного числа
        в зависомости от числительного, идущего перед ним.

        Параметры:
            word: существительное, для которого необходимо установить верную форму.
            number: числительное, в соответствие которому приводится существительное.

        Исключения:
            Error: для переданного слова отсутствует информация о правилах его склонения.
        '''
        number_str: str = str(number)
        if word == 'столбец':
            if number_str.endswith('1') and not number_str.endswith('11'):
                return 'столбца'
            else:    
                return 'столбцов'
        else:
            raise self.Error(f'Отсутствует информация о правилах склонения слова "{word}"')
        

if __name__ == "__main__":
    PSQLBackupTool().create_backup()
    
