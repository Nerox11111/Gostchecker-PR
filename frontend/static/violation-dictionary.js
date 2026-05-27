window.VIOLATION_DICTIONARY = {
  FONT_FAMILY_INVALID: {
    title: "Неверный шрифт",
    description: "Требуется Times New Roman",
  },
  FONT_SIZE_INVALID: {
    title: "Неверный размер шрифта",
    description: "Размер шрифта должен соответствовать требованиям",
  },
  FONT_STYLE_INVALID: {
    title: "Подчеркивание не допускается",
    description: "Убрать подчеркивание в основном тексте",
  },
  FONT_SPACING_INVALID: {
    title: "Неверные интервалы и отступы",
    description: "Требуется полуторный интервал, отступ 1,25 см, выравнивание по ширине",
  },
  PAGE_SETTINGS_MISSING: {
    title: "Не удалось извлечь параметры страницы",
    description: "Проверьте корректность DOCX и настройки секции",
  },
  PAGE_MARGINS_INVALID: {
    title: "Неверные поля страницы",
    description: "Проверьте размеры полей по ГОСТ",
  },
  STRUCTURAL_ELEMENT_MISSING: {
    title: "Отсутствует обязательный раздел",
    description: "Раздел обязателен для данного типа работы",
  },
  TABLE_CAPTION_INVALID: {
    title: "Неверный формат подписи таблицы",
    description: "Формат: «Таблица N — Наименование»",
  },
  FORMULA_FORMAT_INVALID: {
    title: "Неверное оформление формулы",
    description: "Формула должна быть корректно выровнена и пронумерована",
  },
  LISTING_FORMAT_INVALID: {
    title: "Неверное оформление листинга",
    description: "Проверьте шрифт, размер, интервалы и отступы листинга",
  },
  FIGURE_CAPTION_INVALID: {
    title: "Неверный формат подписи рисунка",
    description: "Формат: «Рисунок N — Наименование»",
  },
  FIGURE_CAPTION_FORMAT_WRONG: {
    title: "\u041d\u0435\u0432\u0435\u0440\u043d\u043e\u0435 \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u0438 \u0440\u0438\u0441\u0443\u043d\u043a\u0430",
    description: "\u041f\u043e\u0434\u043f\u0438\u0441\u044c \u0440\u0438\u0441\u0443\u043d\u043a\u0430 \u0434\u043e\u043b\u0436\u043d\u0430 \u0431\u044b\u0442\u044c \u043f\u043e \u0446\u0435\u043d\u0442\u0440\u0443, \u0431\u0435\u0437 \u043e\u0442\u0441\u0442\u0443\u043f\u0430 \u043f\u0435\u0440\u0432\u043e\u0439 \u0441\u0442\u0440\u043e\u043a\u0438",
  },
  FIGURE_NOT_CENTERED: {
    title: "Рисунок не выровнен по центру",
    description: "Абзац с рисунком должен быть выровнен по центру",
  },
  FIGURE_MISSING_BLANK_BEFORE: {
    title: "\u041d\u0435\u0442 \u043f\u0443\u0441\u0442\u043e\u0439 \u0441\u0442\u0440\u043e\u043a\u0438 \u043f\u0435\u0440\u0435\u0434 \u0440\u0438\u0441\u0443\u043d\u043a\u043e\u043c",
    description: "\u041f\u0435\u0440\u0435\u0434 \u0440\u0438\u0441\u0443\u043d\u043a\u043e\u043c \u043d\u0443\u0436\u043d\u0430 \u043f\u0443\u0441\u0442\u0430\u044f \u0441\u0442\u0440\u043e\u043a\u0430 \u0441 \u0432\u044b\u0440\u0430\u0432\u043d\u0438\u0432\u0430\u043d\u0438\u0435\u043c \u043f\u043e \u0446\u0435\u043d\u0442\u0440\u0443",
  },
  FIGURE_INDENT_WRONG: {
    title: "Неверный отступ у рисунка",
    description: "Абзац с рисунком не должен иметь отступ первой строки",
  },
  LIST_MARKER_WRONG: {
    title: "Неверный маркер списка",
    description: "Для ненумерованного списка используйте длинное тире «—»",
  },
  LIST_NUMBERING_ORDER: {
    title: "Нарушен порядок нумерации списка",
    description: "Нумерация в непрерывном блоке списка должна быть последовательной",
  },
};

window.SEVERITY_LABELS_RU = {
  HIGH: "Ошибка",
  MEDIUM: "Предупреждение",
  LOW: "Рекомендация",
};

