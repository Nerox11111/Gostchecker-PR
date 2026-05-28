import { useState, useEffect } from 'react';
import { View, SplitLayout, SplitCol, ScreenSpinner } from '@vkontakte/vkui';
import { useActiveVkuiLocation } from '@vkontakte/vk-mini-apps-router';
import PropTypes from 'prop-types';

import { Home, InfoPanel, Result } from './panels';
import { DEFAULT_VIEW_PANELS } from './routes';
import { fetchCurrentVkUser, getLaunchParams } from './api/correctDocxApi';

const resolveInitialTheme = (vkAppearance) => {
  const stored = localStorage.getItem('gc-theme');
  if (stored === 'light' || stored === 'dark') return stored;
  if (vkAppearance === 'light' || vkAppearance === 'dark') return vkAppearance;
  return window.matchMedia?.('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
};

export const App = ({ initialAppearance }) => {
  const { panel: activePanel = DEFAULT_VIEW_PANELS.HOME } = useActiveVkuiLocation();
  const [fetchedUser, setUser] = useState();
  const [popout, setPopout] = useState(<ScreenSpinner />);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisFile, setAnalysisFile] = useState(null);
  const [runOptions, setRunOptions] = useState({ profile: 'MEDIUM', customChecks: [] });
  const [correctionResult, setCorrectionResult] = useState(null);
  const [launchParams, setLaunchParams] = useState('');
  const [theme, setTheme] = useState(() => resolveInitialTheme(initialAppearance));

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('gc-theme', theme);
  }, [theme]);

  useEffect(() => {
    async function fetchData() {
      try {
        const params = await getLaunchParams();
        setLaunchParams(params);
        setUser(await fetchCurrentVkUser(params));
      } catch {
        setLaunchParams(await getLaunchParams());
      }
      setPopout(null);
    }
    fetchData();
  }, []);

  return (
    <SplitLayout>
      <SplitCol>
        <View activePanel={activePanel}>
          <Home
            id="home"
            fetchedUser={fetchedUser}
            launchParams={launchParams}
            theme={theme}
            onToggleTheme={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
            onResult={(result, file, options) => {
              setAnalysisResult(result);
              setAnalysisFile(file);
              setRunOptions(options);
              setCorrectionResult(null);
            }}
          />
          <Result
            id="result"
            result={analysisResult}
            file={analysisFile}
            filename={analysisFile?.name ?? 'document.docx'}
            launchParams={launchParams}
            runOptions={runOptions}
            correctionResult={correctionResult}
            onCorrectionResult={setCorrectionResult}
          />
          <InfoPanel id="ml" type="ml" />
          <InfoPanel id="gost" type="gost" />
          <InfoPanel id="autofix" type="autofix" />
        </View>
      </SplitCol>
      {popout}
    </SplitLayout>
  );
};

App.propTypes = {
  initialAppearance: PropTypes.oneOf(['light', 'dark']),
};
