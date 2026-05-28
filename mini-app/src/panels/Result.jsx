import { useMemo, useState } from 'react';
import { Panel, PanelHeader, PanelHeaderBack, Div } from '@vkontakte/vkui';
import { useRouteNavigator } from '@vkontakte/vk-mini-apps-router';
import PropTypes from 'prop-types';

import { runDocumentCorrection, saveFixedFile } from '../api/correctDocxApi';

function Ring({ pct }) {
  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  const filled = (pct / 100) * circumference;
  const color = pct >= 90 ? '#00ff94' : pct >= 70 ? '#ffb703' : '#ff4757';

  return (
    <div className="score-ring">
      <svg width={116} height={116} viewBox="0 0 116 116">
        <circle cx={58} cy={58} r={radius} fill="none" stroke="rgba(255,255,255,.06)" strokeWidth={7} />
        <circle
          cx={58}
          cy={58}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={7}
          strokeDasharray={`${filled} ${circumference}`}
          strokeLinecap="round"
          transform="rotate(-90 58 58)"
          style={{ filter: `drop-shadow(0 0 9px ${color})`, transition: 'stroke-dasharray 1.1s ease' }}
        />
      </svg>
      <div className="score-ring__center">
        <span className="score-ring__pct" style={{ color }}>{pct.toFixed(0)}%</span>
        <span className="score-ring__label">ГОСТ</span>
      </div>
    </div>
  );
}

function issueColor(severity) {
  if (severity === 'error') return 'var(--red)';
  if (severity === 'warning') return 'var(--amber)';
  return 'var(--cyan)';
}

const normalizeIssue = (issue, index) => ({
  id: `${issue.code || 'issue'}-${issue.element_id || index}-${index}`,
  code: issue.code || 'CHECK',
  message: issue.message || 'Нарушение форматирования',
  expected: issue.expected,
  actual: issue.actual,
  text: issue.actual_text,
  element: issue.element_id,
  severity: issue.severity || 'warning',
});

const useValidationView = (result) => {
  const violations = result?.help?.items?.length
    ? result.help.items
    : (result?.report?.violations || []);

  const issues = violations.map(normalizeIssue);
  const score = Number(result?.metrics?.correctness_before_percent ?? 0);
  const errors = issues.filter((issue) => issue.severity === 'error').length;
  const warnings = issues.filter((issue) => issue.severity === 'warning').length;
  const topCodes = result?.help?.top_codes || [];

  return {
    score,
    issues,
    errors,
    warnings,
    topCodes,
  };
};

function PreviewPager({ preview }) {
  const [pageIndex, setPageIndex] = useState(0);
  const pages = preview?.pages || [];
  const page = pages[pageIndex];

  if (!pages.length) {
    return (
      <div className="doc-preview doc-preview--empty">
        Preview DOCX недоступен, но исправленный файл уже собран и готов к скачиванию.
      </div>
    );
  }

  return (
    <div className="doc-preview">
      <div className="doc-preview__toolbar">
        <button type="button" onClick={() => setPageIndex((current) => Math.max(0, current - 1))} disabled={pageIndex === 0}>‹</button>
        <span>Страница {pageIndex + 1} из {pages.length}</span>
        <button type="button" onClick={() => setPageIndex((current) => Math.min(pages.length - 1, current + 1))} disabled={pageIndex === pages.length - 1}>›</button>
      </div>
      <article className="doc-page">
        {(page?.paragraphs || []).map((paragraph, index) => (
          <p key={`${page.page}-${index}`}>{paragraph}</p>
        ))}
      </article>
      {preview.truncated && <div className="mini-note">Показаны первые страницы. Полный документ доступен в DOCX.</div>}
    </div>
  );
}

