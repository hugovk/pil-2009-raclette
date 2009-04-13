erase *.pyd
erase pil\*.pyd
python make-manifest.py
python setup.py build_ext -i
python setup.py bdist_wininst
