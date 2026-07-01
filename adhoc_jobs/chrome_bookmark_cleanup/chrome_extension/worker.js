async function openRunner() {
  const url = chrome.runtime.getURL('runner.html');
  const tabs = await chrome.tabs.query({ url });
  if (tabs.length > 0) {
    await chrome.tabs.update(tabs[0].id, { active: true });
    return;
  }
  await chrome.tabs.create({ url });
}

chrome.runtime.onInstalled.addListener(() => {
  openRunner().catch((error) => console.error(error));
});

chrome.runtime.onStartup.addListener(() => {
  openRunner().catch((error) => console.error(error));
});

chrome.runtime.onMessage.addListener((message) => {
  if (message && message.type === 'open-runner') {
    openRunner().catch((error) => console.error(error));
  }
});