export const Result = ({
  id,
  result,
  file,
  filename,
  launchParams,
  runOptions,
  correctionResult,
  onCorrectionResult,
}) => {
  const routeNavigator = useRouteNavigator();
  const [actionError, setActionError] = useState(null);
  const [fixing, setFixing] = useState(false);
  const view = useValidationView(result);

  const corrected = correctionResult?.fixed_file;
  const afterScore = Number(correctionResult?.metrics?.correctness_after_percent ?? view.score);
  const visibleScore = corrected ? afterScore : view.score;
  const statusColor = visibleScore >= 90 ? 'var(--green)' : visibleScore >= 70 ? 'var(--amber)' : 'var(--red)';
  const statusLabel = visibleScore >= 90 ? 'Отлично' : visibleScore >= 70 ? 'Есть замечания' : 'Требует доработки';
  const docType = result?.document_type?.detected
    ? result.document_type.title_ru
    : 'тип файла не определён';

  const bySeverity = useMemo(() => [
    { label: 'ошибки', value: view.errors, color: 'var(--red)' },
    { label: 'warning', value: view.warnings, color: 'var(--amber)' },
    { label: 'всего', value: view.issues.length, color: 'var(--cyan)' },
  ], [view.errors, view.issues.length, view.warnings]);

  if (!result) {
    return (
      <Panel id={id}>
        <PanelHeader before={<PanelHeaderBack onClick={() => routeNavigator.push('/')} />}>Результат</PanelHeader>
        <Div>
          <div className="empty-state">Сначала загрузите DOCX на главной странице.</div>
        </Div>
      </Panel>
    );
  }

  const applyAutoFix = async () => {
    if (!file) return;
    setFixing(true);
    setActionError(null);
    try {
      const nextResult = await runDocumentCorrection(file, runOptions, launchParams);
      onCorrectionResult?.(nextResult);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      setActionError(error.message || 'Не удалось исправить документ');
    } finally {
      setFixing(false);
    }
  };

  return (
    <Panel id={id}>
      <PanelHeader before={<PanelHeaderBack onClick={() => routeNavigator.push('/')} />}>
        <span style={{ fontFamily: 'var(--display)', fontWeight: 900, fontSize: 13, letterSpacing: '.04em' }}>
          {corrected ? 'Исправленный документ' : 'Результат валидации'}
        </span>
      </PanelHeader>

      <Div className={corrected ? 'result-with-download' : 'result-with-fixed-action'}>
        {corrected ? (
          <>
            <div className="result-card">
              <div className="result-card__glow" />
              <div className="section-title"><span>□</span> Preview исправленного DOCX</div>
              <PreviewPager preview={corrected.preview} />
            </div>

            <div className="result-card result-card--score">
              <div className="result-card__glow" />
              <div className="score-hero">
                <Ring pct={afterScore} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--t3)', marginBottom: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{corrected.filename}</div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 17, fontWeight: 900, color: statusColor, marginBottom: 11, textShadow: `0 0 18px ${statusColor}55` }}>Файл исправлен</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--t2)', lineHeight: 1.55 }}>
                    Было {Math.round(view.score)}%, стало {Math.round(afterScore)}%. Размер: {Math.round(corrected.size_bytes / 1024)} КБ.
                  </div>
                </div>
              </div>
            </div>

            <button className="download-bottom-button" type="button" onClick={() => saveFixedFile(corrected)}>
              Скачать файл снизу
            </button>
          </>
        ) : (
          <>
            <div className="result-card result-card--score">
              <div className="result-card__glow" />
              <div className="score-hero">
                <Ring pct={view.score} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--t3)', marginBottom: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{filename}</div>
                  <div style={{ fontFamily: 'var(--display)', fontSize: 17, fontWeight: 900, color: statusColor, marginBottom: 11, textShadow: `0 0 18px ${statusColor}55` }}>{statusLabel}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--t2)', lineHeight: 1.55 }}>
                    {docType} · {result.profile || runOptions?.profile || 'MEDIUM'} · {result.checker_ids?.length || 0} правил
                  </div>
                </div>
              </div>
              <div className="score-summary-line">
                {bySeverity.map((item) => (
                  <div key={item.label}><span>{item.label}</span><b style={{ color: item.color }}>{item.value}</b></div>
                ))}
              </div>
            </div>

            {view.topCodes.length > 0 && (
              <div className="result-card top-codes">
                <div className="section-title"><span>!</span> Частые нарушения</div>
                {view.topCodes.map((item) => (
                  <div className="history-row" key={item.code}>
                    <span>{item.code}</span>
                    <b>{item.count}</b>
                  </div>
                ))}
              </div>
            )}

            {actionError && (
              <div className="error-box">
                <span>!</span>
                {actionError}
              </div>
            )}

            {view.issues.length > 0 ? (
              <div className="result-card">
                <div className="result-card__glow" />
                <div style={{ position: 'relative' }}>
                  <div className="section-title"><span>!</span> Все замечания ({view.issues.length})</div>
                  {view.issues.map((issue) => (
                    <div className="issue-row" key={issue.id}>
                      <div className="issue-row__head">
                        <span style={{ color: issueColor(issue.severity) }}>{issue.code}</span>
                        <b>{issue.severity}</b>
                      </div>
                      <p>{issue.message}</p>
                      {issue.text && <p className="issue-row__quote">{issue.text}</p>}
                      <div className="issue-row__meta">
                        {issue.element && <span>{issue.element}</span>}
                        {issue.actual && <span>сейчас: {issue.actual}</span>}
                        {issue.expected && <span>нужно: {issue.expected}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="success-box">
                <span>✓</span>
                Нарушений не найдено по включенным правилам.
              </div>
            )}

            <div className="fixed-action">
              <button className="analyze-button" type="button" onClick={applyAutoFix} disabled={fixing || !file}>
                {fixing ? 'ИСПРАВЛЯЮ ДОКУМЕНТ...' : 'ЗАПУСТИТЬ ИСПРАВЛЕНИЕ'}
              </button>
            </div>
          </>
        )}
      </Div>
    </Panel>
  );
};

Ring.propTypes = {
  pct: PropTypes.number.isRequired,
};

PreviewPager.propTypes = {
  preview: PropTypes.shape({
    pages: PropTypes.arrayOf(PropTypes.shape({
      page: PropTypes.number,
      paragraphs: PropTypes.arrayOf(PropTypes.string),
    })),
    truncated: PropTypes.bool,
  }),
};

Result.propTypes = {
  id: PropTypes.string.isRequired,
  result: PropTypes.object,
  file: PropTypes.object,
  filename: PropTypes.string,
  launchParams: PropTypes.string,
  runOptions: PropTypes.shape({
    profile: PropTypes.string,
    customChecks: PropTypes.arrayOf(PropTypes.string),
  }),
  correctionResult: PropTypes.object,
  onCorrectionResult: PropTypes.func,
};
