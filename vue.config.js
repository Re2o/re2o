/**
 * Re2o VueJS configuration
 * 
 * Each VueJS components in static/components are compiled into asynchronous
 * chunks in static/bundles.
 * Then you can use for exemple <re2o-hello-world></re2o-hello-world> to call
 * the HelloWorld component.
 * 
 * You can develop components using `yarnpkg watch` (auto rebuild in dev mode)
 * and `watch python3 manage.py collectstatic --noinput` (auto collect statics).
 */

module.exports = {
    // Output to Django statics
    outputDir: './static/bundles/',
};