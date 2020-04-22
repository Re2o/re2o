/**
 * Re2o VueJS configuration
 * 
 * Each VueJS components in static/components are compiled into asynchronous
 * chunks in static/bundles.
 * Then you can use for exemple <re2o-hello-world></re2o-hello-world> to call
 * the HelloWorld component.
 */

const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    // Output to Django statics
    outputDir: './static/bundles/',

    // Customize Webpack    
    chainWebpack: config => {
        // Create file for django-webpack-loader
        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{ filename: './webpack-stats.json' }])
    }
};