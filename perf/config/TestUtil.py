#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2004 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import os, sys, pickle

for toplevel in [".", "..", "../..", "../../..", "../../../.."]:
    toplevel = os.path.normpath(toplevel)
    if os.path.exists(os.path.join(toplevel, "config", "TestUtil.py")):
        break
else:
    raise "can't find toplevel directory!"

def getAdapterReady(serverPipe):

    output = serverPipe.readline().strip()

    if not output:
        print "failed!"
        sys.exit(1)

def printOutputFromPipe(pipe):

    while 1:

        c = pipe.read(1)

        if c == "":
            break

        os.write(1, c)

class TestResults :

    def __init__(self, test):

        self.test = test
        self.results = { }
        self.names = [ ]
        self.products = [ ]
        self.reference = ""

    def add(self, product, name, result):

        if not product in self.products:
            self.products.append(product)

        if not name in self.names:
            self.names.append(name)

        if not self.results.has_key(name):
            self.results[name] = { }

        if not self.results[name].has_key(product):
            self.results[name][product] = [ ]
            
        self.results[name][product].append(result)

    def merge(self, result):

        for n in result.names:
            for p in result.products:
                for i in result.results[n][p]:
                    self.add(p, n, i)

    def addToResults(self, results, tests, names, products, id):

        if not self.test in tests:
            tests.append(self.test)

        if not results.has_key(self.test):
            results[self.test] = { } 

        for n in self.names:

            if not results[self.test].has_key(n):
                results[self.test][n] = { }
                    
            refbest = -1.0
            if not n in names:
                names.append(n)

            for p in self.products:

                if self.results[n].has_key(p):

                    if not results[self.test][n].has_key(p):
                        results[self.test][n][p] = { }

                    if not p in products:
                        products.append(p)

                    (mean, best) = self.calcMeanAndBest(self.results[n][p])

                    if refbest < 0.0:
                        refbest = best

                    results[self.test][n][p][id] = (best, best / refbest)

    def calcMeanAndBest(self, values):

            mean = 0.0
            best = max

            for r in values:
                mean += r
                if r < best:
                    best = r
            mean /= len(values)

            return (mean, best)
        
class HostResults :

    def __init__(self, hostname, outputFile):

        self.id = hostname + " " + sys.platform
        self.outputFile = outputFile
        self.tests = [ ]
        self.results = { }

    def add(self, product, test, name, result):

        if not self.results.has_key(test):
            self.results[test] = TestResults(test)

        if not test in self.tests:
            self.tests.append(test)

        self.results[test].add(product, name, result)

        f = file(self.outputFile, 'w')
        pickle.dump(self, f);
        f.close()

    def merge(self, results):

        for t in results.tests:

            if not t in self.tests:
                self.tests.append(t)

            if not self.results.has_key(t):
                self.results[t] = TestResults(t)

            self.results[t].merge(results.results[t])

    def addToResults(self, results, tests, names, products, hosts):

        if not self.id in hosts:
            hosts.append(self.id)

        for t in self.tests:
            self.results[t].addToResults(results, tests, names, products, self.id)
        
class AllResults :

    def __init__(self):
        self.results = { }

    def add(self, results):

        if self.results.has_key(results.id):
            self.results[results.id].merge(results)
        else:
            self.results[results.id] = results
            
    def printAll(self, csv):

        results = { }
        tests = [ ]
        names = [ ]
        hosts = [ ]
        products = [ ]
        for r in self.results.itervalues():
            r.addToResults(results, tests, names, products, hosts)

        if csv:
            self.printAllAsCsv(results, tests, names, hosts, products)
        else:
            self.printAllAsText(results, tests, names, hosts, products)

    def printAllAsCsv(self, results, tests, names, hosts, products):

        print "Product, Test, Configuration, ",
        for host in hosts:
            print host + ",",
        print ""

        for product in products:
            for test in tests:
                for name in names:
                    if results[test].has_key(name):
                        if results[test][name].has_key(product):
                            print product + "," + test + "," + name + ",",
                            for host in hosts:
                                if not results[test][name][product].has_key(host):
                                    print ",",
                                else:
                                    (m, r) = results[test][name][product][host]
                                    print  str(m) + ",",
                            print ""

    def printAllAsText(self, results, tests, names, hosts, products):

        for test in tests:
            print test + ": "
            sep = "==========================="
            print sep[0:len(test)]
            print ""
            
            print " %-15s" % "Test",
            for host in hosts:
                print "| %-18s" % host[0:18],
            print ""

            print " ---------------",
            for host in hosts:
                print "+-------------------",
            print ""
            
            for name in names:
                hasTest = False
                if results[test].has_key(name):
                    for product in products:
                        if results[test][name].has_key(product):
                            hasTest = True
                            print " %-15s" % (product + " " + name),
                            for host in hosts:
                                if not results[test][name][product].has_key(host):
                                    print "| %-18s" % "",
                                else:
                                    print "| %10.6f (%#1.3f)" % results[test][name][product][host],
                            print ""
                if hasTest:
                    print " ---------------",
                    for host in hosts:
                        print "+-------------------",
                    print ""
            
            print ""
        
class Test :

    def __init__(self, expr, results, i, product, test):
        self.expr = expr
        self.results = results
        self.iteration = i
        self.product = product
        self.test = test

    def run(self, name, directory, clientOpts, serverOpts):

        match = len(self.expr) == 0
        for e in self.expr:
            if e.match(self.product + " " + self.test + " " + name):
                match = True
                break;

        if not match:
            return

        cwd = os.getcwd()
        os.chdir(os.path.join(toplevel, "src", self.product, directory))

        print str(self.iteration) + ": " + self.product + " " + self.test + " " + name + "...",
        sys.stdout.flush()
    
        serverPipe = os.popen(os.path.join(".", "server") + " " + serverOpts)
        getAdapterReady(serverPipe)

        clientPipe = os.popen(os.path.join(".", "client") + " " + clientOpts)
        result = float(clientPipe.read())
        clientPipe.close()
        
        os.chdir(cwd)
        
        self.results.add(self.product, self.test, name, result)
    
        print result
    
