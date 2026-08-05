const os = require('os');
const path = require('path');

const privateDataDir = process.env.CONTEXT_INFRA_PRIVATE_DATA_DIR
  ? path.resolve(process.env.CONTEXT_INFRA_PRIVATE_DATA_DIR)
  : path.join(
      os.homedir(),
      'Library',
      'Application Support',
      'context-infrastructure',
      'chrome-bookmark-cleanup',
    );

module.exports = {
  backupsDir: path.join(privateDataDir, 'backups'),
  historySnapshotDir: path.join(privateDataDir, 'history_snapshot'),
  outputDir: path.join(privateDataDir, 'output'),
  privateDataDir,
};
