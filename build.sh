#!/bin/bash
set -e

HOST="tbears.icon.foundation"
S3_HOST="${HOST}.s3-website.ap-northeast-2.amazonaws.com"
PRODUCT="iconrpcserver"
DEPS="earlgrey iconcommons"
BRANCH=$(git rev-parse --abbrev-ref HEAD)

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

if [[ ("$1" = "test" && "$2" != "--ignore-test") || ("$1" = "build") || ("$1" = "deploy") ]]; then
  pip install -r requirements.txt

  for PKG in $DEPS
  do
    URL="http://${S3_HOST}/${PKG}/VERSION"
    PKG_VER=$(curl $URL)

    URL="http://${S3_HOST}/${BRANCH}/${PKG}/${PKG}-${PKG_VER}-py3-none-any.whl"
    pip install --force-reinstall "$URL"
  done

  if [[ "$2" != "--ignore-test" ]]; then
    python -m unittest
  fi

  if [ "$1" = "build" ] || [ "$1" = "deploy" ]; then
    pip install wheel
    rm -rf build dist *.egg-info
    python setup.py bdist_wheel

    if [ "$1" = "deploy" ]; then
      VER=$(cat VERSION)

      if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        echo "Error: AWS keys should be in your environment"
        exit 1
      fi

      S3_URL="s3://${HOST}/${BRANCH}/${PRODUCT}/"
      echo "$S3_URL"

      pip install awscli
      aws s3 cp VERSION "$S3_URL" --acl public-read
      aws s3 cp dist/*$VER*.whl "$S3_URL" --acl public-read
    fi
  fi

else
  echo "Usage: build.sh [test|build|deploy]"
  echo "  test: run test"
  echo "  build: run test and build"
  echo "  build --ignore-test: run build"
  echo "  deploy: run test, build and deploy to s3"
  echo "  deploy --ignore-test: run build and deploy to s3"
  exit 1
fi
