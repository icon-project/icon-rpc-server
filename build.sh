#!/bin/bash
set -e

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

pip install -r requirements.txt
WGET_VER=$(curl http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/earlgrey/VERSION)
pip install --force-reinstall "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/earlgrey/earlgrey-${WGET_VER}-py3-none-any.whl"
rm -rf earlgrey*

WGET_VER=$(curl http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/iconcommons/VERSION)
pip install --force-reinstall "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/iconcommons/iconcommons-${WGET_VER}-py3-none-any.whl"
rm -rf iconcommons*


pip install wheel
rm -rf build dist *.egg-info
python setup.py bdist_wheel
