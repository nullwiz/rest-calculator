const fs = require('fs')
const path = require('path')

const pluginPath = path.join(
  'node_modules',
  'serverless-python-requirements',
  'lib',
  'packRequirements.js'
)

const content = fs.readFileSync(pluginPath, 'utf-8')

const patchedContent = content.replace(
  'fse.copySync(".serverless/requirements", zipPath);',
  'fse.copySync(".serverless/requirements", zipPath);\n      fse.copySync(".serverless/worker_requirements", zipPath);\n'
)

fs.writeFileSync(pluginPath, patchedContent)
