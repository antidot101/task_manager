# JSON REST API сервиса Personal Task Manager

## **Общая информация**

В POST, PUT запросах параметры объектов (наименования и значения полей) передаются в теле запроса (request body).  
Параметры query string указываются только при фильтрации данных.  
Параметры request body и query string можно указывать в любом порядке.  

Сервис Personal Task Manager (PTM) реализован на базе Django Framework, CУБД PostgreSQL.  
JSON REST API выполнен с применением Django Rest Framework.  
Для организации фильтрации использовалось приложение django-filter. 

## **Регистрация**  

**POST /api/register/**  

Пользователь регистрируется в системе, задав пару логин-пароль.

**Описание полей:**
* \* username – уникальное имя пользователя, максимум 150 символов.  
Допускаются только буквы, цифры и символы @ / . + - _ .
* \* password – пароль, минимум 8 символов.  
Не допускаются  слишком простые пароли, а также состоящие только из цифр.  

**request body:**
```javascript
{  
    "username": "FirstPTMUser",  
    "password": "kgllhk&^$"  
}
```
**response:**
```javascript
{  
    "success": "User 'FirstPTMUser' created successfully"  
}
```
## **Авторизация**  

**POST /api/token-auth/**  

Авторизация пользователя осуществляется по токену, переданному **в заголовке Authorization** с ключевым словом Token.  
Пример: **Token 6865ee7edb678629ea561862eee9248aa63a5a25**  
Получить токен можно, передав пару логин-пароль.  
Функционал, предоставляемый сервисом, доступен только авторизованным пользователям.  

**request body:**
```javascript
{
    "username": "FirstPTMUser",
    "password": "kgllhk&^$"
}
```
**response:**  
```javascript
{
    "token": "6865ee7edb678629ea561862eee9248aa63a5a25"
}
```

## **Создание новой задачи**  

**POST  /api/tasks/**  

**Описание полей:**
* \* id – уникальный иденификатор,
* \* task_name – название задачи, максимум 150 символов
* \* description – описание задачи, максимум 1000 символов
* \* creation_date – дата и время создания задачи в формате iso8601
* \* status – статус задачи, одно из значений (New, Planned, In progress, Completed)
* completion_date (необязательное поле) – дата и время завершения задачи в формате iso8601

Передаваемая дата завершения задачи не может быть раньше текущей.  
Если дата завершения задачи не указывается, поле completion_date в запросе следует удалить.  

**request body:**
```javascript
{
     "task_name": "Подготовка к аудиту",
     "description": "Провести совещание с финансовым блоком и бухгалтерий",
     "status": "Planned",
     "completion_date": "2020-10-25T10:00:00.000001Z"
}
```
**response:**  
```javascript
{
    "success": " Task 'Подготовка к аудиту' created successfully",
    "created_task": {
            "id": 1,
            "task_name": "Подготовка к аудиту",
            "description": "Провести совещание с финансовым блоком и бухгалтерий",
            "creation_date": "2020-10-07T22:12:41.903621Z",
            "status": "Planned",
            "completion_date": "2020-10-25T10:00:00.000001Z"
    }
}
```

## **Просмотр списка задач**  
**GET  /api/tasks/**  

В ответе формируется список задач пользователя, отсортированных по дате завершения, начиная с ближайшей.  
Пользователь может просматривать только свои задачи.

**response:**
```javascript
[
    {
        "id": 1,
        "task_name": "Подготовка к аудиту",
        "description": "Провести совещание с финансовым блоком и бухгалтерий",
        "creation_date": "2020-10-05T09:06:13.422311Z",
        "status": "Planned",
        "completion_date": "2020-10-25T10:00:00.000001Z"
    },
    {
        "id": 2,
        "task_name": "To pay taxes",
        "description": "Make an upload from 1C for the reporting period",
        "creation_date": "2020-10-06T10:36:36.056040Z",
        "status": "New",
        "completion_date": "2020-10-10T10:00:00.000001Z"
    },
]
```

## **Фильтрация списка задач** 

**GET  /api/tasks** 

**Параметры query string:**
* id – уникальный иденификатор
* status – статус задачи, одно из значений (New, Planned, In progress, Completed)
* completion_date – дата и время завершения задачи в формате iso8601
* min_date - дата и время завершения задачи, минимальное значение диапазона
* max_date - дата и время завершения задачи, максимальное значение диапазона

Пользователь имеет возможность отфильтровать свой список задач по идентификатору, статусу, дате и времени завершения задачи.  
Фильтрация по дате и времени возможна как с фиксированным значением, так и в диапазонах 
[min_date, ], [, max_date] и [min_date, max_date] включительно.  

**Примеры:**  
* /api/tasks?id=23  
* /api/tasks?status=Planned&completion_date=2020-11-10T10:00:00.000001Z  
* /api/tasks?status=New&min_date=2020-11-10T10:00:00.000001Z  
* /api/tasks?status=New&min_date=2020-11-10T10:00:00.000001Z&max_date=2020-12-01T10:00:00.000001Z  


## **Редактирование задачи**  

**GET  /api/tasks/<task_id:int>** 

По данному запросу можно получить задачу для редактирования с заданным целочисленным идентификатором task_id.

**PUT  /api/tasks/<task_id:int>**  

**Для редактирования доступны следующие поля:**  
* task_name – название задачи, максимум 150 символов
* description – описание задачи, максимум 1000 символов
* status – статус задачи, одно из значений (New, Planned, In progress, Completed)
* completion_date – дата и время завершения задачи в формате iso8601

Изменённая дата завершения задачи не может быть раньше текущей.  

**request body:**
- *изменить название, статус и описание:*  
```javascript
{
    "task_name": "Preparing presentation",
    "description": "To collect materials from departments ...",
    "status": "Completed"
}
```
или  
- *изменить дату завершения:*  
```javascript
{
    "completion_date": "2020-12-25T20:00:00.000001Z"
}
```
**response:**  
```javascript
{
    "success": " Task 'Preparing presentation' updated successfully",
    "updated_task": {
            "id": 3,
            "task_name": "Preparing presentation",
            "description": "To collect materials from departments ...",
            "creation_date": "2020-10-07T22:12:41.903621Z",
            "status": "Completed",
            "completion_date": "2020-12-25T20:00:00.000001Z"
    }
}
```
## **Просмотр истории изменений задачи**  

**GET  /api/tasks/change-history/<task_id:int>**  

task_id - целочисленный идентификатор задачи.  
Список изменений отсортирован по дате изменения, начиная с последнего.  
Помимо полей задачи в ответе присутствуют дополнительные поля:  
* id – идентификатор изменения
* changed_fields – наименования измененных полей или No changes
* change_date – дата и время изменения
* task – идентификатор задачи

Без указания в запросе task_id будет выведена история изменений всех созданных пользователем задач. 
