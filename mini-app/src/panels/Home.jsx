import { useState, useRef, useCallback, useEffect } from 'react';
import { Panel, PanelHeader, Div } from '@vkontakte/vkui';
import { useRouteNavigator } from '@vkontakte/vk-mini-apps-router';
import PropTypes from 'prop-types';

import {
  classifyDocument,
  fetchHealth,
  fetchModules,
  runDocumentValidation,
} from '../api/correctDocxApi';

const MAX_MB = 20;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const PROFILE_OPTIONS = [
  { value: 'LIGHT', title: 'LIGHT', desc: 'лабораторные и практические' },
  { value: 'MEDIUM', title: 'MEDIUM', desc: 'курсовые и отчеты' },
  { value: 'HARD', title: 'HARD', desc: 'дипломы, НИР, ВКР' },
  { value: 'CUSTOM', title: 'CUSTOM', desc: 'ручной набор правил' },
];

function fmtSize(bytes) {
  return bytes < 1048576 ? `${(bytes / 1024).toFixed(0)} КБ` : `${(bytes / 1048576).toFixed(1)} МБ`;
}

function Orbit() {
  return (
    <div style={{ width: 64, height: 64, position: 'relative', margin: '0 auto 18px' }}>
      <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '1px solid rgba(0,229,255,.20)' }} />
      <div style={{ position: 'absolute', inset: 8, borderRadius: '50%', border: '1px solid rgba(162,89,255,.15)' }} />
      <div style={{ position: 'absolute', top: '50%', left: '50%', width: 8, height: 8, marginTop: -4, marginLeft: -4, borderRadius: '50%', background: 'var(--cyan)', boxShadow: '0 0 10px var(--cyan)', animation: 'pulseGlow 2.5s ease-in-out infinite' }} />
      <div style={{ position: 'absolute', top: '50%', left: '50%', width: 5, height: 5, marginTop: -2.5, marginLeft: -2.5, borderRadius: '50%', background: 'var(--cyan)', boxShadow: '0 0 6px var(--cyan)', animation: 'orbit 3.5s linear infinite' }} />
      <div style={{ position: 'absolute', top: '50%', left: '50%', width: 4, height: 4, marginTop: -2, marginLeft: -2, borderRadius: '50%', background: 'var(--violet)', boxShadow: '0 0 6px var(--violet)', animation: 'orbitRev 5s linear infinite' }} />
    </div>
  );
}

function FeatureCard({ icon, title, desc, onClick }) {
  return (
    <button type="button" onClick={onClick} className="feature-card" aria-label={`Открыть раздел ${title}`}>
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 70% 35% at 50% 0%,rgba(0,229,255,.04) 0%,transparent 70%)', pointerEvents: 'none' }} />
      <span style={{ display: 'block', fontSize: 19, marginBottom: 6, color: 'var(--cyan)', filter: 'drop-shadow(0 0 5px rgba(0,229,255,.4))' }}>{icon}</span>
      <div style={{ fontSize: 10, fontWeight: 700, marginBottom: 3, color: 'var(--t1)' }}>{title}</div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 8, color: 'var(--t3)', lineHeight: 1.5 }}>{desc}</div>
    </button>
  );
}

function ProfileSelector({ value, onChange }) {
  return (
    <div className="mode-grid">
      {PROFILE_OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={`mode-pill ${value === option.value ? 'mode-pill--active' : ''}`}
        >
          <span>{option.title}</span>
          <small>{option.desc}</small>
        </button>
      ))}
    </div>
  );
}

function CheckerToggle({ checker, selected, onToggle }) {
  return (
    <button
      type="button"
      className={`option-toggle ${selected ? 'option-toggle--on' : ''}`}
      onClick={() => onToggle(checker.checker_id)}
    >
      <span className="option-toggle__box">{selected ? '✓' : ''}</span>
      <span>
        <b>{checker.title_ru}</b>
        <small>{checker.checker_id}</small>
      </span>
    </button>
  );
}

const resolveDetectedTitle = (classification) => {
  if (!classification) return 'файл';
  if (!classification.detected) return 'файл';
  return classification.title_ru || classification.class_id || 'файл';
};

