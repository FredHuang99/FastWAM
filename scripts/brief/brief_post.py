import sys, zipfile, re, shutil
src = sys.argv[1]; tmp = src + '.tmp'
zin = zipfile.ZipFile(src); zout = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename.startswith('ppt/charts/chart') and item.filename.endswith('.xml'):
        x = data.decode('utf-8')
        n = x.count('<c:v></c:v>')
        x = re.sub(r'<c:pt idx="\d+"><c:v></c:v></c:pt>', '', x)
        if n: print('removed', n, 'empty points in', item.filename)
        data = x.encode('utf-8')
    zout.writestr(item, data)
zout.close(); zin.close(); shutil.move(tmp, src)
