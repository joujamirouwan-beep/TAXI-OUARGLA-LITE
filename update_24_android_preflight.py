#!/usr/bin/env python3
"""Static release gate for Taxi Ouargla Lite Android AAB prerequisites."""
from pathlib import Path
import re, sys, shutil, subprocess
ROOT = Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok, detail=''):
    checks.append((name, bool(ok), detail))

def read(path):
    p=ROOT/path
    return p.read_text(encoding='utf-8') if p.exists() else ''

app=read(Path('android/app/build.gradle'))
settings=read(Path('android/settings.gradle'))
pub=read(Path('pubspec.yaml'))
manifest=read(Path('android/app/src/main/AndroidManifest.xml'))
wrapper=read(Path('android/gradle/wrapper/gradle-wrapper.properties'))
key_example=read(Path('android/key.properties.example'))
check('Android namespace preserved', "namespace 'com.taxiouargla.lite'" in app)
check('Android applicationId preserved', "applicationId 'com.taxiouargla.lite'" in app)
check('Gradle Android plugin pinned', 'com.android.application" version "8.3.2"' in settings)
check('Kotlin plugin pinned', 'org.jetbrains.kotlin.android" version "1.9.22"' in settings)
check('Gradle distribution compatible', 'gradle-8.4-all.zip' in wrapper)
check('AAB version metadata is Flutter-build overridable', 'versionCode flutter.versionCode' in app and 'versionName flutter.versionName' in app and 'version: 3.10.1+31001' in pub)
check('Arabic launcher label present', 'طاكسي ورڨلة لايت' in manifest)
check('Signing template has required keys', all(re.search(rf'(?m)^{k}=.+$', key_example) for k in ('storeFile','storePassword','keyAlias','keyPassword')))
check('Build script exists', (ROOT/'tools/build_release_aab.sh').is_file())
check('Windows build script exists', (ROOT/'tools/BUILD_AAB_WINDOWS.ps1').is_file())
check('Flutter wrapper script present', (ROOT/'android/gradlew').is_file())
check('Gradle wrapper JAR present', (ROOT/'android/gradle/wrapper/gradle-wrapper.jar').is_file())
check('Windows Gradle wrapper present', (ROOT/'android/gradlew.bat').is_file())
check('Local signing config present', (ROOT/'android/key.properties').is_file())
check('Flutter SDK available in PATH', __import__('shutil').which('flutter') is not None)
java_path=shutil.which('java')
java_version=''
if java_path:
    proc=subprocess.run([java_path, '-version'], capture_output=True, text=True)
    java_version=(proc.stderr or proc.stdout).splitlines()[0] if (proc.stderr or proc.stdout) else ''
check('JDK 17 available in PATH', bool(re.search(r'version \"17([.]|\")', java_version)), java_version)
for name, ok, detail in checks:
    print(f"{'PASS' if ok else 'BLOCK'} | {name}{(' | '+detail) if detail else ''}")
passed=sum(ok for _,ok,_ in checks)
print(f"\nRESULT: {passed}/{len(checks)} PASS; {len(checks)-passed} BLOCK")
print('NOTE: PASS here means static prerequisite check only; it is not a Flutter build or Google Play validation.')
sys.exit(0 if all(ok for _,ok,_ in checks) else 2)
