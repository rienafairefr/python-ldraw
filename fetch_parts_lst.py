#!/usr/bin/env python
from urllib import urlretrieve
import zipfile
import os


url = 'http://www.ldraw.org/library/updates/complete.zip'

retrieved = "complete.zip"

if not os.path.exists(retrieved):
    print('retrieve the complete.zip from ldraw.org ...')
    urlretrieve(url, filename=retrieved)

if not os.path.exists('tmp/ldraw'):
    print('unzipping the complete.zip ...')
    zip_ref = zipfile.ZipFile(retrieved, 'r')
    zip_ref.extractall('tmp')
    zip_ref.close()

if not os.path.exists('tmp/mklist/mklist'):
    print('unzipping the mklist  zip ...')
    zip_ref = zipfile.ZipFile('tmp/ldraw/mklist1_6.zip', 'r')
    zip_ref.extractall('tmp/mklist')
    zip_ref.close()

    print('patch the mklist  sources ...')
    patch = """diff -Naur mklist.orig/makefile mklist/makefile
--- mklist.orig/makefile	2018-02-23 10:05:40.000000000 +0100
+++ mklist/makefile	2018-02-23 10:05:47.111079214 +0100
@@ -1,6 +1,6 @@
 CC=gcc

-CFLAGS= -I./include
+CFLAGS= -I./include -D MAX_PATH=256

 AR = ar
 RANLIB = ranlib
diff -Naur mklist.orig/mklist.c mklist/mklist.c
--- mklist.orig/mklist.c	2018-02-23 10:05:06.000000000 +0100
+++ mklist/mklist.c	2018-02-23 10:05:12.602915933 +0100
@@ -84,7 +84,7 @@
 int GetShortPathName(char *longpath, char * shortpath, int psize)
 {
     strncpy(shortpath, longpath, psize);
-    return(strlen(shortpath);
+    return(strlen(shortpath));
 }
 #endif
"""
    open('tmp/mklist.patch', 'w').write(patch)

    os.system('dos2unix tmp/mklist/mklist.c')
    os.system('dos2unix tmp/mklist/makefile')
    os.system('patch -d tmp -l -p0 < tmp/mklist.patch')
    os.system('make -C tmp/mklist')

if not os.path.exists('tmp/ldraw/parts.lst'):
    print('mklist ...')
    os.system('tmp/mklist/mklist -d -i tmp/ldraw/parts -o tmp/ldraw/parts.lst')
