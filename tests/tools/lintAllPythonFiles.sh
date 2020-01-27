#!/bin/bash
for file in `find . -name "*.py" ! -name "__init__.py"`;
  do
      echo "Check $file with pylint"
      python3 -m pylint --rcfile=tests/tools/.pylintrc $file
  done
