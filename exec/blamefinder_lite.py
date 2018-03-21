#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import argparse
import subprocess
import re

class BlameFinder:
    def __init__(self, ghash, bhash, rpath, cpath):
        self.stat = True
        self.flag = True
        self.rebuild = False
        self.hashval = ghash
        self.badhashval = bhash
        self.repopath = rpath
        self.casepath = cpath
        self.execpath = "."
        self.tcmd = "make test"
        self.keep = False
        #self.keep = True
    def git_start(self):
        cmd0 = "git bisect start"
        cmd1 = "git bisect bad" + self.badhashval
        cmd2 = "git bisect good " + self.hashval
        print cmd0
        if subprocess.call(cmd0, shell = True, cwd = self.repopath) != 0:
            print "cmd failed"
            exit()
        print cmd1
        if subprocess.call(cmd1, shell = True, cwd = self.repopath) != 0:
            print "cmd failed"
            exit()
        print cmd2
        if subprocess.call(cmd2, shell = True, cwd = self.repopath) != 0:
            print "cmd failed"
            exit()



    def git_end(self):
        cmd = "git bisect reset"
        subprocess.call(cmd, shell = True, cwd = self.repopath)
        if self.rebuild:
            rbcmd = ""
            subprocess.call("rm CMakeCache.txt", shell = True, cwd = self.repopath + "/trunk/build")
            w = open('buildlog', 'w')
            p = subprocess.call(rbcmd, shell = True,stdout = w, stderr = w, cwd = self.repopath + "/trunk/build")
            w.close()
            #print p
            if p != 0:
                print " build failed"    
                exit()


    def git_bisect(self):
        cmd = "git bisect "+ self.stat
        p = subprocess.Popen(cmd, shell = True,stdout=subprocess.PIPE, cwd = self.repopath)
        p.wait()
        cmd_res = p.stdout.read()
        print cmd_res
        #print "return code:\n"
        #print p.returncode

        if p.returncode != 0:
            exit()
        if re.search('first bad commit', cmd_res) == None:
            self.flag = True
        else:
            self.flag = False

    def build_MC(self):
        w = open('buildlog', 'w')
        p = subprocess.call(rbcmd, shell = True,stdout = w, stderr = w, cwd = self.repopath + "/trunk/build")
        w.close()
        print p
        if p != 0:
            print " build failed"    
            exit()

    def testandcheck(self,n):
        if self.keep:
            tpath = self.execpath + "/test" + str(n)
        else:
            subprocess.call("rm -rf test", shell = True, cwd = self.execpath)
            tpath = self.execpath + "/test" 
        print tpath
        cpcmd = "cp -r " + self.casepath + " " + tpath 
        subprocess.call(cpcmd, shell = True)   
        p = subprocess.call(self.tcmd, shell = True, cwd = tpath)

        if os.path.exists(tpath+ "/err.log"):
            if os.path.getsize(tpath+ "/err.log"):
                print "test failed\n"
                self.stat = "bad"
            else:
                print "test passed\n"
                self.stat = "good"
        else:
            print "err.log dosen't exist, STOP!"
            print n
            exit()
 
    def run(self):
        self.git_start()
        n = 0
        while self.flag:
            n += 1
            print "Building merlin, it may take several minutes.\n  Message can be found in buildlog.\n"
            self.build_MC()
            self.testandcheck(n)
            self.git_bisect()
        self.git_end() 
	    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-bh', '--bhash' , type = str, default = "")
    parser.add_argument('-gh', '--ghash' , type = str, default = "")
    parser.add_argument('-cp', '--casepath' , type = str, default = "")
    parser.add_argument('-rp', '--repopath' , type = str, default = "")
    parser.add_argument('--keep', action = 'store_true', default = False)
    args = parser.parse_args()

    T = BlameFinder(args.ghash, args.bhash, args.repopath, args.casepath)
    T.run()

