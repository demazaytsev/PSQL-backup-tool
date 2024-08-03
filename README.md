# PSQL-backup-tool
Утилита для создания резервных копий объектов базы данных PostgreSQL. Основные функции включают в себя извлечение данных из базы данных и сохранение их в файловую систему в соответствии с указанной структурой каталогов.


## Установка
1. Создайте виртуальное окружение:
``` bash
python -m venv venv
```
2. Активируйте виртуальное окружение:
- Для Windows:
```bash
.\venv\Scripts\activate
```
- Для Linux или MacOS:
```bash
source venv/bin/activate
```
3. Установите необходимые зависимости:
```
pip install -r requirements.txt
```

    
## Настройка
1. Отредактируйте файл **settings.json** в корневом каталоге проекта в соответствии с параметрами вашей базы данных.
2. Отредактируйте файл **query.sql** таким образом, чтобы содержащийся в нем SQL-запрос возвращал таблицу с тремя столбцами:
- Путь к файлу относительно параметра "storage", указанного в **settings.json**
- Имя файла
- Содержимое файла
## Использование
Для создания резервной копии выполните команду:
```bash
python psql_backup_tool.py
```
## Пример
Предположим, у вас имеется база данных "fictional_characters_db", содержащая таблицу "cartoon_characters":

id | name | universe | description
--- | --- | --- | ---
1 | Mickey Mouse | Disney | The cheerful and adventurous mouse who is Disney's mascot
2 | Bugs Bunny | Warner Bros | The clever and mischievous rabbit known for his catchphrase "What's up, Doc?"
3 | Donald Duck | Disney | A short-tempered but good-hearted duck who often finds himself in comical situations
4 | Daffy Duck | Warner Bros | The zany and self-absorbed duck who is always getting into trouble
5 | SpongeBob | Nickelodeon | An optimistic and energetic sea sponge who lives in a pineapple under the sea

Файл **settings.json**:
```json
{   
    "connection": 
        {
            "host": "localhost",
            "port": 5432, 
            "database": "fictional_characters_db",
            "user": "your_username",
            "password": "your_password"
        },
    "storage": "backups",
    "overwriting": true
}
```
Файл **query.sql**:
```sql
SELECT
    CASE
        WHEN universe = 'Disney' THEN 'Disney'
        WHEN universe = 'Warner Bros' THEN 'Warner_Bros'
        ELSE 'Other'
    END AS folder_path,
    name AS file_name,
    description AS text
FROM
    cartoon_characters;
```
После запуска утилиты будет сформирована структура каталогов, имеющая следующий вид:
```
backups/
├── Disney
│   ├── Mickey Mouse.txt
│   └── Donald Duck.txt
├── Warner_Bros
│   ├── Bugs Bunny.txt
│   └── Daffy Duck.txt
└── Other
    └── SpongeBob.txt
```
где каждый .txt файл содержит информацию о соответствующем персонаже (поле "description").
