# 🔍 Диагностика проблемы 404 на фронтенде

## ✅ Backend проверен - работает!

```bash
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/
# Возвращает: 401 Unauthorized ✅ (endpoint найден)
```

## 🔍 Что проверить на фронтенде:

### 1. Очистить кеш браузера

**Chrome/Edge:**

1. Открыть DevTools (F12)
2. Правый клик на кнопке обновления страницы
3. Выбрать "**Очистить кеш и жесткая перезагрузка**" (Empty Cache and Hard Reload)

**Или:**

- `Cmd + Shift + R` (macOS)
- `Ctrl + Shift + R` (Windows/Linux)

### 2. Проверить Network Tab

1. Открыть DevTools (F12)
2. Вкладка **Network**
3. Поставить галочку "**Disable cache**"
4. Нажать на кнопку сохранения оценок
5. Найти запрос `bulk-update`
6. Проверить:
   - **URL** - должен быть `result/api/lecturer/bulk-grades/bulk-update/` (с дефисами!)
   - **Status** - должен быть 401 или 200, НЕ 404
   - **Headers** → Request Headers → Authorization - должен быть `Bearer <token>`

### 3. Проверить Console

Откройте Console (F12) и выполните:

```javascript
// 1. Проверить что API настроен правильно
console.log("API file loaded:", typeof api !== "undefined");

// 2. Проверить базовый URL
import api from "./api.js";
console.log("Base URL:", api.defaults.baseURL);

// 3. Проверить токен
console.log(
  "Access Token:",
  localStorage.getItem("access") ? "EXISTS ✅" : "MISSING ❌"
);

// 4. Проверить что токен добавляется в запросы
api.interceptors.request.use((config) => {
  console.log("🚀 Request:", config.method.toUpperCase(), config.url);
  console.log("🔐 Auth header:", config.headers.Authorization);
  return config;
});
```

### 4. Проверить исходный код компонента

Откройте DevTools → Sources → найдите `TeacherGradesPage.jsx` и проверьте что URL правильный:

```javascript
// Должно быть:
api.post('result/api/lecturer/bulk-grades/bulk-update/', ...)

// НЕ должно быть:
api.post('result/api/lecturer/bulk-grades/bulk_update/', ...)  // ❌ подчеркивания
api.post('/result/api/lecturer/bulk-grades/bulk-update/', ...) // ❌ начальный слеш
```

### 5. Перезапустить Vite dev server

```bash
# Терминал с фронтендом
# Нажать Ctrl+C

cd ~/Desktop/projects/SkyLearn/skyfront

# Очистить кеш Vite
rm -rf node_modules/.vite

# Перезапустить
npm run dev
```

### 6. Проверить что backend запущен на правильном порту

```bash
# Проверить что Django работает
curl http://localhost:8000/admin/
# Должна вернуться HTML страница
```

### 7. Временно добавить логирование в код

Откройте `skyfront/src/pages/crud/teacher/TeacherGradesPage.jsx` и добавьте:

```javascript
const response = await api.post(
  "result/api/lecturer/bulk-grades/bulk-update/",
  bulkData
);

// Добавьте ДО запроса:
console.log(
  "🔍 URL будет:",
  api.defaults.baseURL + "result/api/lecturer/bulk-grades/bulk-update/"
);
console.log(
  "🔍 Token будет:",
  localStorage.getItem("access") ? "ДА ✅" : "НЕТ ❌"
);

const response = await api.post(
  "result/api/lecturer/bulk-grades/bulk-update/",
  bulkData
);
```

Сохраните, подождите HMR (Hot Module Replacement), и попробуйте снова.

## 🎯 Быстрая диагностика

В консоли браузера (F12 → Console) выполните:

```javascript
// Полная диагностика
(async function () {
  console.log("=".repeat(60));
  console.log("ДИАГНОСТИКА BULK UPDATE");
  console.log("=".repeat(60));

  // 1. Проверка токена
  const token = localStorage.getItem("access");
  console.log("1️⃣ Token exists:", token ? "YES ✅" : "NO ❌");
  if (token) {
    console.log("   Token preview:", token.substring(0, 30) + "...");
  }

  // 2. Проверка endpoint БЕЗ токена
  try {
    const response = await fetch(
      "http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          course_id: 1,
          grade_type: "1st_module",
          grades: [],
        }),
      }
    );
    console.log("2️⃣ Endpoint status:", response.status);
    if (response.status === 401) {
      console.log("   ✅ Backend работает! (нужен токен)");
    } else if (response.status === 404) {
      console.log("   ❌ Backend НЕ работает! (404 Not Found)");
    }
  } catch (e) {
    console.log("2️⃣ ❌ Ошибка соединения:", e.message);
  }

  // 3. Проверка endpoint С токеном
  if (token) {
    try {
      const response = await fetch(
        "http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
          body: JSON.stringify({
            course_id: 1,
            grade_type: "1st_module",
            grades: [],
          }),
        }
      );
      console.log("3️⃣ С токеном status:", response.status);
      const data = await response.json();
      console.log("   Response:", data);
    } catch (e) {
      console.log("3️⃣ ❌ Ошибка:", e.message);
    }
  }

  console.log("=".repeat(60));
})();
```

## ✅ Ожидаемые результаты:

- **Шаг 1:** Token EXISTS ✅
- **Шаг 2:** Endpoint status: 401 ✅ (означает что endpoint работает)
- **Шаг 3:** Статус 200 или 400 (в зависимости от данных)

## ❌ Если видите 404:

1. **Backend не перезагрузился** → Перезапустите Django
2. **Неправильный URL в запросе** → Проверьте Network tab
3. **Старый кеш браузера** → Очистите кеш

## 🔄 Полный перезапуск:

```bash
# Терминал 1: Backend
pkill -9 -f "manage.py runserver"
cd ~/Desktop/projects/SkyLearn
source venv/bin/activate
rm -rf result/__pycache__
python manage.py runserver

# Терминал 2: Frontend
cd ~/Desktop/projects/SkyLearn/skyfront
# Ctrl+C если запущен
rm -rf node_modules/.vite
npm run dev

# Терминал 3: Проверка
curl -X POST http://localhost:8000/result/api/lecturer/bulk-grades/bulk-update/ \
  -H "Content-Type: application/json" -d '{}'
# Должно вернуть 401 ✅
```

## 📞 После проверки:

Напишите что показали:

1. Network tab → Status code
2. Network tab → Request URL
3. Console → Диагностика скрипта
4. Sources → URL в коде

Это поможет точно определить проблему!
