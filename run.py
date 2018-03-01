#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from promsd.promsd import create_app


if __name__ == '__main__':
    # create_app(os.getenv('FLASK_CONFIG') or 'default')
    # CONFIG = os.getenv('FLASK_CONFIG') or DevConfig
    app = create_app()
    app.run(debug=True, port=4999)


