import os
import click
import unittest
from promsd.promsd import create_app

app = create_app()

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='promsd/*')
    COV.start()


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Enable code coverage')
def test(coverage):
    """Run the unit tests."""

    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    tests = unittest.TestLoader().discover('tests/', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()