export const Home = ({ id, fetchedUser, launchParams, onResult, theme, onToggleTheme }) => {
  const routeNavigator = useRouteNavigator();
  const [file, setFile] = useState(null);
  const [classification, setClassification] = useState(null);
  const [profile, setProfile] = useState('MEDIUM');
  const [customChecks, setCustomChecks] = useState([]);
  const [checkers, setCheckers] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [phase, setPhase] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth({ status: 'offline' }));
    fetchModules()
      .then((payload) => {
        const catalog = payload.checker_catalog || [];
        setCheckers(catalog);
        setCustomChecks(catalog.map((item) => item.checker_id));
      })
      .catch(() => setCheckers([]));
  }, []);

  useEffect(() => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.docx') || file.size > MAX_BYTES) return;

    let cancelled = false;
    setPhase('classifying');
    setProgress(30);
    classifyDocument(file, launchParams)
      .then((payload) => {
        if (cancelled) return;
        setClassification(payload);
        setProfile((payload.recommended_mode || 'MEDIUM').toUpperCase());
        setProgress(100);
        setPhase('idle');
      })
      .catch((submitError) => {
        if (cancelled) return;
        setClassification({ detected: false });
        setProfile('MEDIUM');
        setPhase('idle');
        setError(submitError.message || 'Не удалось определить тип документа');
      });

    return () => {
      cancelled = true;
    };
  }, [file, launchParams]);

  const validateFile = useCallback((candidate) => {
    if (!candidate) return false;
    if (!candidate.name.toLowerCase().endsWith('.docx')) {
      setError('Поддерживаются только документы .docx');
      return false;
    }
    if (candidate.size > MAX_BYTES) {
      setError(`Файл слишком большой. Лимит ${MAX_MB} МБ`);
      return false;
    }
    return true;
  }, []);

  const setFileReset = useCallback((nextFile) => {
    setError(null);
    setProgress(0);
    setClassification(null);
    if (nextFile && !validateFile(nextFile)) {
      setFile(null);
      return;
    }
    setFile(nextFile);
    setPhase('idle');
  }, [validateFile]);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    setDragging(false);
    const droppedFile = event.dataTransfer.files?.[0];
    if (droppedFile) setFileReset(droppedFile);
  }, [setFileReset]);

  const toggleCustomCheck = (checkerId) => {
    setCustomChecks((current) => (
      current.includes(checkerId)
        ? current.filter((item) => item !== checkerId)
        : [...current, checkerId]
    ));
  };

  const runValidation = async () => {
    if (!validateFile(file)) return;

    setError(null);
    setProgress(12);
    setPhase('validating');

    try {
      const result = await runDocumentValidation(file, {
        profile,
        customChecks,
      }, launchParams);
      setProgress(100);
      onResult(result, file, { profile, customChecks });
      routeNavigator.push('/result');
    } catch (submitError) {
      setPhase('error');
      setError(submitError.message || 'Ошибка соединения с API');
    }
  };

  const busy = phase === 'validating' || phase === 'classifying';
  const phaseLabel = phase === 'classifying' ? 'Определяю тип документа...' : 'Валидация документа...';
  const detectedTitle = resolveDetectedTitle(classification);
  const detectedMode = classification?.detected ? (classification.recommended_mode || profile) : profile;

  return (
    <Panel id={id}>
      <PanelHeader>
        <span style={{ fontFamily: 'var(--display)', fontWeight: 900, fontSize: 14, letterSpacing: '.05em', color: 'var(--t1)' }}>
          ГОСТ<span style={{ color: 'var(--cyan)', textShadow: '0 0 12px rgba(0,229,255,.55)' }}>ЧЕКЕР</span>
        </span>
      </PanelHeader>
      <button type="button" className="theme-toggle theme-toggle--floating" onClick={onToggleTheme} aria-label="Переключить тему">
        {theme === 'dark' ? 'Light' : 'Dark'}
      </button>

      <Div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, paddingBottom: 16, animation: 'fadeIn .5s ease' }}>
          {fetchedUser?.photo_100 && <img src={fetchedUser.photo_100} alt="" style={{ width: 28, height: 28, borderRadius: '50%', border: '1.5px solid var(--b1)', flexShrink: 0 }} />}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--t3)' }}>режим доступа</div>
            <div style={{ fontSize: 13, fontWeight: 700 }}>
              {fetchedUser ? `${fetchedUser.first_name} ${fetchedUser.last_name}` : 'VK Mini Apps'}
            </div>
          </div>
          <div className={`status-pill ${health?.status === 'ok' ? 'status-pill--ok' : ''}`}>
            <div />
            {health?.status === 'ok' ? 'API online' : 'API offline'}
          </div>
        </div>

        <div style={{ textAlign: 'center', paddingBottom: 22, animation: 'fadeUp .5s ease' }}>
          <Orbit />
          <h1 style={{ fontFamily: 'var(--display)', fontWeight: 900, fontSize: 'clamp(20px,5.5vw,28px)', lineHeight: 1.15, marginBottom: 10 }}>
            Проверка документов<br />
            <span className="gc-grad">по ГОСТ</span>
          </h1>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--t3)', lineHeight: 1.9 }}>
            DOCX · автотип · валидация · исправление
          </p>
        </div>

        <div
          onDrop={onDrop}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onClick={() => !file && inputRef.current?.click()}
          className={`drop-zone ${dragging ? 'drop-zone--drag' : ''} ${file ? 'drop-zone--ready' : ''}`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".docx"
            onChange={(event) => {
              const selectedFile = event.target.files?.[0];
              if (selectedFile) setFileReset(selectedFile);
              event.target.value = '';
            }}
            style={{ display: 'none' }}
          />

          {!file ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, position: 'relative' }}>
              <div className="upload-glyph">↑</div>
              <div style={{ fontSize: 15, fontWeight: 700 }}>Перетащите .docx сюда</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--t3)' }}>или нажмите для выбора · до {MAX_MB} МБ</div>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, position: 'relative' }}>
              <div className="file-glyph">DOCX</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{file.name}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--t3)', marginTop: 2 }}>{fmtSize(file.size)}</div>
              </div>
              <button
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  setFileReset(null);
                }}
                className="round-danger"
                aria-label="Убрать файл"
              >
                ×
              </button>
            </div>
          )}
        </div>

        {file && (
          <div className="result-card classification-card">
            <div className="gc-label">тип документа</div>
            <div className="classification-title">{detectedTitle}</div>
            <div className="meta-grid">
              <div><span>статус</span><b>{classification?.detected ? 'определен' : 'тип файла не определён'}</b></div>
              <div><span>профиль</span><b>{detectedMode || 'MEDIUM'}</b></div>
              <div><span>правила</span><b>{profile === 'CUSTOM' ? customChecks.length : profile}</b></div>
            </div>
            {classification?.warning && <p className="mini-note">{classification.warning}</p>}
          </div>
        )}

        <div style={{ animation: 'fadeUp .5s .12s ease both', marginBottom: 14 }}>
          <div className="gc-label" style={{ marginBottom: 10 }}>режим проверки</div>
          <ProfileSelector value={profile} onChange={setProfile} />
        </div>

        {profile === 'CUSTOM' && (
          <div className="custom-checks">
            <div className="gc-label">custom правила</div>
            {checkers.map((checker) => (
              <CheckerToggle
                key={checker.checker_id}
                checker={checker}
                selected={customChecks.includes(checker.checker_id)}
                onToggle={toggleCustomCheck}
              />
            ))}
          </div>
        )}

        {error && (
          <div className="error-box">
            <span>!</span>
            {error}
          </div>
        )}

        {busy && (
          <div className="progress-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
              <span style={{ fontSize: 13, fontWeight: 700 }}>{phaseLabel}</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--cyan)' }}>{progress}%</span>
            </div>
            <div className="gc-track">
              <div className="gc-fill" style={{ width: `${progress}%` }} />
            </div>
            <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--t3)', textAlign: 'center', marginTop: 9 }}>
              FastAPI читает DOCX, выбирает профиль и запускает чекеры без ручного выбора типа.
            </p>
          </div>
        )}

        {!busy && (
          <div style={{ display: 'grid', gap: 8, marginTop: 14 }}>
            <button
              className={`analyze-button ${!file ? 'analyze-button--select' : ''}`}
              type="button"
              onClick={() => (file ? runValidation() : inputRef.current?.click())}
              disabled={profile === 'CUSTOM' && customChecks.length === 0}
            >
              {file ? 'ВАЛИДАЦИЯ ДОКУМЕНТА' : 'Выберите файл'}
            </button>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginTop: 18, animation: 'fadeUp .5s .3s ease both' }}>
          <FeatureCard icon="◎" title="Классификатор" desc="16 признаков + RF" onClick={() => routeNavigator.push('/ml-model')} />
          <FeatureCard icon="□" title="ГОСТ" desc="поля, шрифты, списки" onClick={() => routeNavigator.push('/gost-732')} />
          <FeatureCard icon="↯" title="Автофикс" desc="docx без переписывания" onClick={() => routeNavigator.push('/autofix')} />
        </div>
      </Div>
    </Panel>
  );
};

FeatureCard.propTypes = {
  icon: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  desc: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
};

ProfileSelector.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};

CheckerToggle.propTypes = {
  checker: PropTypes.shape({
    checker_id: PropTypes.string.isRequired,
    title_ru: PropTypes.string.isRequired,
  }).isRequired,
  selected: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
};

Home.propTypes = {
  id: PropTypes.string.isRequired,
  fetchedUser: PropTypes.shape({
    photo_100: PropTypes.string,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
  }),
  launchParams: PropTypes.string,
  onResult: PropTypes.func.isRequired,
  theme: PropTypes.oneOf(['light', 'dark']).isRequired,
  onToggleTheme: PropTypes.func.isRequired,
};
