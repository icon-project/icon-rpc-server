#!/bin/bash
set -e

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

pip install -r requirements.txt
wget "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/earlgrey-0.0.2-py3-none-any.whl"
pip install --force-reinstall earlgrey-0.0.2-py3-none-any.whl
rm -rf earlgrey*
wget "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/iconcommons-0.9.5-py3-none-any.whl"
pip install --force-reinstall iconcommons-0.9.5-py3-none-any.whl
rm -rf iconcommons*


pip install wheel
rm -rf build dist *.egg-info
python setup.py bdist_wheel
