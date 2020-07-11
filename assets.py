# myapp/util/assets.py

from flask import Flask
from flask_assets import Environment, Bundle

bundles = {

    'base_js': Bundle(
        'web/assets/jquery/jquery.min.js',
        'tether/tether.min.js',
        'bootstrap/js/bootstrap.min.js',
        'viewport-checker/jquery.viewportchecker.js',
        'smooth-scroll/smooth-scroll.js',
        'dropdown/js/script.min.js',
        'touch-swipe/jquery.touch-swipe.min.js',
        'theme/js/script.js',
        'facebook-plugin/facebook-script.js',
        'jarallax/jarallax.js',
        'formoid/formoid.min.js',
        output='gen/base.js'),

    'base_css': Bundle(
        'tether/tether.min.css',
        'bootstrap/css/bootstrap.min.css',
        'dropdown/css/style.css',
        'animatecss/animate.min.css',
        'theme/css/style.css',
        'facebook-plugin/style.css',
        'mobirise/css/mbr-additional.css',
        'web/assets/mobirise-icons/mobirise-icons.css',
        output='gen/base.css'),

    # 'others_js': Bundle(
    #     'js/lib/jquery-1.10.2.js',
    #     'js/lib/Chart.js',
    #     'js/admin.js',
    #     output='gen/others.js'),

    # 'others_css': Bundle(
    #     'css/lib/reset.css',
    #     'css/common.css',
    #     'css/admin.css',
    #     output='gen/others.css')
}

app = Flask(__name__)
assets = Environment(app)

assets.register(bundles)
