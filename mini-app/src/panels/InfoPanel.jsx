import { Panel, PanelHeader, PanelHeaderBack, Div } from '@vkontakte/vkui';
import { useRouteNavigator } from '@vkontakte/vk-mini-apps-router';
import PropTypes from 'prop-types';

const CONTENT = {
  ml: {
    title: 'Классификатор',
    kicker: 'Определение типа документа и режима проверки',
    lead: 'Backend извлекает из DOCX 16 числовых признаков, передает их RandomForest-модели и получает тип документа, режим LIGHT/MEDIUM/HARD и confidence. Если модель недоступна, включается резервная эвристика, но production-сценарий рассчитан на classifier.joblib.',
    cards: [
      {
        title: 'Что извлекается из DOCX',
        text: 'Модуль app/ml/features.py читает документ через python-docx и считает признаки, которые устойчиво доступны без ручной разметки.',
        items: ['условное число страниц', 'глубина заголовков 1 / 1.1 / 1.1.1', 'наличие содержания, введения, заключения, реферата', 'количество таблиц, рисунков, формул, источников и приложений', 'корректность полей, объем текста и средняя длина абзаца'],
      },
      {
        title: 'Какие классы поддерживаются',
        text: 'Модель классифицирует 8 типов учебных и научных документов. От типа зависит рекомендуемый режим проверки.',
        items: ['lab_work и practice -> LIGHT', 'internship и coursework -> MEDIUM', 'thesis_bachelor и thesis_master -> HARD', 'scientific_rpt и rnd_nir -> HARD'],
      },
      {
        title: 'Как обучается модель',
        text: 'Скрипты scripts/extract_features.py и scripts/train_classifier.py формируют dataset.csv и обучают RandomForestClassifier. Стартовая bootstrap-модель нужна только для первого запуска.',
        items: ['минимум 50-100 DOCX на каждый класс', 'macro F1 на тесте не ниже 0.85', 'ни один класс не ниже F1 0.70', '5-fold macro F1 не ниже 0.82'],
      },
    ],
    flow: ['DOCX', 'features.py', '16 признаков', 'RandomForest', 'doc_type', 'mode'],
  },
  gost: {
    title: 'ГОСТ-правила',
    kicker: 'Проверка и исправление DOCX',
    lead: 'Текущая версия запускает FastAPI-метод /api/run: документ автоматически классифицируется, получает профиль LIGHT/MEDIUM/HARD, затем проходит набор чекеров по полям, шрифтам, структуре, таблицам, рисункам, формулам, листингам и спискам.',
    paper: true,
    cards: [
      {
        title: 'LIGHT',
        text: 'Базовый режим для лабораторных, практических, рефератов и коротких файлов. Он фокусируется на быстром нормоконтроле оформления.',
        items: ['поля страницы', 'Times New Roman, размер, стиль и интервалы', 'абзацный отступ и выравнивание', 'подписи таблиц и рисунков', 'эвристическая проверка листингов'],
      },
      {
        title: 'MEDIUM',
        text: 'Режим для курсовых, отчетов и более насыщенных учебных работ. Он включает LIGHT и добавляет проверки элементов, где часто ломается DOCX-верстка.',
        items: ['формат формул', 'выравнивание рисунков', 'нумерация и маркеры списков', 'подписи рисунков без точки в конце', 'центровка рисунка, пустой строки и подписи'],
      },
      {
        title: 'HARD',
        text: 'Полный режим для ВКР, дипломов, НИР и научных отчетов. Он запускает весь каталог реализованных чекеров.',
        items: ['структурные элементы документа', 'нумерация страниц и титульного листа', 'таблицы, формулы, рисунки и листинги', 'основной текст и списки', 'отключение нерелевантных правил по типу документа'],
      },
      {
        title: 'CUSTOM',
        text: 'Ручной режим всегда доступен: можно выбрать конкретные чекеры и прогнать только их, не выбирая тип работы вручную.',
        items: ['классификация типа остается автоматической', 'custom_checks передаются в /api/run', 'результат показывает процент корректности', 'дашборд группирует нарушения по кодам', 'исправление запускается отдельной кнопкой'],
      },
    ],
  },
  autofix: {
    title: 'Автофикс',
    kicker: 'Безопасное исправление форматирования',
    lead: 'Автоисправление запускается отдельным POST /api/run в режиме correct. Backend заново проверяет файл, применяет доступные fixer-модули и возвращает исправленный DOCX прямо в ответе вместе с preview для просмотра во фронте.',
    cards: [
      {
        title: 'Что исправляется',
        text: 'В текущей версии фиксы подключены через correct_all и отдельные scope для страниц, шрифтов, рисунков и списков.',
        items: ['поля страницы', 'нумерация страниц в нижнем колонтитуле', 'шрифт, размер, интервалы и абзацные отступы', 'подписи и центровка рисунков', 'маркеры и нумерация списков'],
      },
      {
        title: 'Как идет сценарий',
        text: 'Пользователь сначала валидирует документ, смотрит процент и список замечаний, затем запускает исправление фиксированной кнопкой.',
        items: ['валидация не меняет файл', 'исправление возвращает *_fixed.docx', 'preview строится из исправленного документа', 'скачивание идет из base64-ответа API'],
      },
      {
        title: 'Что не исправляется автоматически',
        text: 'Содержательные решения остаются за автором документа. Приложение не переписывает смысловой текст.',
        items: ['отсутствующие разделы с авторским текстом', 'сложная библиография', 'смысловые ссылки на источники', 'ручная переработка таблиц', 'спорные случаи, которые checker помечает как warning'],
      },
      {
        title: 'Будущая история',
        text: 'Историю проверок лучше добавить следующим этапом через отдельную SQLite/PostgreSQL-таблицу, не смешивая ее с текущей валидацией.',
        items: ['vk_user_id из launch-параметров', 'имя файла и профиль проверки', 'процент до и после исправления', 'путь к сохраненному DOCX', 'TTL-очистка старых файлов'],
      },
    ],
    flow: ['validate', 'dashboard', 'correct', 'fixers', 'preview', 'download'],
  },
};

function Flow({ items }) {
  if (!items?.length) return null;

  return (
    <div className="info-flow">
      {items.map((item, index) => (
        <div className="info-flow__node" key={item}>
          <span>{item}</span>
          {index < items.length - 1 && <b />}
        </div>
      ))}
    </div>
  );
}

export const InfoPanel = ({ id, type }) => {
  const routeNavigator = useRouteNavigator();
  const content = CONTENT[type];

  return (
    <Panel id={id}>
      <PanelHeader before={<PanelHeaderBack onClick={() => routeNavigator.push('/')} />}>
        {content.title}
      </PanelHeader>
      <Div>
        <section className={`info-page ${content.paper ? 'info-page--paper' : ''}`}>
          <div className="info-page__hero">
            <span>{content.kicker}</span>
            <h1>{content.title}</h1>
            <p>{content.lead}</p>
          </div>

          <Flow items={content.flow} />

          <div className="info-page__grid">
            {content.cards.map((card) => (
              <article className="info-card" key={card.title}>
                <h2>{card.title}</h2>
                <p>{card.text}</p>
                <ul>
                  {card.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>
      </Div>
    </Panel>
  );
};

Flow.propTypes = {
  items: PropTypes.arrayOf(PropTypes.string),
};

InfoPanel.propTypes = {
  id: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['ml', 'gost', 'autofix']).isRequired,
};
