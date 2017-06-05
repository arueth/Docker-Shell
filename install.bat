@echo off
pushd %CD%
cd drivers
call install.bat
popd
pushd %CD%
cd package
twine upload dist/*
popd