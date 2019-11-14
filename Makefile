check:
	pycodestyle .
	flake8 .

test:
	pytest -v --cov


cov: test
	codecov


clean:
	rm -rf .eggs dist gparser.egg-info .coverage .pytest_cache


upload: test
	python setup.py sdist && twine upload dist/*