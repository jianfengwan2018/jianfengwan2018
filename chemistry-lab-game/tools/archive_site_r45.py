#!/usr/bin/env python3
"""One-shot user-authorized R45 archive. No site credentials; only public bytes."""
import base64,concurrent.futures,datetime,gzip,hashlib,json,pathlib,shutil,subprocess,time,urllib.parse,urllib.request
P=pathlib.Path('chemistry-lab-game')
D=json.loads(gzip.decompress(base64.b64decode((P/'tools/archive_site_r45_payload.b64').read_text())))
ROOT=P/'web-demo/current'
ORIGIN='https://dahua-continuous-playtest.boldcornbread.chatgpt.site/'
def git(*a): return subprocess.check_output(['git',*a],text=True).strip()
def run(*a,**kw): subprocess.run(a,check=True,**kw)
def dig(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def safe(s):
 p=pathlib.PurePosixPath(s)
 if p.is_absolute() or '..' in p.parts: raise ValueError(s)
 return s
if ROOT.exists(): raise RuntimeError('current already exists; refusing to overwrite')
head=git('rev-parse','HEAD')
run('git','config','user.name','github-actions[bot]')
run('git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
def fetch(f):
 path=safe(f['path']); url=ORIGIN+urllib.parse.quote(path,safe='/')+'?archive=r45'
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=90) as r:b=r.read()
   if len(b)!=f['size'] or dig(b)!=f['sha256'] or blob(b)!=f['git_blob']: raise ValueError('Snapshot bytes mismatch: '+path)
   target=ROOT/'out'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
   return path
  except Exception:
   if attempt==2: raise
   time.sleep(2*(attempt+1))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for i,p in enumerate(pool.map(fetch,D['files']),1):
  if i%50==0:print('Verified runtime files',i,flush=True)
shutil.copytree(ROOT/'out',ROOT/'dist')
for name,text in D['extras'].items():
 p=ROOT/safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
(ROOT/'README.md').write_text("""# 大化春秋 · Site R45
完整可运行的 HTML5/Canvas 源码和资源，固定目录维护。不是 Godot Web 导出。
运行：在此目录执行 python3 -m http.server 8000 --directory out，再打开 http://localhost:8000/。
根入口包括六楼教室静态开场及70秒赠书视频；?preview=lab6仅测试楼层，跳过开场。
测试：node --test --test-concurrency=1 tests/*.test.mjs
out 是正式线上目录；dist 是字节一致的本地测试镜像，无构建依赖。
包含772个线上文件、全部39个测试文件及测试所需历史JSON夹具。
保留原始地图、人物、633图、网页版70秒赠书视频；未加入15秒已取消动画。
不包含私有站点凭据、托管配置、.git目录或与运行/测试无关的旧QA截图、过时dist资源。
SOURCE_README.md保存源项目说明。version.json逐文件记录字节数、SHA-256和Git blob SHA。
Git提交/带时间标签恢复历史；原仓库Godot及v6/v12历史目录未修改。
""",encoding='utf-8')
run('node','--test','--test-concurrency=1',*[str(p.relative_to(ROOT)) for p in sorted((ROOT/'tests').glob('*.test.mjs'))],cwd=ROOT)
files=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file():
  b=p.read_bytes();files.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=dig(b),git_blob_sha1=blob(b)))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
tag='html5-r45-'+stamp.replace('-','').replace(':','')
manifest=dict(name='大化春秋',version='R45',source_commit=D['source_commit'],archived_at=stamp,technology='HTML5 / Canvas',runtime_files_unchanged=True,tests_passed=362,files=files)
(ROOT/'version.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Remove the one-time trigger from the current tree after success.
pathlib.Path('.github/workflows/archive-site-r45.yml').unlink()
run('git','add',str(ROOT),'.github/workflows/archive-site-r45.yml')
run('git','commit','-m','chore(archive): preserve complete verified Site R45 runtime and tests')
archive=git('rev-parse','HEAD')
catalog=P/'releases/index.json';index=json.loads(catalog.read_text())
index['snapshots'].append(dict(id=tag,kind='html5',version='R45',status='archived',archived_at=stamp,archive_commit=archive,source_commit=D['source_commit'],root='web-demo/current',manifest='version.json',tag=tag,note='完整Site R45运行源码/资源与测试；70秒赠书视频网页版本；原Godot及历史归档保留。'))
catalog.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
change=P/'CHANGELOG.md';change.write_text('# '+stamp+' · Site R45 GitHub归档\n\n固定路径 web-demo/current；362项测试通过；完整运行源码与资源，含70秒赠书视频。source_commit: '+D['source_commit']+'；archive_commit: '+archive+'。旧版本未覆盖。\n\n'+change.read_text(),encoding='utf-8')
run('python3','chemistry-lab-game/tools/check_versions.py')
run('python3','-m','unittest','discover','-s','chemistry-lab-game/tools','-p','test_*.py')
run('git','add',str(catalog),str(change))
run('git','commit','-m','docs(releases): record verified R45 archive commit and tag')
run('git','tag','-a',tag,archive,'-m','Site R45 archived '+stamp)
run('git','fetch','origin','main')
if git('rev-parse','origin/main')!=head: raise RuntimeError('main changed concurrently; refusing overwrite; rerun only after review')
run('git','push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+tag)
print(json.dumps(dict(archive_commit=archive,record_commit=git('rev-parse','HEAD'),tag=tag,files=len(files),runtime_files=len(D['files'])),ensure_ascii=False))
