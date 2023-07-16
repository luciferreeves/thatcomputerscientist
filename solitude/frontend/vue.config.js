const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  outputDir: '../../templates/@solitude_frontend',
  assetsDir: '../../static/@solitude/prod',
  transpileDependencies: true
})
